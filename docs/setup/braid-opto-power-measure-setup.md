# Braid Opto-Power Measure Setup

Maps how optical power is spread across the arena, for two reasons:

1. A general power/irradiance ("power per unit area") heatmap of the arena.
2. The intensity of the optogenetic (red LED) stimulus, both ON and OFF
   (baseline), at each position — using the same on/off pulse pattern real
   experiments use.

This is a QC (quality control) check, not part of the required calibration
pipeline in [Workflow](../workflow.md) — run it occasionally (e.g. after
moving LEDs, changing intensity, or if flies in one part of the arena seem
to respond differently than flies in another) rather than before every
experiment.

It works by tracking 4 IR LEDs with Braid (as 4 separate objects) while a
Thorlabs PM100D power meter is swept by hand through the arena, held at the
centroid of the 4 LEDs. Positions and power readings are recorded to two
separate files and lined up afterward by timestamp.

## Prerequisites

- **4 IR LEDs**, arranged in a known square, rigidly attached around the
  PM100D sensor head so their centroid tracks the sensor's position as you
  move it.
- **Thorlabs PM100D** power meter, connected via USB, switched to its
  **NI-VISA** mode (not "TLPM" mode) from the console's own front-panel
  menu — see [Environment Setup](environment.md#3-hardware-sdks) for why,
  and its note that this hasn't been verified on this project's machines
  yet.
- The project's **optogenetic light Arduino** (see [Opto
  Trigger](../repos/optofly/opto-trigger.md)), connected via USB. This tool
  expects it at the fixed device name `/dev/opto_trigger` — see [udev
  Rules](udev-rules.md) if that name doesn't exist yet on this machine.
- Braid already running and tracking — see [Workflow](../workflow.md) for
  the calibration steps that come before this.

## Install

```bash
cd ~/src/braid-opto-power-measure
uv sync
```

## One-time setup: a dedicated Braid config

This tool needs Braid configured to track up to 6 bright points per camera
(the 4 LEDs, plus headroom), instead of the single point most other configs
in this project track. Create it once, based on the existing laser config:

```bash
cp ~/braid-configs/laser.toml ~/braid-configs/power_meter.toml
sed -i 's/max_num_points = 1/max_num_points = 6/' ~/braid-configs/power_meter.toml
```

`sed -i` edits the file in place — `s/max_num_points = 1/max_num_points = 6/`
means "replace the first occurrence of `max_num_points = 1` with
`max_num_points = 6`."

> ⚠️ **Common failure:** `~/braid-configs/laser.toml` doesn't exist yet — this
> command silently produces an empty or missing `power_meter.toml` instead
> of an error you'd notice. Confirm `laser.toml` already exists first (it's
> created as part of [Braid Extrinsic
> Calibration](braid-extrinsic-calibration.md#optional-verify-tracking-with-a-laser));
> if it doesn't, do that step first.

## Configuration

Rig constants live in `config.toml` (checked into the repo), for example:

```toml
[braid]
url = "http://127.0.0.1:8397/"

[power_meter]
wavelength_nm = 625          # match the LED color you're measuring
sensor_diameter_mm = 9.5

[leds]
square_side_mm = 100.0        # distance between adjacent IR LEDs

[light]
enabled = true
port = "/dev/opto_trigger"
intensity = 128               # 0-255
on_duration_ms = 300
period_s = 10.0                # time between the start of successive pulses
```

Per-run settings (session name, duration, output location, dry-run
switches) are command-line flags instead — see below.

## Recording a session

Two equivalent ways to run it. Either way, sweep the power meter by hand
through the whole arena while it records — the more of the arena you cover,
the more complete the resulting heatmap.

### Option A: one combined command

```bash
./launch_power_meter.sh --session-name arena_sweep_1
```

Starts Braid with `power_meter.toml`, waits for it to come up, runs the
recorder in the foreground, and stops Braid again when you stop the
recorder.

### Option B: launch Braid yourself

```bash
# terminal 1
braid-run ~/braid-configs/power_meter.toml

# terminal 2
uv run record --session-name arena_sweep_1
```

Useful if you want to watch Braid's own web interface while recording, or
Braid is already running for another reason.

Stop recording any time with **Ctrl+C** — everything already written to
disk up to that point is kept.

Useful flags for both commands above:

| Flag | Default | Meaning |
|---|---|---|
| `--session-name` | *(required)* | Used in the output folder's name |
| `--duration` | run until Ctrl+C | Stop automatically after this many seconds |
| `--virtual` | off | Simulate the power meter — no real PM100D needed, for a dry run |
| `--no-light` | off | Skip light cycling — ambient-only sweep, no Arduino needed |

> ⚠️ **Common failure:** the recorder starts but every power reading is
> zero, or the LEDs aren't tracked. Confirm Braid's own web interface shows
> exactly 4 live tracked points before starting a real sweep — fewer means
> an LED is occluded or `power_meter.toml` doesn't have `max_num_points`
> raised (see "One-time setup" above).

## Analysis

```bash
uv run analyze sessions/<timestamp>_<session-name>
```

This lines up each recorded position with the closest power reading in
time, then writes up to two images into the session folder:

- `heatmap_light_on.png` — stimulus intensity map.
- `heatmap_light_off.png` — ambient/baseline map.

Check both images for evenness across the arena. A patchy or lopsided
`heatmap_light_on.png` usually means an LED, lens, or diffuser needs
adjusting — not a problem with this tool itself.

> ⚠️ **Common failure:** warnings printed about "no frame with exactly 4
> tracked objects" — this means an IR LED was blocked from camera view for
> the entire sweep, or Braid was tracking with the wrong config (see the
> LED-tracking check above). No heatmap is produced when this happens;
> re-run the sweep after fixing whichever LED dropped out.

## Full documentation

[Braid Opto-Power Measure README](../repos/braid-opto-power-measure/README.md) —
full CLI flag reference and output file formats (`braid_positions.csv`,
`power.csv`, `session_metadata.toml`).
