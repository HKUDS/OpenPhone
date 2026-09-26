"""Android app map data structures.

Port of phonecli/app_map.py adapted for Android UIAutomator XML format.
Macro actions use ADB commands instead of WDA HTTP calls:

  {"action": "launch", "package": "com.android.settings", "wait": 2.0}
  {"action": "tap", "x": 540, "y": 960, "wait": 1.0}
  {"action": "swipe", "x1": 540, "y1": 1500, "x2": 540, "y2": 500, "duration": 400, "wait": 0.5}
  {"action": "back", "wait": 0.5}
  {"action": "home", "wait": 0.5}
"""

import re
from dataclasses import dataclass, field
from typing import Optional

import yaml


@dataclass
class ScreenElement:
    text: str
    center: tuple[float, float]  # normalized [0, 1]
    leads_to: Optional[str] = None
    found_at_scroll: int = 0
    fixed: bool = False
    aliases: list[str] = field(default_factory=list)
    semantic_type: str = ""


@dataclass
class Screen:
    id: str
    elements: list[ScreenElement] = field(default_factory=list)
    description: str = ""
    scrollable: bool = False
    scroll_direction: str = ""  # "vertical" | "horizontal"


@dataclass
class Operation:
    id: str
    description: str
    macro: list[dict]
    type: str  # "NAV" or "ACT"
    target_screen: str = ""  # screen_id that this operation navigates to (NAV only)


class AppMap:
    """Loads and queries a YAML app map file for Android apps."""

    def __init__(self, map_path: str):
        try:
            with open(map_path, "r") as f:
                self.data = yaml.safe_load(f)
        except (FileNotFoundError, yaml.YAMLError) as e:
            raise ValueError(f"Failed to load app map '{map_path}': {e}") from e
        self.map_path = map_path
        self.app_name = self.data.get("app", "Unknown")
        self.package = self.data.get("package", "")
        self.screen_w = self.data.get("screen_w", 1080)
        self.screen_h = self.data.get("screen_h", 1920)

        self.launch_behavior = self.data.get("launch_behavior", "always_home")
        self.common_tasks: list[str] = self.data.get("common_tasks", [])
        self.known_limitations: list[str] = self.data.get("known_limitations", [])

        self.screens: list[Screen] = []
        for s in self.data.get("screens", []):
            elements = []
            for e in s.get("elements", []):
                elements.append(ScreenElement(
                    text=e["text"],
                    center=tuple(e["center"]),
                    leads_to=e.get("leads_to"),
                    found_at_scroll=e.get("found_at_scroll", 0),
                    fixed=e.get("fixed", False),
                    aliases=e.get("aliases", []),
                    semantic_type=e.get("semantic_type", ""),
                ))
            self.screens.append(Screen(
                id=s["id"],
                elements=elements,
                description=s.get("description", ""),
                scrollable=s.get("scrollable", False),
                scroll_direction=s.get("scroll_direction", ""),
            ))

        self._macros = self.data.get("screen_macros", {})

    def get_screen(self, screen_id: str) -> Optional[Screen]:
        for s in self.screens:
            if s.id == screen_id:
                return s
        return None

    def identify_current_screen(self, xml_str: str) -> tuple:
        """Identify which map screen best matches the given Android UIAutomator XML.

        Parses <node> elements with text, content-desc, or resource-id attributes.

        Returns (screen_id, confidence) where confidence is 0.0–1.0.
        Returns (None, 0) if no good match found.
        """
        xml_texts = set()

        # Match Android UIAutomator <node> elements and extract text-like attributes
        for match in re.finditer(r'<node\b([^>]*?)/>', xml_str):
            attrs = match.group(0)
            for attr in ["text", "content-desc"]:
                m = re.search(rf'{attr}="([^"]*)"', attrs)
                if m and m.group(1).strip():
                    text = m.group(1).strip()
                    if len(text) > 1:
                        xml_texts.add(text)

        # Also handle non-self-closing <node ...> (UIAutomator may use either format)
        for match in re.finditer(r'<node\b([^>]*?)>', xml_str):
            attrs = match.group(0)
            for attr in ["text", "content-desc"]:
                m = re.search(rf'{attr}="([^"]*)"', attrs)
                if m and m.group(1).strip():
                    text = m.group(1).strip()
                    if len(text) > 1:
                        xml_texts.add(text)

        if not xml_texts:
            return None, 0.0

        best_id, best_overlap, best_coverage = None, 0, 0.0
        for screen in self.screens:
            screen_texts = {e.text for e in screen.elements}
            if not screen_texts:
                continue
            overlap = len(xml_texts & screen_texts)
            coverage = overlap / len(screen_texts)
            if coverage >= 0.5 and overlap > best_overlap:
                best_overlap, best_id, best_coverage = overlap, screen.id, coverage

        if best_id is None:
            return None, best_coverage
        return best_id, best_coverage

    def find_relative_macro(self, from_id: str, to_id: str) -> list:
        """Return the relative action steps to go from from_screen to to_screen."""
        from_path = self._macros.get(from_id, [])
        to_path = self._macros.get(to_id, [])
        if not to_path:
            return []
        if not from_path:
            return list(to_path)

        i = 0
        while i < min(len(from_path), len(to_path)):
            if from_path[i] != to_path[i]:
                break
            i += 1
        return list(to_path[i:])

    def get_nav_targets(self, from_screen_id: str) -> list[str]:
        """Return navigation target names reachable from a given screen."""
        targets = []
        screen = self.get_screen(from_screen_id)
        if screen:
            for e in screen.elements:
                if e.leads_to:
                    label = e.text
                    if e.aliases:
                        label += f" ({e.aliases[0]})"
                    targets.append(label)
        return targets

    def build_operations(self) -> dict[str, Operation]:
        """Build operations catalog by traversing the screen graph from screen_0."""
        ops: dict[str, Operation] = {}
        visited_screens: set[str] = set()
        visited_ops: set[str] = set()

        def _skip(text: str) -> bool:
            t = text.lower()
            skips = [
                "profile picture", "navigate up", "more options",
                "dismiss", "clear", "learn more", "back", "cancel",
                "no unused", "no recent", "no nearby",
                "google account", "manage your google",
            ]
            return any(s in t for s in skips) or len(text.strip()) <= 1

        def _op_id(texts: list[str]) -> str:
            clean = "".join(c if c.isalnum() else "_" for c in "_".join(texts).lower())
            return clean.strip("_")[:60]

        def _explore(screen_id: str, prefix_texts: list[str], depth: int, max_depth: int = 6):
            if depth > max_depth or screen_id in visited_screens:
                return
            visited_screens.add(screen_id)
            screen = self.get_screen(screen_id)
            if not screen:
                return

            base_macro = list(self._macros.get(screen_id, []))
            for e in screen.elements:
                if _skip(e.text) or not e.text:
                    continue

                x = round(e.center[0] * self.screen_w)
                y = round(e.center[1] * self.screen_h)
                mid_x = self.screen_w // 2
                from_y = int(self.screen_h * 0.7)
                to_y = int(self.screen_h * 0.2)

                op_macro = list(base_macro)
                for _ in range(e.found_at_scroll):
                    op_macro.append({
                        "action": "swipe",
                        "x1": mid_x, "y1": from_y, "x2": mid_x, "y2": to_y,
                        "duration": 400, "wait": 0.5,
                    })
                op_macro.append({"action": "tap", "x": x, "y": y, "wait": 1.0})

                texts = prefix_texts + [e.text]
                op_id = _op_id(texts)
                if op_id in visited_ops:
                    continue
                visited_ops.add(op_id)

                op_type = "NAV" if e.leads_to else "ACT"
                desc = " → ".join(texts)
                ops[op_id] = Operation(
                    id=op_id, description=desc,
                    macro=op_macro, type=op_type,
                    target_screen=e.leads_to or "",
                )

                if e.leads_to:
                    _explore(e.leads_to, texts, depth + 1)

        _explore("screen_0", [], 0)
        return ops

    def get_target_screen_info(self, ops: dict[str, Operation], op_id: str) -> str:
        """Return the description of the screen an operation navigates to.

        Used by the macro agent's Phase 2 verification to help the LLM confirm
        whether a candidate operation actually leads to the right page.
        """
        op = ops.get(op_id) if ops else None
        if not op or not op.target_screen:
            return ""
        screen = self.get_screen(op.target_screen)
        if screen and getattr(screen, 'description', ''):
            return screen.description
        return ""

    def format_ops_catalog(self, ops: dict[str, Operation], nav_only: bool = False) -> str:
        """Format operations catalog as a compact tree with semantic tags.

        When nav_only=True, only NAV operations are included (skipping ACT
        leaf nodes). This produces a ~60% smaller catalog for LLM routing
        without losing screen-level navigation targets.
        """
        filtered = {k: v for k, v in ops.items() if not nav_only or v.type == "NAV"}
        if not filtered:
            return ""

        # Parse operations into a path tree: prefix → [(suffix, op)]
        tree = {}
        for op_id, op in filtered.items():
            parts = op.description.split(" → ")
            prefix = " → ".join(parts[:-1]) if len(parts) > 1 else ""
            suffix = parts[-1]
            tree.setdefault(prefix, []).append((suffix, op_id, op))

        lines = []
        nav_hint = " (NAV only)" if nav_only else ""
        lines.append(f"{self.app_name} ({self.package})"
                     f" — {len(filtered)} operations in {len(tree)} groups{nav_hint}")
        self._format_tree_level(tree, "", depth=0, lines=lines)
        return "\n".join(lines)

    def _format_tree_level(self, tree: dict, prefix: str, depth: int,
                           lines: list):
        """Format one level of the operation tree."""
        items = tree.get(prefix, [])
        if not items:
            return
        items.sort(key=lambda x: (x[2].type != "NAV", x[0].lower()))

        indent = "  " * depth
        for suffix, op_id, op in items:
            elem = self._find_element(suffix)
            tags = []
            if elem:
                type_tag = self._type_tag(elem)
                if type_tag:
                    tags.append(type_tag)
                if elem.aliases:
                    tags.append(elem.aliases[0])
            tag_str = f" [{'] ['.join(tags)}]" if tags else ""
            lines.append(f"{indent}{suffix}{tag_str}  # {op_id}")

            child_prefix = f"{prefix} → {suffix}" if prefix else suffix
            if child_prefix in tree:
                self._format_tree_level(tree, child_prefix, depth + 1, lines)

    def _find_element(self, text: str):
        """Find a ScreenElement by text across all screens."""
        for screen in self.screens:
            for e in screen.elements:
                if e.text == text:
                    return e
        return None

    def _type_tag(self, elem) -> str:
        """Map semantic_type to a concise tag for the LLM."""
        mapping = {
            "toggle": "TOGGLE", "switch": "TOGGLE",
            "input": "INPUT", "textfield": "INPUT",
            "slider": "SLIDER", "button": "BUTTON",
            "checkbox": "CHECKBOX", "label": "LABEL",
            "link": "LINK", "network": "NETWORK",
            "setting": "SETTING", "tab": "TAB",
            "menu_item": "MENU",
        }
        return mapping.get(elem.semantic_type, "")

    def format_nav_reference(self) -> str:
        """Generate a concise navigation reference for VLM consumption.

        Unlike format_ops_catalog (designed for text-LLM routing with op_ids),
        this produces a clean markdown-like reference listing top-level pages
        and their direct sub-pages. Suitable for appending to a VLM system prompt.

        Used by the "screen_cloud + map" fair-comparison baseline.
        """
        if not self.screens:
            return ""

        _noise = {"navigate up", "more options", "back", "cancel", "dismiss",
                  "clear", "learn more", "profile picture"}

        def _clean(text):
            return text.replace("&amp;", "&")

        def _is_noise(text):
            return text.lower() in _noise or len(text.strip()) <= 1

        # Build child index: screen_id -> list of (text, leads_to, semantic_type)
        children_of = {}
        for screen in self.screens:
            for e in screen.elements:
                if e.leads_to and not _is_noise(e.text):
                    children_of.setdefault(screen.id, []).append(
                        (e.text, e.leads_to, e.semantic_type))

        if "screen_0" not in children_of:
            return f"App: {self.app_name} ({self.package})"

        # Deduplicate root entries by target screen, keep the "best" label
        # (shortest non-noise text usually most descriptive)
        seen_targets = {}
        for text, child_id, stype in children_of["screen_0"]:
            if child_id in seen_targets:
                # Keep shorter label
                prev = seen_targets[child_id]
                if len(text) < len(prev[0]):
                    seen_targets[child_id] = (text, stype)
            else:
                seen_targets[child_id] = (text, stype)

        lines = [
            "## App Navigation Reference",
            f"This app (\"{self.app_name}\") has these top-level pages:",
            ""
        ]

        for child_id, (label, stype) in sorted(seen_targets.items(),
                                                key=lambda x: x[1][0].lower()):
            sub_items = children_of.get(child_id, [])
            sub_navs = [(t, s) for t, _, s in sub_items
                        if not _is_noise(t)]
            if len(sub_navs) > 8:
                # Too many to list — pick the most informative ones (non-label)
                sub_navs = [(t, s) for t, s in sub_navs if s not in ("label", "")]
                if len(sub_navs) > 8:
                    sub_navs = sub_navs[:8]

            tag = ""
            if stype == "input":
                tag = " [search]"
            elif stype in ("toggle", "switch"):
                tag = " [toggle]"
            lines.append(f"- {_clean(label)}{tag}")
            for sub_text, sub_stype in sub_navs:
                sub_tag = ""
                if sub_stype == "input":
                    sub_tag = " [text]"
                elif sub_stype in ("toggle", "switch"):
                    sub_tag = " [toggle]"
                lines.append(f"  - {_clean(sub_text)}{sub_tag}")

        return "\n".join(lines)

    def build_enriched_screen_hint(self, screen_id: str) -> str:
        """Build a rich VLM hint for a screen."""
        screen = self.get_screen(screen_id)
        if not screen:
            return ""

        parts = [f"You are on \"{screen_id}\""]
        if screen.description:
            parts[0] += f": {screen.description}"
        parts[0] += "."

        nav_targets = self.get_nav_targets(screen_id)
        if nav_targets:
            parts.append(f"Navigation targets: {', '.join(nav_targets)}")
        else:
            screen = self.get_screen(screen_id)
            if screen:
                refs = [e.text for e in screen.elements if e.fixed and e.text]
                if refs:
                    parts.append(f"Reference elements: {', '.join(refs[:8])}")

        if screen.scrollable:
            direction = screen.scroll_direction or "vertical"
            parts.append(f"This screen is {direction}-scrollable.")

        return " ".join(parts)
