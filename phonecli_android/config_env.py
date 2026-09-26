"""Config loading with ``${ENV_VAR}`` expansion.

Every agent config in this repository is secret-free: the OpenRouter key is
written as ``${OPENROUTER_API_KEY}`` and resolved from the environment when the
config is read.  Export the key before running anything:

    export OPENROUTER_API_KEY="sk-or-v1-..."

Unset variables expand to an empty string, which is the same behaviour as the
historical ``api_key: ""`` configs.
"""

import os
import re

import yaml

_ENV_RE = re.compile(r"\$\{([A-Za-z_][A-Za-z0-9_]*)\}")


def expand_env(value):
    """Recursively expand ``${VAR}`` placeholders in a parsed config object."""
    if isinstance(value, str):
        return _ENV_RE.sub(lambda m: os.environ.get(m.group(1), ""), value)
    if isinstance(value, dict):
        return {k: expand_env(v) for k, v in value.items()}
    if isinstance(value, list):
        return [expand_env(v) for v in value]
    return value


def load_config(path):
    """Read a YAML config file and expand ``${ENV_VAR}`` placeholders."""
    with open(path, "r", encoding="utf-8") as f:
        return expand_env(yaml.safe_load(f))
