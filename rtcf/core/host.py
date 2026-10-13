"""FilterHost — the capture -> plugin -> render loop.

Owns the frame queue and the render window. Plugins never touch the
capture device directly; they receive FramePackets and return them.
"""
from __future__ import annotations

import logging
import time

import cv2

from rtcf.core.contracts import FilterPlugin, FramePacket, PluginContext
from rtcf.services.capture_service import CaptureService
from rtcf.services.inference_pool import InferencePool
from rtcf.utils.frame_queue import LatestFrameQueue

log = logging.getLogger("rtcf.host")


class FilterHost:
    def __init__(self, config, capture: CaptureService, inference: InferencePool,
                 plugins: list[FilterPlugin]) -> None:
        self.config = config
        self.capture = capture
        self.inference = inference
        self.plugins = plugins
        self._active: FilterPlugin | None = None
        self._queue = LatestFrameQueue(maxsize=config.pipeline.queue_depth)

    def activate(self, name: str) -> None:
        match = next((p for p in self.plugins if p.manifest.name == name), None)
        if match is None:
            raise KeyError(f"plugin not loaded: {name}")
        settings = self.config.plugins.settings.get(name, {})
        match.setup(PluginContext(
            inference=self.inference,
            weights_dir=self.config.models.weights_dir,
            settings=dict(settings),
        ))
        self._active = match
        log.info("activated plugin %s v%s", match.manifest.name, match.manifest.version)

    def run(self, source: str) -> None:
        if self._active is None:
            raise RuntimeError("no plugin activated; call activate() first")
        self.capture.open(source)
        try:
            while True:
                packet = self.capture.read()
                if packet is None:
                    break
                t0 = time.perf_counter_ns()
                out = self._active.process(packet)
                latency_ms = (time.perf_counter_ns() - t0) / 1e6
                if self.config.render.overlay_stats:
                    cv2.putText(out.image, f"{latency_ms:.1f}ms", (12, 28),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                if self.config.render.preview:
                    cv2.imshow(self.config.render.window_title, out.image)
                    if cv2.waitKey(1) & 0xFF == ord("q"):
                        break
        finally:
            self.capture.close()
            cv2.destroyAllWindows()

    def selftest(self) -> bool:
        return bool(self.plugins) and self.capture.probe() and self.inference.healthy()