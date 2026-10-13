# Security Policy

## Scope

`realtime-camera-filter-ai` captures from local camera devices and processes
frames on-device. The host does **not** upload frames anywhere by default.
Any plugin that performs network I/O must declare it in its manifest:

```toml
[capabilities]
network = true
hosts = ["api.example.com"]
```

The loader refuses to enable a plugin whose declared capabilities exceed the
user's `config/permissions.yaml` allowlist.

## Reporting a vulnerability

Open a **private** security advisory on GitHub, or email
`security@realtime-camera-filter-ai.dev`. Include:

- Host version (`python -m rtcf.cli version`)
- Plugin name and version
- Repro steps and the captured frame if it's a processing bug

We aim to acknowledge within 72 hours.

## Threat model notes

- **Malicious plugin:** plugins run in-process. The loader sandboxes imports
  to the plugin folder, but a determined plugin can still touch the host. Only
  enable plugins you trust. A subprocess isolation mode is planned for v0.5.
- **Model weights:** shipped weights are hashed in `models/weights.sha256`.
  The loader verifies hashes before loading. Mismatched weights are refused.
- **Camera permissions:** the host requests camera access per-session and
  releases the device on exit. See `services/capture_service.py`.