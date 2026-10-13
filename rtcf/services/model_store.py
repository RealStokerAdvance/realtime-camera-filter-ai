"""ModelStore — resolves weight paths and reports availability per plugin."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class WeightInfo:
    name: str
    path: Path
    present: bool
    size_bytes: int


class ModelStore:
    def __init__(self, weights_dir: Path) -> None:
        self.weights_dir = weights_dir

    def resolve(self, name: str) -> WeightInfo:
        path = self.weights_dir / name
        present = path.exists()
        return WeightInfo(
            name=name, path=path, present=present,
            size_bytes=path.stat().st_size if present else 0,
        )

    def missing(self, names: list[str]) -> list[str]:
        return [n for n in names if not self.resolve(n).present]