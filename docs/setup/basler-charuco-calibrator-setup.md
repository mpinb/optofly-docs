# Basler ChArUco Calibrator Setup

Calibrates the intrinsics (focal length, lens distortion) of one Basler
tracking camera. Do this first, before any other calibration step — see
[Workflow](../workflow.md).

You'll need a printed ChArUco calibration board and the Basler Pylon SDK
installed (see [Environment Setup](environment.md)).

## Install

```bash
cd ~/src/basler-charuco-calibrator
uv sync
```

## Run

```bash
uv run python -m basler_charuco_calibrator
```

If more than one Basler camera is connected, you'll be asked to pick one.

Before you start, set up the arena lighting: turn on only the lights
mounted above the arena. The floor backlight isn't needed for this step —
see [Lighting during calibration](../workflow.md#lighting-during-calibration)
for why, and how to switch the backlight off if it's on.

Move the ChArUco board around in front of the camera. A live overlay shows
four coverage bars (horizontal position, vertical position, size, skew) —
once all four reach 70%, press `c` to calibrate, then `q` to quit. The
result is written as `Basler-<camera serial>.yaml`.

> ⚠️ **Common failure:** the app exits immediately with "Save directory does
> not exist" — the output folder (default `~/.config/strand-cam/camera_info`)
> must already exist; the app won't create it for you. Create it first:
> `mkdir -p ~/.config/strand-cam/camera_info`.

Repeat this entire process once per tracking camera in the rig.

## Full documentation

[Basler ChArUco Calibrator README](../repos/basler-charuco-calibrator/README.md) —
full flag reference, config file format, and output YAML schema.
