"""Macro agent — hybrid PhoneCLI-style agent for Android evaluation.

Architecture:
    Round 1: LLM task→operation mapping → ADB macro replay → optional VLM verify
    Round 2+: ScreenshotCloud-style VLM (CLOUD_V0 prompt + STATE_ASSESSMENT history)

Key design: Round 1 uses the app map for one-shot macro navigation. Round 2+
is pure VLM — no screen identification, no macro() calls. This avoids the
complexity of VLM trying to distinguish "navigate via macro" vs "interact with
UI elements", while still getting the benefit of deterministic Round 1 navigation.
"""

import os
import re
import tempfile
import time

from evaluation.app_map import AppMap, Operation
from evaluation.definition import get_code_snippet

from phonecli.prompts import MACRO_PLAN_PROMPT, MACRO_VERIFY_PROMPT, VLM_VERIFY_PROMPT
from phonecli.llm_client import text_completion, vision_completion
from templates.android_screenshot_template import SYSTEM_PROMPT_ANDROID_MLLM_CLOUD_V0


def _parse_llm_map_response(response: str) -> dict:
    """Parse the LLM task→operation mapping response."""
    response = response.strip()
    result = {"type": "need_vlm", "op_id": None, "reason": "", "answer": ""}

    for line in response.splitlines():
        # Strip markdown formatting and whitespace for robust matching.
        # Reasoning models (GLM, Kimi) often wrap tags like **MACRO_VLM:**
        clean = line.strip().lstrip("-*# \t")
        if not clean:
            continue
        upper = clean.upper()
        if upper.startswith("OP:"):
            return {"type": "op", "op_id": clean[3:].strip()}
        elif upper.startswith("MACRO_VLM:"):
            return {"type": "macro_vlm", "op_id": clean[10:].strip()}
        elif upper.startswith("NEED_VLM:"):
            return {"type": "need_vlm", "reason": clean[9:].strip()}
        elif upper.startswith("FINISH:"):
            return {"type": "finish", "answer": clean[7:].strip()}

    return result


class MacroAgentTask:
    """Hybrid agent: Round 1 macro routing + Round 2+ cloud VLM."""

    def __init__(self, instruction, controller, page_executor, agent, record,
                 command_per_step, app_map=None, llm_config=None, **kwargs):
        from evaluation.evaluation import ScreenshotReactTask as _FallbackTask
        self._parent = _FallbackTask(instruction, controller, page_executor,
                                     agent, record, command_per_step, **kwargs)
        self.instruction = instruction
        self.controller = controller
        self.page_executor = page_executor
        self.agent = agent
        self.record = record
        self.accessibility = self._parent.accessibility
        self.app_map = app_map
        self.llm_config = llm_config or {}
        self.force_macro_vlm = self.llm_config.get("force_macro_vlm", False)
        self.skip_landing_check = self.llm_config.get("skip_landing_check", False)
        self.landing_hint_level = self.llm_config.get("landing_hint_level", 2)
        self.cold_read_warmup = self.llm_config.get("cold_read_warmup", False)
        self._macro_phase_done = False
        self._ops_catalog = None
        self._fruitless_rounds = 0

        if self.app_map:
            try:
                self._ops_catalog = self.app_map.build_operations()
            except Exception:
                self._ops_catalog = {}

        # Cloud-style system prompt (pure role definition).
        # History accumulates STATE_ASSESSMENT strings via update_after_cot.
        self.system_prompt = [{"role": "system",
                               "content": SYSTEM_PROMPT_ANDROID_MLLM_CLOUD_V0}]
        self.record.history = []

    def _get_llm_client_kwargs(self):
        api_key = (self.llm_config.get("api_key")
                   or getattr(self.agent, 'api_key', None)
                   or "EMPTY")
        api_base = (self.llm_config.get("api_base")
                    or getattr(self.agent, 'api_base', None)
                    or "http://localhost:8002/v1")
        model = self.llm_config.get("model") or "Qwen/Qwen2.5-3B-Instruct"
        return {"api_key": api_key, "api_base": api_base, "model": model}

    # ------------------------------------------------------------------
    # Round 1: macro routing
    # ------------------------------------------------------------------

    def _llm_map_task(self) -> dict:
        if not self.app_map or not self._ops_catalog:
            return {"type": "need_vlm", "reason": "No app map loaded"}

        ops_catalog_str = self.app_map.format_ops_catalog(self._ops_catalog, nav_only=True)
        if not ops_catalog_str.strip():
            return {"type": "need_vlm", "reason": "No operations in catalog"}

        system_prompt = MACRO_PLAN_PROMPT.format(
            app_name=self.app_map.app_name,
            operations_catalog=ops_catalog_str,
            memory_context="",
        )
        user_prompt = f"Task: {self.instruction}"

        try:
            llm_kwargs = self._get_llm_client_kwargs()
            response = text_completion(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                **llm_kwargs,
                label="macro_map_task",
            )
        except Exception as e:
            print(f"[MacroAgent] LLM map-task failed: {e}")
            return {"type": "need_vlm", "reason": str(e)}

        result = _parse_llm_map_response(response)
        print(f"[MacroAgent] Phase 1 → {result['type']} {result.get('op_id', '')}")

        # Phase 2: verify candidate operation against target screen description.
        # Prevents navigating to a daily-summary page when the task asks about
        # a specific past date or item not shown there.
        if result["type"] in ("op", "macro_vlm") and result.get("op_id"):
            if not self._verify_operation(result):
                print("[MacroAgent] Phase 2 → REJECTED, falling back to VLM")
                return {"type": "need_vlm",
                        "reason": "Target page unmatched — fallback to VLM"}

        return result

    def _verify_operation(self, phase1_result: dict) -> bool:
        """Phase 2: confirm the selected operation navigates to a useful page."""
        op_id = phase1_result.get("op_id")
        if not op_id:
            return True

        op = self._ops_catalog.get(op_id)
        if not op:
            return True

        screen_desc = self.app_map.get_target_screen_info(
            self._ops_catalog, op_id)
        if not screen_desc:
            return True  # No description available — trust Phase 1

        verify_prompt = MACRO_VERIFY_PROMPT.format(
            task=self.instruction,
            op_description=op.description,
            screen_description=screen_desc,
        )

        try:
            llm_kwargs = self._get_llm_client_kwargs()
            response = text_completion(
                system_prompt=verify_prompt,
                user_prompt="YES / NO / UNCLEAR?",
                max_tokens=512,  # bumped for reasoning models (was 16→128→512)
                temperature=0.0,
                **{k: v for k, v in llm_kwargs.items()
                   if k not in ("system_prompt", "user_prompt", "max_tokens", "temperature")},
                label="macro_map_task",
            )
        except Exception as e:
            print(f"[MacroAgent] Phase 2 failed: {e}")
            return True  # On error, trust Phase 1

        verdict = response.strip().upper()
        print(f"[MacroAgent] Phase 2 screen='{screen_desc[:80]}...' → [{len(verdict)}] {verdict[:200]}")
        # Match YES/NO/UNCLEAR as standalone words anywhere in verbose output.
        # Reasoning models (GLM, Kimi) may wrap answers in markdown (**YES**, *YES*).
        if re.search(r'\bYES\b', verdict):
            return True
        if re.search(r'\bUNCLEAR\b', verdict):
            return True
        return False

    def _execute_macro(self, op: Operation) -> bool:
        if not op or not op.macro:
            return False

        print(f"[MacroAgent] Replaying macro: {op.id} ({len(op.macro)} steps)")
        for step in op.macro:
            action = step.get("action", "")
            try:
                if action == "force_stop":
                    self.controller.kill_package(step.get("package", ""))
                elif action == "launch":
                    self.controller.launch_app(step.get("package", ""))
                elif action == "tap":
                    self.controller.tap(step["x"], step["y"])
                elif action == "swipe":
                    dur = step.get("duration", 400)
                    self.controller.run_command(
                        f"adb -s {self.controller.device} shell input swipe "
                        f"{step['x1']} {step['y1']} "
                        f"{step['x2']} {step['y2']} {dur}"
                    )
                elif action == "back":
                    self.controller.back()
                elif action == "home":
                    self.controller.home()
                elif action == "wait":
                    time.sleep(step.get("seconds", 1.0))
            except Exception as e:
                print(f"[MacroAgent] Step failed: {step} — {e}")
                return False

            wait = step.get("wait", 0.5)
            if wait:
                time.sleep(wait)

        print(f"[MacroAgent] Macro replay complete")
        return True

    def _vlm_verify(self) -> bool:
        """VLM checks if task is complete after macro replay."""
        fd, screenshot_path = tempfile.mkstemp(suffix=".png", prefix="macro_verify_")
        os.close(fd)
        try:
            self.controller.save_screenshot(screenshot_path)
            if not os.path.exists(screenshot_path):
                return True

            llm_kwargs = self._get_llm_client_kwargs()
            response = vision_completion(
                system_prompt=VLM_VERIFY_PROMPT,
                user_text=f"Task: {self.instruction}\n\nIs this task complete?",
                image_paths=[screenshot_path],
                **llm_kwargs,
                label="macro_verify",
            )
            is_complete = "COMPLETE" in response.upper()
            print(f"[MacroAgent] VLM verify: {'COMPLETE' if is_complete else 'INCOMPLETE'}")
            return is_complete
        except Exception as e:
            print(f"[MacroAgent] VLM verify failed: {e}")
            return True
        finally:
            try:
                os.remove(screenshot_path)
            except OSError:
                pass

    # ------------------------------------------------------------------
    # Screen context detection (lightweight — for Round 1 macro landing)
    # ------------------------------------------------------------------

    def _detect_screen_context(self) -> str:
        """Identify current screen after macro replay, return a short hint.

        Uses the app map to match the current XML against known screens.
        Returns a description string (may be empty if identification fails).
        """
        if not self.app_map:
            return ""
        try:
            # Get XML path from the most recent record step
            if not self.record.contents:
                return ""
            last_step = self.record.contents[-1]
            xml_path = last_step.get("xml") if last_step.get("xml") != "ERROR" else None
            if not xml_path:
                xml_path = last_step.get("ac_xml")
            if not xml_path or not os.path.exists(xml_path):
                return ""

            with open(xml_path, "r") as f:
                xml_str = f.read()

            sid, confidence = self.app_map.identify_current_screen(xml_str)
            if sid and confidence >= 0.4:
                hint = self.app_map.build_enriched_screen_hint(sid)
                print(f"[MacroAgent] Post-macro screen: {sid} ({confidence:.0%})")
                return f"Current screen context: {hint}. "
        except Exception as e:
            print(f"[MacroAgent] Screen detection: {e}")
        return ""

    # ------------------------------------------------------------------
    # Landing verification
    # ------------------------------------------------------------------

    def _cold_read_screen(self) -> str:
        """One-shot VLM read of the current screen state after macro landing.

        Weak VLMs struggle to cold-read a page they were teleported to.
        This separates "read the screen" from "decide what to do": a
        dedicated call describes the visible state, and the description is
        injected into the main VLM's context.
        """
        fd, screenshot_path = tempfile.mkstemp(suffix=".png", prefix="coldread_")
        os.close(fd)
        try:
            self.controller.save_screenshot(screenshot_path)
            if not os.path.exists(screenshot_path):
                return ""

            llm_kwargs = self._get_llm_client_kwargs()
            response = vision_completion(
                system_prompt=(
                    "You are a screen reader. Describe the current mobile "
                    "screen state precisely: which page this is, which input "
                    "fields/toggles/sliders are visible, what values are "
                    "already set, and which element is currently focused. "
                    "Be concise (under 150 words)."
                ),
                user_text="Describe this screen state.",
                image_paths=[screenshot_path],
                **llm_kwargs,
                label="cold_read",
            )
            desc = (response or "").strip()
            if desc:
                print(f"[MacroAgent] Cold read: {desc[:120]}...")
            return desc
        except Exception as e:
            print(f"[MacroAgent] Cold read failed: {e}")
            return ""
        finally:
            try:
                os.remove(screenshot_path)
            except OSError:
                pass

    # ------------------------------------------------------------------
    # Landing mismatch check
    # ------------------------------------------------------------------

    def _landing_mismatch(self, op: Operation, screen_context: str) -> bool:
        """Check if the detected screen matches the macro operation's target.

        Returns True if the landing page is clearly wrong (screen detection
        found a page unrelated to the operation's navigation target).
        """
        if not screen_context:
            return False  # can't verify, trust the macro

        # Extract expected target text from the op description
        # e.g. "Network & internet → Airplane mode" → look for "Network", "Airplane"
        target_words = set()
        for part in op.description.split(" → "):
            for w in part.lower().split():
                if len(w) > 2:
                    target_words.add(w)

        if not target_words:
            return False

        context_lower = screen_context.lower()
        matches = sum(1 for w in target_words if w in context_lower)
        # If fewer than 2 target words appear in the detected screen context,
        # the macro likely landed on the wrong page
        mismatch = matches < min(2, len(target_words))
        if mismatch:
            print(f"[MacroAgent] Landing mismatch: expected {target_words}, "
                  f"got context '{screen_context[:100]}...'")
        return mismatch

    # ------------------------------------------------------------------
    # Round 2+: cloud-style VLM (same pattern as ScreenshotCloudTask)
    # ------------------------------------------------------------------

    def _round_vlm(self, round_count):
        """Cloud-style VLM step — no screen identification, no macro()."""
        self.record.update_before(
            controller=self.controller,
            need_screenshot=True,
            ac_status=self.accessibility,
            need_labeled=True,
        )

        try:
            image_path = self.record.labeled_current_screenshot_path

            # Build cloud-style user prompt with history injection
            history_text = ""
            if self.record.history:
                valid = [h for h in self.record.history if h is not None]
                if valid:
                    history_text = "\n".join(
                        f"  [{i}] {h}" for i, h in enumerate(valid, 1)
                    )

            prompt_text = (
                f"Task: {self.instruction}\n"
                f"History Information:\n{history_text}\n"
                f"Current Information: <image>"
            )

            current_message = self.agent.prompt_to_message_cloud(
                prompt_text, [image_path]
            )
            rsp = self.agent.act([*self.system_prompt, *current_message])

            # Extract STATE_ASSESSMENT for next round's history
            pattern = r'<STATE_ASSESSMENT>\s*(.*?)\s*</STATE_ASSESSMENT>'
            match = re.search(pattern, rsp, re.DOTALL)
            prompt_his = match.group(1) if match else None

        except Exception as e:
            import traceback
            traceback.print_exc()
            self.record.update_after_cot(
                {"action": "error", "error": str(e)},
                "",
                f"Error in round {round_count}: {e}",
                "",
            )
            self.record.turn_number += 1
            return

        # Detect fruitless rounds: if VLM is stuck scrolling/swiping,
        # inject a search hint after N consecutive rounds with no progress.
        called_fn = self._extract_called_function(rsp)
        if self._is_fruitless_action(called_fn):
            self._fruitless_rounds += 1
        else:
            self._fruitless_rounds = 0

        if self._fruitless_rounds >= 3 and prompt_his:
            if called_fn == "wait":
                hint = (
                    "[SYSTEM HINT: You have been waiting for several rounds. "
                    "If an ad or popup is blocking the screen, try tapping the "
                    "close button (×), pressing Back, or tapping outside the ad.]"
                )
            else:
                hint = (
                    "[SYSTEM HINT: After several scroll attempts without finding "
                    "the target, try using the search bar at the top of the screen "
                    "to search for the relevant setting directly.]"
                )
            prompt_his = f"{prompt_his} {hint}"
            print(f"[MacroAgent] Injected hint after "
                  f"{self._fruitless_rounds} fruitless rounds ({called_fn})")

        try:
            exe_res = self.page_executor(get_code_snippet(rsp))
        except Exception as e:
            import traceback
            traceback.print_exc()
            print(f"[MacroAgent] Action execution failed in round "
                  f"{round_count}: {e}")
            exe_res = {"action": "error", "error": str(e)}
            # Append hint so VLM can self-correct next round
            if prompt_his:
                prompt_his = (
                    f"{prompt_his} "
                    f"[SYSTEM HINT: The previous action failed with error: "
                    f"'{e}'. Choose a different element or approach.]"
                )

        self.record.update_after_cot(
            exe_res, rsp, prompt_his, get_code_snippet(rsp),
        )
        self.record.turn_number += 1

    @staticmethod
    def _extract_called_function(rsp: str) -> str:
        """Extract the function name from <CALLED_FUNCTION> block."""
        m = re.search(r'<CALLED_FUNCTION>\s*(\w+)', rsp)
        return m.group(1) if m else ""

    @staticmethod
    def _is_fruitless_action(fn_name: str) -> bool:
        """Check if the action suggests the VLM is stuck or searching."""
        return fn_name.lower() in ("swipe", "scroll", "wait")

    # ------------------------------------------------------------------
    # Dispatch
    # ------------------------------------------------------------------

    def run_step(self, round_count):
        if round_count == 1 and not self._macro_phase_done and self.app_map:
            return self._round_macro()

        if self.app_map and self._macro_phase_done:
            return self._round_vlm(round_count)

        self._parent.run_step(round_count)

    def _round_macro(self):
        """Round 1: LLM map-task → ADB macro replay → verify or VLM handoff."""
        print(f"[MacroAgent] Round 1 — Macro routing phase")

        map_result = self._llm_map_task()

        if map_result["type"] == "finish":
            print(f"[MacroAgent] Query answered: {map_result['answer']}")
            self.record.update_before(
                controller=self.controller,
                need_screenshot=True,
                ac_status=getattr(self, 'accessibility', False),
            )
            self.page_executor.finish(map_result["answer"])
            self.record.update_after_cot(
                {"action": "finish", "message": map_result["answer"]},
                f"FINISH: {map_result['answer']}",
                f"Task query answered: {map_result['answer']}",
                "finish()",
            )
            self._macro_phase_done = True
            return

        # Some models (e.g. GLM-5V) misclassify interactive tasks as OP.
        # When force_macro_vlm is set, downgrade OP → MACRO_VLM so the
        # VLM always gets a chance to interact after macro navigation.
        if self.force_macro_vlm and map_result["type"] == "op":
            map_result["type"] = "macro_vlm"

        if map_result["type"] in ("op", "macro_vlm"):
            op_id = map_result["op_id"]
            op = self._ops_catalog.get(op_id) if self._ops_catalog else None

            if op and self._execute_macro(op):
                # OP path: verify and finish if complete
                if map_result["type"] == "op" and self._vlm_verify():
                    self.record.update_before(
                        controller=self.controller,
                        need_screenshot=True,
                        ac_status=getattr(self, 'accessibility', False),
                    )
                    self.page_executor.finish("Macro completed task")
                    self.record.update_after_cot(
                        {"action": "finish", "message": "Macro completed"},
                        f"OP: {op_id}",
                        f"Macro operation {op_id} completed task.",
                        "finish()",
                    )
                    self._macro_phase_done = True
                    return

                # MACRO_VLM path: macro navigated, hand off to VLM
                print(f"[MacroAgent] Macro navigated, switching to VLM")
                self._macro_phase_done = True

                # Verify landing: if detected screen doesn't match expected target,
                # reset to VLM from clean state instead of misleading the VLM.
                # (skip_landing_check=True: ablation of the landing-mismatch guard)
                screen_context = ""
                if not self.skip_landing_check:
                    screen_context = self._detect_screen_context()
                    if self._landing_mismatch(op, screen_context):
                        print("[MacroAgent] Landing mismatch — resetting to VLM fallback")
                        if self.app_map:
                            try:
                                pkg = self.app_map.package
                                self.controller.kill_package(pkg)
                                time.sleep(0.3)
                                self.controller.launch_app(pkg)
                                time.sleep(2.0)
                            except Exception:
                                pass
                        self._round_vlm(1)
                        return

                # Build a rich landing hint so the VLM understands where it
                # arrived and what still needs to be done.  Cold-reading a UI
                # after a macro teleport is harder than walking in yourself;
                # this gives the VLM the context it would have built up during
                # manual navigation.
                # landing_hint_level: 2 = full (desc + elements + cold read),
                #                      0 = bare handoff (no page context)
                parts = [f"Macro completed: navigated to \"{op.description}\"."]
                parts.append(f"Task: {self.instruction}.")

                if self.landing_hint_level >= 1:
                    # Target screen description from the app map (static structure)
                    if not screen_context:
                        target_desc = self.app_map.get_target_screen_info(
                            self._ops_catalog, op_id)
                        if target_desc:
                            screen_context = f"Current screen: {target_desc}. "
                    if screen_context:
                        parts.append(screen_context.strip())

                if self.landing_hint_level >= 2:
                    # List interactive elements on the target screen so the VLM
                    # knows what to look for without visually exploring everything.
                    if op.target_screen:
                        screen = self.app_map.get_screen(op.target_screen)
                        if screen and screen.elements:
                            interactive = [
                                e for e in screen.elements
                                if e.semantic_type or e.leads_to
                            ]
                            if interactive:
                                elem_hints = []
                                for e in interactive[:8]:
                                    tag = e.semantic_type or "nav"
                                    elem_hints.append(f"{e.text}[{tag}]")
                                parts.append(
                                    f"Expected elements: {', '.join(elem_hints)}.")

                    # Cold-read warmup: one-shot VLM describes the live screen
                    # state so weak VLMs don't flounder on a teleported page.
                    if self.cold_read_warmup:
                        cold_desc = self._cold_read_screen()
                        if cold_desc:
                            parts.append(f"Current screen state: {cold_desc}")

                parts.append(
                    "Look at the current screen and complete the task step "
                    "by step.  The macro has only navigated here — you must "
                    "still perform any interactions (tap, type, swipe, etc.) "
                    "that the task requires."
                )

                state_assessment = " ".join(parts)

                self.record.update_before(
                    controller=self.controller,
                    need_screenshot=True,
                    ac_status=getattr(self, 'accessibility', False),
                )
                self.record.update_after_cot(
                    {"action": "macro", "op_id": op_id},
                    f"MACRO_VLM: {op_id}",
                    state_assessment,
                    f"macro_vlm({op_id})",
                )
                self.record.turn_number += 1
                return

        # No match or macro failed — fall back to pure VLM.
        # No macro was executed, so the app is already in its initial state
        # from task setup.  Killing + relaunching would waste time; just hand
        # control to the VLM.
        print(f"[MacroAgent] No matching macro, falling back to VLM")
        self._macro_phase_done = True
        self._round_vlm(1)
