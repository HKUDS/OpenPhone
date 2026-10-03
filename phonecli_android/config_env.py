"""Config loading with ``${ENV_VAR}`` expansion and ``~`` resolution.

Every agent config in this repository is secret-free and machine-independent:
API keys are written as ``${OPENROUTER_API_KEY}`` and paths as ``~/.android/avd``
or ``${ANDROID_SDK_PATH:-~/Library/Android/sdk}``.  Placeholders and the leading
``~`` are resolved when the config is read, so the same file works on any
machine.  Export the values you want to override before running anything:

    export OPENROUTER_API_KEY="sk-or-v1-..."
    export ANDROID_SDK_PATH="$HOME/Library/Android/sdk"

``${VAR}`` expands to an empty string when the variable is unset (the historical
``api_key: ""`` behaviour), while ``${VAR:-default}`` falls back to ``default``.
"""

import os
import re

import yaml

_ENV_RE = re.compile(r"\$\{([A-Za-z_][A-Za-z0-9_]*)(?::-([^}]*))?\}")


def _replace(match):
    value = os.environ.get(match.group(1))
    if value is None:
        value = match.group(2) if match.group(2) is not None else ""
    return value


def expand_env(value):
    """Recursively expand ``${VAR}``/``${VAR:-default}`` and a leading ``~``."""
    if isinstance(value, str):
        out = _ENV_RE.sub(_replace, value)
        if out.startswith("~/"):
            out = os.path.expanduser(out)
        return out
    if isinstance(value, dict):
        return {k: expand_env(v) for k, v in value.items()}
    if isinstance(value, list):
        return [expand_env(v) for v in value]
    return value


def load_config(path):
    """Read a YAML config file and expand ``${ENV_VAR}`` placeholders."""
    with open(path, "r", encoding="utf-8") as f:
        return expand_env(yaml.safe_load(f))
