"""CameraHandler — wraps a physical capture device as a FramePacket source."""
from __future__ import annotations

import time

import cv2
import numpy as np

from rtcf.core.contracts import FramePacket


class CameraHandler:
    def __init__(self, device_index: int, width: int, height: int, fps: int,
                 backend: str = "dshow", fourcc: str = "MJPG") -> None:
        self.device_index = device_index
        self.width = width
        self.height = height
        self.fps = fps
        self.backend = backend
        self.fourcc = fourcc
        self._cap: cv2.VideoCapture | None = None
        self._frame_id = 0

    def open(self) -> None:
        api = {"dshow": cv2.CAP_DSHOW, "msmf": cv2.CAP_MSMF,
               "v4l2": cv2.CAP_V4L2}.get(self.backend, cv2.CAP_ANY)
        self._cap = cv2.VideoCapture(self.device_index, api)
        self._cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        self._cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
        self._cap.set(cv2.CAP_PROP_FPS, self.fps)
        self._cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*self.fourcc))

    def read(self) -> FramePacket | None:
        if self._cap is None:
            return None
        ok, image = self._cap.read()
        if not ok or image is None:
            return None
        self._frame_id += 1
        return FramePacket(image=image, pts_ns=time.monotonic_ns(), frame_id=self._frame_id)

    def probe(self) -> bool:
        return self._cap is not None and self._cap.isOpened()

    def close(self) -> None:
        if self._cap is not None:
            self._cap.release()
            self._cap = None