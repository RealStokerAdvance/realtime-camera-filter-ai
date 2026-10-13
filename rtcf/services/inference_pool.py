"""InferencePool — thread pool + ONNX session cache for filter models.

Sessions are keyed by absolute weight path. `run()` is the only public
entry; it's thread-safe and reuses sessions across frames.
"""
from __future__ import annotations

import hashlib
import logging
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import numpy as np
import onnxruntime as ort

log = logging.getLogger("rtcf.inference")


class InferencePool:
    def __init__(self, size: int, weights_dir: Path, verify_hashes: bool = True) -> None:
        self.size = size
        self.weights_dir = weights_dir
        self.verify_hashes = verify_hashes
        self._pool = ThreadPoolExecutor(max_workers=size, thread_name_prefix="rtcf-inf")
        self._sessions: dict[str, ort.InferenceSession] = {}

    def _session(self, weights: Path) -> ort.InferenceSession:
        key = str(weights.resolve())
        if key not in self._sessions:
            if self.verify_hashes and not self._hash_ok(weights):
                raise RuntimeError(f"weight hash mismatch: {weights}")
            self._sessions[key] = ort.InferenceSession(
                key, providers=["CUDAExecutionProvider", "CPUExecutionProvider"]
            )
        return self._sessions[key]

    def _hash_ok(self, weights: Path) -> bool:
        manifest = self.weights_dir / "weights.sha256"
        if not manifest.exists():
            return True  # no manifest -> nothing to verify
        digest = hashlib.sha256(weights.read_bytes()).hexdigest()
        for line in manifest.read_text(encoding="utf-8").splitlines():
            if line.strip().endswith(weights.name):
                return line.split()[0] == digest
        return True

    def run(self, weights: Path, tensor: np.ndarray) -> np.ndarray:
        session = self._session(weights)
        name = session.get_inputs()[0].name
        return session.run(None, {name: tensor})[0]

    def healthy(self) -> bool:
        try:
            _ = ort.get_available_providers()
            return True
        except Exception:  # pragma: no cover - env-dependent
            return False

    def shutdown(self) -> None:
        self._pool.shutdown(wait=True)
        self._sessions.clear()