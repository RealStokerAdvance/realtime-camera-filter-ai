# Contributing to realtime-camera-filter-ai

Thanks for wanting to plug into the host. This repo is a **plugin host** for
real-time AI camera filters: a thin core host, a loader, a registry, and a
bunch of self-contained extension modules that each expose one filter
pipeline.

## Ground rules

1. **One plugin, one folder.** Every filter lives under `plugins/` and ships
   a `plugin.toml` manifest. No filter logic in the host.
2. **Contracts are frozen.** `core/contracts.py` defines the interfaces
   (`FilterPlugin`, `FramePacket`, `PluginManifest`). Breaking a contract is
   a major-version bump and a migration note in `docs/`.
3. **No blocking calls on the capture thread.** Inference and post-processing
   run on worker pools. See `services/inference_pool.py`.
4. **Respect the frame budget.** Target is 30 FPS at 720p on a mid-tier GPU.
   If your plugin can't hold the budget, mark it `tier = "offline"` in the
   manifest and it won't be offered in live mode.

## Dev setup

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python -m rtcf.cli list-plugins
python -m rtcf.cli run --plugin beauty_smooth --source 0
```

## Adding a plugin

```
plugins/
  my_filter/
    __init__.py
    plugin.toml
    pipeline.py
```

`pipeline.py` must export a class subclassing `FilterPlugin`. Register it by
adding the folder name to `config/plugins.yaml` under `enabled`.

## Style

- Python: `ruff` + `black`, line length 100.
- Native accel (C++/CUDA): put it in `native/`, expose via `pybind11`, keep the
  Python fallback working.
- C# / Java bridges are optional; see `bridges/` for the interop shims.

## PR checklist

- [ ] `pytest tests/` passes
- [ ] `python -m rtcf.cli selftest` passes
- [ ] Manifest validates against `models/plugin_manifest.py`
- [ ] Frame budget benchmarked (`tests/test_pipeline_budget.py`)