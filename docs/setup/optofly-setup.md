# OptoFly Setup

This is the main pipeline — what you run to actually record experiments.
Set this up last, after camera and lens calibration are done (see
[Workflow](../workflow.md)).

## Install

```bash
cd ~/src/optofly
uv sync
```

If it succeeds, you'll see no error output, ending with a line like
"Installed N packages".

## Configure

```bash
cp configs/config.example.toml configs/config.toml
cp configs/visual_stimuli.example.toml configs/visual_stimuli.toml
```

Edit `configs/config.toml` to point at your Braid server and calibration
files.

## Run

Make sure Braid is already running and recording before starting `optofly`:

```bash
uv run python main.py
```

Once it's actually running, you should see log output showing it's
connected to Braid and listening for tracking data.

> ⚠️ **Common failure:** `optofly` starts but no flies ever trigger
> anything — this almost always means Braid isn't tracking yet, or the
> trigger zone in `config.toml` doesn't overlap the arena. Check Braid's own
> web UI for live 3D tracks first.

## Full documentation

This setup page only covers the bare minimum to get `optofly` running.
For the complete calibration pipeline, architecture, and every subsystem
(camera, opto trigger, visual stimuli), see:

- [Getting Started](../repos/optofly/getting-started.md)
- [Calibration](../repos/optofly/calibration.md)
- [Architecture](../repos/optofly/architecture.md)
- [Troubleshooting](../repos/optofly/troubleshooting.md)
