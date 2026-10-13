"""Skin-smoothing filter: bilateral pass blended by strength, edge-aware."""
from __future__ import annotations

import cv2
import numpy as np

from rtcf.core.contracts import FramePacket, PluginContext, PluginManifest


class Plugin:
    manifest: PluginManifest

    def setup(self, ctx: PluginContext) -> None:
        self.strength = float(ctx.settings.get("strength", 0.6))
        self.preserve_edges = bool(ctx.settings.get("preserve_edges", True))

    def process(self, packet: FramePacket) -> FramePacket:
        img = packet.image
        smooth = cv2.bilateralFilter(img, d=9, sigmaColor=60, sigmaSpace=60)
        if self.preserve_edges:
            edges = cv2.Canny(img, 60, 140)[:, :, None]
            mask = (edges > 0).astype(np.float32)
            out = smooth * (1 - mask) + img * mask
        else:
            out = smooth
        packet.image = cv2.addWeighted(img, 1 - self.strength, out, self.strength, 0)
        return packet

    def teardown(self) -> None:
        pass