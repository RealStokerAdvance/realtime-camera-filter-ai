"""CaptureService — owns the active source handler and normalizes its API."""
from __future__ import annotations

from pathlib import Path

from rtcf.core.contracts import FramePacket
from rtcf.handlers.camera_handler import CameraHandler
from rtcf.handlers.file_handler import FileHandler


class CaptureService:
    def __init__(self, cfg) -> None:
        self.cfg = cfg
        self._handler: CameraHandler | FileHandler | None = None

    def open(self, source: str) -> None:
        if source.isdigit():
            self._handler = CameraHandler(
                device_index=int(source),
                width=self.cfg.width,
                height=self.cfg.height,
                fps=self.cfg.fps,
                backend=self.cfg.backend,
                fourcc=self.cfg.fourcc,
            )
        else:
            self._handler = FileHandler(Path(source))
        self._handler.open()

    def read(self) -> FramePacket | None:
        return self._handler.read() if self._handler else None

    def probe(self) -> bool:
        return self._handler is not None and getattr(self._handler, "probe", lambda: True)()

    def close(self) -> None:
        if self._handler is not None:
            self._handler.close()
            self._handler = None