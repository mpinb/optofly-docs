# Ximea Py Setup

`ximea-py` is a Python driver library, not a standalone tool — like
[`optotune-lens`](optotune-lens-setup.md), you don't run it directly as
part of normal rig setup. It wraps the XIMEA camera vendor SDK (`xiApi`)
so Python code can open a XIMEA camera, set exposure/gain, and pull image
frames. [`liquid-lens-calibration`](liquid-lens-calibration-setup.md) uses
it to read frames from the XIMEA focus camera during lens calibration.

You only need to set this up standalone if you're developing the driver
itself, or testing XIMEA camera communication directly in Python.

## Install (standalone)

```bash
cd ~/src/ximea-py
uv sync --group dev
```

This installs `pytest`, `ruff`, and `numpy` for development. The
`XIMEA Linux software package` (`libm3api.so.2`) must already be installed
system-wide — see [Environment Setup](environment.md).

## Run the test suite

```bash
uv run pytest
```

You should see all tests pass, ending in a line like `X passed in Y s`.

This repo builds a Python package named **`ximea`** (not `ximea-py` — that
name belongs to an unrelated, pre-existing package on PyPI). Both
`liquid-lens-calibration` and `optofly` depend directly on
`ximea @ git+https://github.com/mpinb/ximea-py.git`, so `uv sync` in either
repo always resolves this driver, not the PyPI package.

> ⚠️ **Common failure (older checkouts):** if lens calibration behaves as
> though this driver isn't installed at all, check `uv pip show ximea`
> inside `liquid-lens-calibration` — if it reports a stale version, or
> `uv pip show ximea-py` resolves to anything, pull the latest
> `pyproject.toml`/`uv.lock` from that repo and re-run `uv sync`.

## Full documentation

[Ximea Py README](../repos/ximea-py/README.md) — full usage examples,
sensor correction defaults, and frame buffer management notes.
