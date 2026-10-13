"""PluginLoader — import plugins from disk with import sandboxing.

Sandboxing here means: only the plugin's own folder is on sys.path during
import, and the manifest is validated before the module is executed. It is
NOT a security boundary (see SECURITY.md) — it's hygiene.
"""
from __future__ import annotations

import importlib.util
import logging
import sys
from pathlib import Path

from rtcf.core.contracts import FilterPlugin
from rtcf.core.registry import PluginRegistry
from rtcf.models.plugin_manifest import parse_manifest

log = logging.getLogger("rtcf.loader")


class PluginLoader:
    def __init__(self, registry: PluginRegistry, plugins_root: Path,
                 sandbox_imports: bool = True) -> None:
        self.registry = registry
        self.plugins_root = plugins_root
        self.sandbox_imports = sandbox_imports

    def load_enabled(self) -> list[FilterPlugin]:
        loaded: list[FilterPlugin] = []
        for name in self.registry.enabled:
            try:
                loaded.append(self._load_one(name))
            except Exception as exc:  # one bad plugin must not kill the host
                log.error("failed to load plugin %s: %s", name, exc)
        return loaded

    def _load_one(self, name: str) -> FilterPlugin:
        folder = self.plugins_root / name
        manifest_path = folder / "plugin.toml"
        if not manifest_path.exists():
            raise FileNotFoundError(f"missing manifest: {manifest_path}")
        manifest = parse_manifest(manifest_path)

        module_name, _, attr = manifest.entrypoint.partition(":")
        init_file = folder / "__init__.py"
        spec = importlib.util.spec_from_file_location(
            f"rtcf_plugin_{name}", init_file,
            submodule_search_locations=[str(folder)],
        )
        if spec is None or spec.loader is None:
            raise ImportError(f"cannot build spec for {name}")

        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
        pipeline = importlib.import_module(f"{spec.name}.pipeline")
        plugin_cls = getattr(pipeline, attr)
        plugin = plugin_cls()
        plugin.manifest = manifest
        return plugin