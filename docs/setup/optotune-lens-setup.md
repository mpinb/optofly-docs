# Optotune Lens Setup

`optotune-lens` is a Python driver library, not a standalone tool — you
don't run it directly as part of normal rig setup. It's installed
automatically as a dependency when you `uv sync` either
[`optofly`](optofly-setup.md) or
[`liquid-lens-calibration`](liquid-lens-calibration-setup.md), both of which
expect it cloned as a sibling directory (`../optotune-lens`) — see
[Environment Setup](environment.md).

You only need to set this up standalone if you're developing the driver
itself, or testing hardware communication directly.

## Install (standalone)

```bash
cd ~/src/optotune-lens
uv sync --extra dev
```

## Run the test suite

Tests use a mock serial implementation — no physical lens hardware needed:

```bash
uv run pytest
```

You should see all tests pass, ending in a line like `X passed in Y s`.

> ⚠️ **Common failure:** connecting to a real lens fails with a timeout —
> double check the serial port (`/dev/ttyUSB0` on Linux, `COMx` on Windows)
> and that no other program (including another Claude Code or Python
> session) already has that port open.

## Full documentation

[Optotune Lens README](../repos/optotune-lens/README.md) — full API
reference for both the `Lens` (Lens Driver 4) and `ICC1C` classes.
