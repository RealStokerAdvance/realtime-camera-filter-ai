"""FileHandler — replays a video file as a FramePacket source (offline mode)."""
from __future__ import annotations

import time
from pathlib import Path

import cv2

from rtcf.core.contracts import FramePacket


class FileHandler:
    def __init__(self, path: Path, loop: bool = False) -> None:
        self.path = path
        self.loop = loop
        self._cap: cv2.VideoCapture | None = None
        self._frame_id = 0

    def open(self) -> None:
        self._cap = cv2.VideoCapture(str(self.path))
        if not self._cap.isOpened():
            raise FileNotFoundError(f"cannot open video: {self.path}")

    def read(self) -> FramePacket | None:
        if self._cap is None:
            return None
        ok, image = self._cap.read()
        if not ok:
            if self.loop:
                self._cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                ok, image = self._cap.read()
            if not ok:
                return None
        self._frame_id += 1
        return FramePacket(image=image, pts_ns=time.monotonic_ns(), frame_id=self._frame_id)

    def close(self) -> None:
        if self._cap is not None:
            self._cap.release()
            self._cap = None