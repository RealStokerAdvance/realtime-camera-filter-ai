"""load_host_config — read YAML, validate against HostConfig, return typed."""
from __future__ import annotations

from pathlib import Path

import yaml

from rtcf.models.config_schema import HostConfig

_DEFAULT = Path("config/default.yaml")


def load_host_config(path: Path | None = None) -> HostConfig:
    target = path or _DEFAULT
    raw = yaml.safe_load(target.read_text(encoding="utf-8")) or {}
    return HostConfig.model_validate(raw)