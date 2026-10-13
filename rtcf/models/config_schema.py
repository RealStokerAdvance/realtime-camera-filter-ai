"""Typed config schema (pydantic v2) mirroring config/default.yaml."""
from __future__ import annotations

from pydantic import BaseModel, Field


class HostCfg(BaseModel):
    name: str
    version: str
    log_level: str = "info"


class CaptureCfg(BaseModel):
    backend: str = "dshow"
    device_index: int = 0
    width: int = 1280
    height: int = 720
    fps: int = 30
    fourcc: str = "MJPG"


class PipelineCfg(BaseModel):
    queue_depth: int = 4
    drop_policy: str = "latest"
    inference_pool_size: int = 2
    post_pool_size: int = 2


class RenderCfg(BaseModel):
    preview: bool = True
    window_title: str = "RTCF Preview"
    overlay_stats: bool = True


class ModelsCfg(BaseModel):
    weights_dir: str = "models/weights"
    verify_hashes: bool = True
    default_runtime: str = "onnxruntime"


class PluginsCfg(BaseModel):
    registry: str = "config/plugins.yaml"
    autoload: bool = True
    sandbox_imports: bool = True


class HostConfig(BaseModel):
    host: HostCfg
    capture: CaptureCfg = Field(default_factory=CaptureCfg)
    pipeline: PipelineCfg = Field(default_factory=PipelineCfg)
    render: RenderCfg = Field(default_factory=RenderCfg)
    models: ModelsCfg = Field(default_factory=ModelsCfg)
    plugins: PluginsCfg = Field(default_factory=PluginsCfg)