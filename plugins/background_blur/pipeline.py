"""Background blur: run segmentation, feather the mask, composite."""
from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np

from rtcf.core.contracts import FramePacket, PluginContext, PluginManifest


class Plugin:
    manifest: PluginManifest

    def setup(self, ctx: PluginContext) -> None:
        self.radius = int(ctx.settings.get("radius_px", 18))
        self.weights = Path(str(ctx.settings.get("segmentation_model")))
        self.inference = ctx.inference

    def process(self, packet: FramePacket) -> FramePacket:
        img = packet.image
        h, w = img.shape[:2]
        blob = cv2.resize(img, (256, 256)).astype(np.float32) / 255.0
        blob = blob.transpose(2, 0, 1)[None]
        mask = self.inference.run(self.weights, blob)[0, 0]
        mask = cv2.resize(mask,