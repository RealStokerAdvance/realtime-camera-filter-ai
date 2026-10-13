"""Typer CLI for the host. Thin — all logic lives in services/core."""
from __future__ import annotations

from pathlib import Path

import typer
from rich import print as rprint

from rtcf import __version__
from rtcf.bootstrap import build_host

app = typer.Typer(add_completion=False, help="realtime-camera-filter-ai host CLI")


@app.command()
def version() -> None:
    rprint(f"realtime-camera-filter-ai {__version__}")


@app.command("list-plugins")
def list_plugins() -> None:
    host = build_host()
    for p in host.plugins:
        rprint(f"[bold]{p.manifest.name}[/bold] v{p.manifest.version} — {p.manifest.description}")


@app.command()
def run(
    plugin: str = typer.Option(..., "--plugin", "-p", help="plugin folder name to activate"),
    source: str = typer.Option("0", "--source", "-s", help="camera index or file path"),
) -> None:
    host = build_host()
    host.activate(plugin)
    host.run(source=source)


@app.command()
def selftest() -> None:
    host = build_host()
    ok = host.selftest()
    rprint(f"selftest: {'PASS' if ok else 'FAIL'}")
    raise typer.Exit(code=0 if ok else 1)


if __name__ == "__main__":
    app()