"""LatestFrameQueue — bounded queue that drops to the newest frame.

Real-time capture must never block the producer on a slow consumer. When
full, `put` evicts the oldest frame and keeps the latest — the pipeline
always processes fresh frames, never a backlog.
"""
from __future__ import annotations

import threading
from collections import deque
from typing import Generic, TypeVar

T = TypeVar("T")


class LatestFrameQueue(Generic[T]):
    def __init__(self, maxsize: int = 4) -> None:
        self.maxsize = maxsize
        self._dq: deque[T] = deque()
        self._lock = threading.Lock()
        self._not_empty = threading.Condition(self._lock)

    def put(self, item: T) -> None:
        with self._not_empty:
            if len(self._dq) >= self.maxsize:
                self._dq.popleft()
            self._dq.append(item)
            self._not_empty.notify()

    def get(self, timeout: float | None = None) -> T | None:
        with self._not_empty:
            if not self._dq:
                self._not_empty.wait(timeout)
            return self._dq.popleft() if self._dq else None

    def __len__(self) -> int:
        with self._lock:
            return len(self._dq)