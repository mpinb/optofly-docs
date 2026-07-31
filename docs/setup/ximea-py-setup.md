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

> ⚠️ **Common failure:** package name collision. This repo builds a Python
> package named **`ximea`**, but
> [`liquid-lens-calibration`](https://github.com/mpinb/liquid-lens-calibration)'s
> `pyproject.toml` currently depends on a package named **`ximea-py`** with
> no `[tool.uv.sources]` override — unlike its `optotune-lens` dependency,
> which does pin to a local path. `ximea-py` also happens to be the name of
> an unrelated, pre-existing package on PyPI, so `uv sync` silently
> resolves that one instead of this repo. If lens calibration behaves as
> though this driver isn't installed at all, check
> `uv pip show ximea-py` inside `liquid-lens-calibration` — if it reports
> the PyPI package instead of this repo, that's the mismatch. This needs a
> fix in `liquid-lens-calibration` itself (e.g. a `[tool.uv.sources]` entry
> pointing at this repo, same pattern used for `optotune-lens`) —
> flagged here, not silently worked around.

## Full documentation

[Ximea Py README](../repos/ximea-py/README.md) — full usage examples,
sensor correction defaults, and frame buffer management notes.
