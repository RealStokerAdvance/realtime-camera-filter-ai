"""Bootstrap: wire config -> loader -> registry -> host, then hand off.

This is the only module that knows the full assembly order. Everything
downstream receives its dependencies via constructor injection so plugins
and services stay testable in isolation.
"""
from __future__ import annotations

import logging
from pathlib import Path

from rtcf.core.host import FilterHost
from rtcf.core.loader import PluginLoader
from rtcf.core.registry import PluginRegistry
from rtcf.services.capture_service import CaptureService
from rtcf.services.inference_pool import InferencePool
from rtcf.utils.config_loader import load_host_config
from rtcf.utils.logging_setup import configure_logging

log = logging.getLogger("rtcf.bootstrap")


def build_host(config_path: Path | None = None) -> FilterHost:
    cfg = load_host_config(config_path)
    configure_logging(cfg.host.log_level)

    registry = PluginRegistry.from_file(Path(cfg.plugins.registry))
    loader = PluginLoader(
        registry=registry,
        plugins_root=Path("plugins"),
        sandbox_imports=cfg.plugins.sandbox_imports,
    )

    capture = CaptureService(cfg.capture)
    inference = InferencePool(
        size=cfg.pipeline.inference_pool_size,
        weights_dir=Path(cfg.models.weights_dir),
        verify_hashes=cfg.models.verify_hashes,
    )

    plugins = loader.load_enabled() if cfg.plugins.autoload else []
    log.info("bootstrap complete: %d plugin(s) loaded", len(plugins))

    return FilterHost(config=cfg, capture=capture, inference=inference, plugins=plugins)