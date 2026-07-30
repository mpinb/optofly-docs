# Liquid Lens Calibration Setup

Builds the lookup table that tells the liquid lens which focus setting
("diopter") to use at a given distance. Do this after Braid's multi-camera
calibration is done and Braid is tracking live — see [Workflow](../workflow.md).

You'll need: the 6-camera Basler rig, a XIMEA CB160CG-LX-X8G3 camera, a
printed AprilTag (family `36h11`), and both the Basler Pylon SDK and XIMEA
xiAPI runtime installed (see [Environment Setup](environment.md)).

## Install

```bash
cd ~/src/liquid-lens-calibration
uv sync
```

This repo loads the `optotune-lens` driver library from `../optotune-lens`
(a sibling directory) — make sure that repo is cloned alongside this one
first, as covered in [Environment Setup](environment.md).

## Run

```bash
uv run lens-calibrate
```

1. Place an AprilTag somewhere in view of the Basler rig.
2. Press **Enter** in the preview window — it triangulates the tag, sweeps
   the lens, and records the best-focus diopter for that position.
3. Move the tag to a new distance, press **Enter** again. Repeat for
   ~10–15 positions.
4. Press **q** then **Enter** to quit — this fits the `z → diopter` curve
   and writes it to the location `optofly` reads from.

> ⚠️ **Common failure:** the tool errors out immediately on start, refusing
> to proceed — the default Braid calibration XML
> (`/home/nfc/braid-configs/calibration_charuco.xml`) doesn't exist yet.
> Finish Braid's own multi-camera calibration first, or pass the correct
> path with `--calibration`.

## Full documentation

[Liquid Lens Calibration README](../repos/liquid-lens-calibration/README.md) —
full CLI flag reference, the single-height vs. multi-height target modes,
and the output CSV format.
