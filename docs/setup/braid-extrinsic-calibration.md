# Braid Extrinsic Calibration

This is step 2 of the calibration pipeline (see [Workflow](../workflow.md)).
It works out where each tracking camera physically sits and points relative
to the others, so Braid can combine their 2D views into a single 3D
position for each tracked object. Braid does this itself, using AprilTags
(printed square markers with a unique ID pattern that a camera can detect
and identify) placed at known positions in the arena.

This step is controlled entirely through Braid's own web interface, so
there isn't much to configure here — but the order of operations matters,
and a few things fail silently if done out of order. This page walks
through the procedure end to end.

## Prerequisites

- Every tracking camera already has its **intrinsic** calibration done
  (step 1) — see [Basler ChArUco Calibrator
  Setup](basler-charuco-calibrator-setup.md). This produces a
  `Basler-<serial>.yaml` file per camera in
  `~/.config/strand-cam/camera_info/`; extrinsic calibration reads all of
  them, so a camera missing its file will be skipped or will make the
  calibration fail.
- Physical AprilTags, printed and ready to place in the arena.
- Arena lighting set up: overhead lights on, floor backlight doesn't matter
  either way — see [Lighting during
  calibration](../workflow.md#lighting-during-calibration).

## Step 1: place the tags

Before starting Braid, place each physical AprilTag in the arena at the
position listed in `~/braid-configs/apriltags_coordinates.csv`. Each row is
one tag:

```csv
id,x,y,z
0,0,-0.275,0.445
1,-0.275,0,0.445
...
```

- `id` — the AprilTag's printed ID number.
- `x`, `y`, `z` — that tag's position in meters, in the arena's coordinate
  frame.

Do this first. Everything below assumes the tags are already in place and
won't move again until calibration is finished.

> ⚠️ **Common failure:** a tag placed at the wrong coordinate, or a tag ID
> that doesn't match the CSV. The calibration has no way to catch this —
> it will quietly bundle-adjust using the wrong ground-truth position and
> produce a calibration that looks like it succeeded but is subtly wrong
> everywhere. Double-check tag IDs and positions against the CSV before
> moving on.

## Step 2: launch Braid

Double-click `~/apriltag_calibration/launch_calibration.sh`, or run it from
a terminal:

```bash
~/apriltag_calibration/launch_calibration.sh
```

Either way, it opens (or runs in) a terminal window attached to
`braid-run`. Leave that window open — you'll come back to it in Step 5 to
press Ctrl+C.

This script:

1. Deletes any leftover AprilTag detection files from a previous
   calibration session in `~/apriltag_calibration/`, so this run can't
   accidentally get mixed with stale data (see the common-failure note in
   Step 6).
2. Starts `braid-run ~/braid-configs/apriltag_calibration.toml` from inside
   `~/apriltag_calibration/`, so the detection files Braid writes land
   there directly instead of somewhere you have to go find afterward.

Leave this running for the rest of the procedure. Braid's web UI should now
be reachable the same way it is for a normal tracking session.

## Step 3: configure each camera

Do this once for **each** of the tracking cameras, one at a time, in
Braid's web UI:

1. Switch that camera from object detection to AprilTag detection mode.
   > **Note:** the exact control for this (dropdown, toggle, or checkbox)
   > depends on the version of Braid's web UI and hasn't been verified
   > against the live interface for this doc — check the per-camera panel
   > for a detection-mode selector and confirm the exact label the first
   > time you follow this page, then update this note.
2. Raise that camera's exposure until all — or nearly all — of the visible
   tags are reliably detected. Watch the live detection overlay; tags that
   flicker in and out of detection need more exposure.

Repeat for every camera before moving on. Skipping a camera here means it
won't contribute any detections to the calibration, and bundle adjustment
will silently proceed with one fewer camera instead of erroring.

> ⚠️ **Common failure:** exposure raised too far washes out the tag's
> black/white pattern and detection gets *worse*, not better. If a tag
> stops being detected as you increase exposure, back off rather than
> continuing to increase it.

## Step 4: run all cameras together

Once every camera has AprilTag detection on and is reliably detecting its
tags, leave all of them running simultaneously for **at least 30 seconds**.
This gives the bundle adjustment enough overlapping detections across
cameras to converge on a stable result.

## Step 5: stop

1. Disable AprilTag detection on each camera in the web UI first. This
   finalizes that camera's detection file.
2. Once every camera's detection is off, stop `braid-run` itself —
   Ctrl+C in the terminal from Step 2.

## Step 6: run the calibration

Double-click `~/apriltag_calibration/run_calibration.sh`, or run it from a
terminal:

```bash
cd ~/apriltag_calibration
./run_calibration.sh
```

This decompresses any compressed detection files, backs up the previous
`calibration_charuco.xml` (if one exists) to a timestamped `.bak` file, and
runs `braid-april-cal-cli` with bundle adjustment to produce the new
`~/braid-configs/calibration_charuco.xml`. See the `README.md` in
`~/apriltag_calibration/` on this machine for the full details of what the
script does.

The terminal stays open until you press a key, so you can read the output
before it closes.

> ⚠️ **Common failure:** stale detection files from an earlier attempt
> left in `~/apriltag_calibration/` before Step 2. `launch_calibration.sh`
> clears these automatically at the start of each session — but if you
> copy detection files into that directory by hand for any reason, `.
> /run_calibration.sh` has no way to tell old data from new, and will
> silently include it in the bundle adjustment. If a calibration looks
> wrong after a rerun, check the timestamps embedded in the
> `apriltags*.csv` filenames first.

## Confirm it worked

Once `run_calibration.sh` finishes successfully, confirm Braid is tracking
in 3D using the new calibration: open Braid's own web UI and look for live
3D tracks. This is also the check the next step in the pipeline (Liquid
Lens Calibration) assumes has already passed — see
[Workflow](../workflow.md).

### Optional: verify tracking with a laser

A laser pointer's bright dot is an easier, more controllable target than a
fly for sanity-checking that tracking looks right — you can move it
exactly where you want, whenever you want:

```bash
braid-run ~/braid-configs/laser.toml
```

This config uses `DetectLight` polarity (bright-object detection) instead
of the `DetectDark` polarity the fly-tracking configs
(`multi_fly.toml`/`single_fly.toml`) use. Turn off both the backlight and
the overhead arena lights first — same as for the laser-based FOV
calibration, see [Lighting during
calibration](../workflow.md#lighting-during-calibration) — otherwise
either light source can wash out or be mistaken for the laser dot.

Move the laser dot around the arena and watch Braid's web UI for a live 3D
track following it. If you want a plotted trajectory instead of just the
live view, record a short session, unzip the resulting `.braidz` file, and
load `kalman_estimates.csv.gz` with pandas to plot the tracked position
over time — see [Braid crashed while recording, leaving a `.braid` folder
behind](../troubleshooting.md#braid-crashed-while-recording-leaving-a-braid-folder-behind)
for what's inside a `.braidz` file.

> **Note:** exact `kalman_estimates.csv.gz` column names aren't verified
> here — check the CSV header once you have one before writing a plotting
> script against it.

Keep this trick in your back pocket beyond calibration, too: it's a
convenient way to check later that the optogenetic trigger or a
visual/light stimulus is actually firing — move the laser into the trigger
zone and confirm the expected response happens, without needing a live
fly.
