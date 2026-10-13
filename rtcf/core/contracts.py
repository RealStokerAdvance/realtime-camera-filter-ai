"""Frozen contracts shared by the host and every plugin.

Breaking any symbol here is a major-version bump. Plugins import from this
module only — never from `rtcf.core.host` or internal services.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol, runtime_checkable

import numpy as np


@dataclass(slots=True)
class FramePacket:
    """One captured frame plus the metadata the pipeline threads through.

    `image` is BGR uint8, shape (H, W, 3) — OpenCV convention. `pts_ns` is
    the monotonic capture timestamp; plugins must preserve it so latency
    stats stay honest.
    """

    image: np.ndarray
    pts_ns: int
    frame_id: int
    meta: dict[str, object] = field(default_factory=dict)


@dataclass(slots=True)
class PluginManifest:
    name: str
    version: str
    description: str
    tier: str = "live"          # live | offline
    entrypoint: str = "pipeline:Plugin"
    capabilities: dict[str, object] = field(default_factory=dict)


@runtime_checkable
class FilterPlugin(Protocol):
    """Every filter implements this. `setup` runs once; `process` per frame."""

    manifest: PluginManifest

    def setup(self, ctx: "PluginContext") -> None: ...
    def process(self, packet: FramePacket) -> FramePacket: ...
    def teardown(self) -> None: ...


@dataclass(slots=True)
class PluginContext:
    """Handed to plugins at setup. Read-only handles to shared services."""

    inference: object          # InferencePool
    weights_dir: str
    settings: dict[str, object] = field(default_factory=dict)