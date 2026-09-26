"""System prompts for text LLM and VLM operations."""

# ---------------------------------------------------------------------------
# Text LLM: task → macro operation mapping
# ---------------------------------------------------------------------------

MACRO_PLAN_PROMPT = """You are a mobile task planner. Map the task to an operation from the catalog below.

## Operations Catalog (tree format)
Indented hierarchy: each level represents nested navigation.
Tags: [TOGGLE]=switch, [INPUT]=text field, [SLIDER]=adjustable, [▶]=expands to sub-screen.
Each line ends with an operation ID after #.

{operations_catalog}

{memory_context}
## Output (ONE line only)
OP: <operation_id>       — navigating to this screen alone completes the task
MACRO_VLM: <operation_id> — macro navigates there, then VLM must interact (toggle/type/slide/verify)
NEED_VLM: <reason>       — no matching operation
FINISH: <answer>         — query answerable without any action

## Rules
- Use the operation_id from the # comment at end of each line.
- OP: use ONLY when just viewing the target page IS the task. Example: "Open settings" → OP.
- MACRO_VLM: use when ANY interaction is needed beyond viewing: toggling a switch, typing text, adjusting a slider, selecting an option, or verifying visual state. Tags [TOGGLE]/[INPUT]/[SLIDER] are strong hints to use MACRO_VLM.
- [▶] elements are navigation-only (can't complete tasks). Choose MACRO_VLM with the target sub-screen's operation_id.
- When in doubt, choose MACRO_VLM.
- NEED_VLM: no matching operation in catalog.
- FINISH: query with known answer.
- If the task asks about specific data (a past date, a named item, a filtered result) and no operation explicitly targets that data, prefer NEED_VLM — navigating to a generic overview page forces VLM to backtrack.
"""

# ---------------------------------------------------------------------------
# Phase 2: verify whether the selected operation's target screen matches the task
# ---------------------------------------------------------------------------

MACRO_VERIFY_PROMPT = """You are verifying whether a candidate navigation operation leads to a page that can help complete a mobile task.

Task: {task}
Selected operation: {op_description}
Target page description: {screen_description}

Does this target page help complete the task? Answer with one word:
YES — this page directly helps (e.g., transactions list for finding a transaction)
NO — this page won't help (e.g., today-only summary for a past-date query)
UNCLEAR — not sure, proceed with the navigation anyway"""

# ---------------------------------------------------------------------------
# VLM: coordinate-based action from screenshot
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# VLM: verification — check if task is complete
# ---------------------------------------------------------------------------

VLM_VERIFY_PROMPT = """You are a mobile task verifier. Look at the screenshot and determine if the task is complete.

Task: {task}

Output exactly one line:
COMPLETE: <brief confirmation of what was done>
or
INCOMPLETE: <what still needs to be done>"""

# ---------------------------------------------------------------------------
# Text LLM: XML text verification
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# Text LLM: element stability classification for app map crawling
# ---------------------------------------------------------------------------

ELEMENT_CLASSIFY_PROMPT = """You are a mobile UI element classifier for an app named "{app_name}". Classify each element as STABLE or DYNAMIC.

STABLE: Fixed UI chrome — navigation tabs, menu buttons, search bars, filter/publish/profile icons, bottom tab bar items, back/close buttons, settings gears, category selectors, shopping cart icons, hamburger menus. These appear the same every time the app opens.

DYNAMIC: Variable content — post titles, usernames, follower counts, timestamps, video descriptions, comment text, personalized recommendations, trending topics, news headlines, ad banners, message previews, notification text. These change between sessions.

Output one line per element in exactly this format (no quotes, no JSON):
STABLE|element text
DYNAMIC|element text

Example:
STABLE|Following
DYNAMIC|我在X上也是有1.1万人看过了
STABLE|Home
STABLE|Search

Output ONLY the classification lines, nothing else."""

# ---------------------------------------------------------------------------
# Enrichment: generate aliases and semantic types for elements
# ---------------------------------------------------------------------------

ELEMENT_ENRICH_PROMPT = """You are a mobile UI analyst enriching an app map for the app "{app_name}".
For each element below, output exactly one JSON object per line with:

  {{
    "text": "<original text>",
    "aliases": ["<synonym1>", "<synonym2>", ...],
    "semantic_type": "<toggle|button|tab|input|label|link|network|setting|menu_item|other>"
  }}

Rules:
- aliases: common synonyms, alternate names, Chinese↔English equivalents, abbreviation expansions.
  Examples: "Wi-Fi" → ["WiFi", "wireless", "无线", "wifi network"]
           "Bluetooth" → ["BT", "蓝牙", "bluetooth settings"]
- semantic_type: what kind of UI element this is.
  - toggle: a switch/checkbox (tap changes state)
  - button: an action button
  - tab: bottom/side navigation tab
  - input: text field for typing
  - label: display-only text
  - link: navigates to another screen
  - network: a Wi-Fi network name in a list
  - setting: a settings category item
  - menu_item: an item in a menu/list that leads to a sub-screen
- Keep aliases concise (1-5 items each).
- Output ONE JSON object per line, no extra text.

Elements:
{element_list}"""

# ---------------------------------------------------------------------------
# Enrichment: generate screen descriptions
# ---------------------------------------------------------------------------

SCREEN_ENRICH_PROMPT = """You are a mobile UI analyst describing screens in the "{app_name}" app.
For the screen below, output a JSON object:

  {{
    "description": "<one-sentence summary of what this screen is and what user can do here>",
    "scrollable": true/false,
    "scroll_direction": "vertical" | "horizontal" | ""
  }}

Rules:
- description: concise (one sentence), describe purpose and key content.
  Examples: "Wi-Fi settings page with on/off toggle and available networks list"
           "Bottom navigation bar with 4 tabs: Home, Explore, Messages, Profile"
- scrollable: true if this screen likely has scrollable content beyond what's listed.

Screen ID: {screen_id}
Elements:
{element_list}

Output ONLY the JSON object, nothing else."""

# ---------------------------------------------------------------------------
# Enrichment: generate app-level metadata
# ---------------------------------------------------------------------------

APP_ENRICH_PROMPT = """You are a mobile app analyst describing the "{app_name}" app.
Based on the screen list and element summary below, output a JSON object:

  {{
    "launch_behavior": "always_home" | "resume_last",
    "common_tasks": ["<task1>", "<task2>", ...],
    "known_limitations": ["<limitation1>", ...]
  }}

Rules:
- launch_behavior: "always_home" if the app always opens to the main screen;
  "resume_last" if it resumes where left off.
- common_tasks: 5-10 most common user tasks this app supports, in natural language.
  Examples: ["Turn on/off Wi-Fi", "Toggle Bluetooth", "Check battery percentage"]
- known_limitations: any known quirks that might affect navigation
  (e.g. "Some settings require scrolling to find", "Search bar is hidden behind a gesture").

Screens summary:
{screen_summary}

Output ONLY the JSON object, nothing else."""

# ---------------------------------------------------------------------------
# Memory: context template for macro planning
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# Memory: extract user insights from completed task
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# Memory: query profile for cached answer
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# Profile generation: analyze screen_0 elements and produce app-specific rules
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# Sanitization: classify personal data candidates via LLM
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# Text LLM: task decomposition for multi-app workflows
# ---------------------------------------------------------------------------
