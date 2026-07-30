# OptoFly Project Wiki

This is the documentation hub for the **OptoFly** project: a real-time
tracking and closed-loop optogenetic stimulation system for flying insects,
plus the calibration tools it depends on.

If you're setting up a new rig or working on this project for the first
time, start here:

1. Read [Overview](overview.md) to understand what the pieces are and how
   they fit together.
2. Follow [Setup → Environment](setup/environment.md), then the setup page
   for each tool in the order listed there.
3. Read [Workflow](workflow.md) for the full calibration-to-experiment
   pipeline, in order.

If something isn't working, check [Troubleshooting](troubleshooting.md) first.

## The repos

| Repo | What it does |
|---|---|
| [`optofly`](https://github.com/mpinb/optofly) | The main pipeline: real-time fly tracking, triggered recording, optogenetic stimulation, autofocus, visual stimuli |
| [`basler-charuco-calibrator`](https://github.com/mpinb/basler-charuco-calibrator) | One-time camera intrinsic calibration for each Basler tracking camera |
| [`liquid-lens-calibration`](https://github.com/mpinb/liquid-lens-calibration) | Builds the lookup table the liquid lens uses to autofocus at a given distance |
| [`optotune-lens`](https://github.com/mpinb/optotune-lens) | The low-level driver library both `optofly` and `liquid-lens-calibration` use to talk to the liquid lens hardware |

Full docs for each are under [Component Docs](repos/optofly/getting-started.md)
in the sidebar — this wiki pulls them in automatically so they're always
up to date with each repo's own `main` branch.
