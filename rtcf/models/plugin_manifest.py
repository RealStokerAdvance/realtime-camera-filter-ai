"""parse_manifest — validate a plugin.toml into a PluginManifest."""
from __future__ import annotations

import sys
from pathlib import Path

if sys.version_info >= (3, 11):
    import tomllib
else:  # pragma: no cover
    import tomli as tomllib

from rtcf.core.contracts import PluginManifest

_REQUIRED = ("name", "version", "description")


def parse_manifest(path: Path) -> PluginManifest:
    raw = tomllib.loads(path.read_text(encoding="utf-8"))
    plugin = raw.get("plugin", {})
    missing = [k for k in _REQUIRED if k not in plugin]
    if missing:
        raise ValueError(f"{path}: missing required keys {missing}")
    return PluginManifest(
        name=plugin["name"],
        version=plugin["version"],
        description=plugin["description"],
        tier=plugin.get("tier", "live"),
        entrypoint=plugin.get("entrypoint", "pipeline:Plugin"),
        capabilities=dict(raw.get("capabilities", {})),
    )