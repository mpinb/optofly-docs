# Troubleshooting

This page covers issues that span repos. For issues inside `optofly`
itself once it's running, see
[OptoFly's own Troubleshooting doc](repos/optofly/troubleshooting.md).

## `git clone` fails or points at the wrong place

All 5 repos moved to the `mpinb` GitHub organization. If you have an old
clone that still points at a personal account, check and fix it:

```bash
cd ~/src/<repo>
git remote -v
git remote set-url origin git@github.com:mpinb/<repo-name>.git
```

## "No module named optotune_lens" (or similar) when running `optofly` or `liquid-lens-calibration`

Both repos load `optotune-lens` from `../optotune-lens` — a sibling
directory, not a package installed from PyPI.

> ⚠️ **Common failure:** cloning `optotune-lens` into a different parent
> folder than the repo that needs it — silently breaks the local path
> dependency instead of raising a clear error at `uv sync` time in some
> cases. Confirm the layout matches
> [Environment Setup](setup/environment.md): all repos as siblings under
> the same parent directory (e.g. `~/src/`).

## Basler or XIMEA camera not detected

Both `basler-charuco-calibrator` and `liquid-lens-calibration` need vendor
SDKs installed **system-wide**, separately from anything `uv sync`
installs: the Basler Pylon SDK, and (for `liquid-lens-calibration` only)
the XIMEA xiAPI runtime. `uv sync` succeeding does not mean these are
installed — they're OS-level installs, not Python packages. See
[Environment Setup](setup/environment.md).

## `liquid-lens-calibration` used to silently install the wrong `ximea` package

`liquid-lens-calibration` previously depended on a package named
`ximea-py`, which is also the name of an unrelated, pre-existing package on
PyPI. `uv sync` silently installed that unrelated PyPI package instead of
[this org's driver](setup/ximea-py-setup.md), which builds a package named
**`ximea`** (not `ximea-py`). Both `liquid-lens-calibration` and `optofly`
now depend directly on `ximea @ git+https://github.com/mpinb/ximea-py.git`,
so this collision no longer happens.

> ⚠️ **Common failure (older checkouts):** camera calls fail or behave
> unexpectedly in `liquid-lens-calibration` despite `uv sync` succeeding —
> run `uv pip show ximea` inside that repo; if it reports a version that
> doesn't match [`mpinb/ximea-py`](https://github.com/mpinb/ximea-py)'s
> latest release, or `uv pip show ximea-py` still resolves to something,
> pull the latest `pyproject.toml`/`uv.lock` from this repo and re-run
> `uv sync`.

## Calibration board or laser dot isn't detected cleanly

Usually a lighting problem, not a hardware fault — see
[Lighting during calibration](workflow.md#lighting-during-calibration) for
the correct light setup per step, and how to switch the backlight on/off
from the Arduino IDE or a Python REPL. If the laser's bright spot still
isn't detected with both the backlight and overhead lights off, see the
`calibrate_braid_ximea` troubleshooting notes in
[`optofly`'s Calibration doc](repos/optofly/calibration.md).

## A calibration step gives obviously wrong numbers

Each calibration step in [Workflow](workflow.md) depends on the one before
it. Wrong results in a later step are often caused by a stale or wrong
file from an earlier one (an old camera intrinsics YAML, an outdated Braid
calibration XML). Re-run from the earliest step you're unsure about,
rather than assuming the current step's tool is at fault.
