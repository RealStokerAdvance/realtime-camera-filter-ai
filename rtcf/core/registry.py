"""PluginRegistry — reads config/plugins.yaml into an enabled/disabled set."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import yaml


@dataclass(slots=True)
class PluginRegistry:
    enabled: list[str] = field(default_factory=list)
    disabled: list[str] = field(default_factory=list)
    settings: dict[str, dict] = field(default_factory=dict)

    @classmethod
    def from_file(cls, path: Path) -> "PluginRegistry":
        raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        return cls(
            enabled=list(raw.get("enabled", [])),
            disabled=list(raw.get("disabled", [])),
            settings=dict(raw.get("settings", {})),
        )

    def is_enabled(self, name: str) -> bool:
        return name in self.enabled