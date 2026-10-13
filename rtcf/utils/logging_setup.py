"""configure_logging — rich-backed logger with a plain fallback."""
from __future__ import annotations

import logging

from rich.logging import RichHandler


def configure_logging(level: str = "info") -> None:
    logging.basicConfig(
        level=level.upper(),
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(rich_tracebacks=True, show_path=False)],
        force=True,
    )