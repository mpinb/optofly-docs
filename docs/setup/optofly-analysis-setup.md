# OptoFly Analysis Setup

Analyzes finished recordings (`.braidz` files, produced by `optofly` — see
[Getting Started](../repos/optofly/getting-started.md)) to answer two
questions, without writing any code:

1. **Did the flies behave normally?** — velocity and saccade (fast-turn)
   statistics.
2. **Did they respond to the stimulus** (a looming visual threat, or an
   optogenetic light activation), **and how?** — percent responsive, turn
   direction, turn size — broken down by whatever condition varied (stimulus
   angle, light intensity, and so on).

It can also compare groups of recordings side by side (for example, control
flies vs. a mutant line).

This is a post-hoc analysis tool — run it after an experiment finishes, on
the `.braidz` file(s) it produced. It's not part of the calibration sequence
in [Workflow](../workflow.md) and doesn't need any hardware.

## Prerequisites

- One or more finished `.braidz` recording files (from `optofly`, or
  recovered from a crash — see [Braid crashed while recording, leaving a
  `.braid` folder
  behind](../troubleshooting.md#braid-crashed-while-recording-leaving-a-braid-folder-behind)).
- `uv` installed — see [Environment Setup](environment.md#1-install-uv).
  You do **not** need Python installed separately, and you do not need to
  `pip install` anything.

## Install

```bash
cd ~/src/optofly-analysis
uv sync
```

This installs the project's own code (`optofly_analysis/`) into its virtual
environment, which is what makes the `optofly-analyze` command below
available via `uv run`.

## Running an analysis

```bash
uv run optofly-analyze /path/to/your_recording.braidz -o results/
```

When it finishes, open the newest folder inside `results/` — it's named
after the date and time of the run (e.g. `results/20260805_143022/`) — and
look at `summary.txt` plus the `.png` plots inside. Every run gets its own
timestamped subfolder, so re-running never overwrites a previous result —
it's safe to point `-o` at the same folder every time.

### Comparing groups (e.g. control vs. mutant)

To analyze several recordings together and get a side-by-side comparison,
list them in a "runs" TOML file instead of passing paths directly:

```toml
# runs/my_experiment.toml
[groups.control]
files = ["/data/control_1.braidz", "/data/control_2.braidz"]

[groups.mutant]
files = ["/data/mutant_1.braidz"]
```

```bash
uv run optofly-analyze -r runs/my_experiment.toml -o results/
```

Two or more groups automatically get extra overlay plots under
`results/<timestamp>/comparison/`.

## CLI reference

```
optofly-analyze [files ...] [-p PARAMS] [-r RUNS] [--only {stim,opto,both,none}] [-o OUTPUT]
```

| Flag | Meaning |
|------|---------|
| `files` (positional) | One or more `.braidz` paths for a quick single-group run. Treated as one group named `data`. Cannot be combined with `-r`. |
| `-p, --params PATH` | TOML file with a `[parameters]` table (tuning). Optional — sensible defaults are used if omitted. |
| `-r, --runs PATH` | TOML file with `[groups.<name>]` tables (which files to analyze, and how to group them for comparison). Cannot be combined with positional `files`. |
| `--only {stim,opto,both,none}` | Force which event analyses run, overriding auto-detection. Behavioral plots always run regardless. |
| `-o, --output DIR` | Output directory (default `./optofly_results`). Each run writes its own timestamped subfolder inside it. |

> ⚠️ **Common failure:** `Provide either files or --runs, not both.` — pick
> one input mode. Either list `.braidz` paths directly on the command line,
> or put them in a `-r/--runs` TOML file, not both at once.

## Output layout

```
results/
  20260805_143022/                     <- one timestamped folder per run
    <group>/
      behavior/   velocity/saccade plots (always produced)
      stim/       looming-stimulus response plots (only if the file has a real stim log)
      opto/       optogenetic response plots (only if opto.csv is present)
      opto_effect/ compares loom response with/without nearby opto (only if both stim and opto data are present)
    comparison/   overlay plots (only if you defined 2+ groups)
    summary.txt   object/saccade/event counts and percent responsive, per group
```

`stim/`, `opto/`, and `opto_effect/` only appear when the corresponding data
was found *and usable* — nothing is guessed or invented for missing data.

> ⚠️ **Common failure:** `[<group>] no usable files, skipping group` — the
> `.braidz` path is wrong, or the file doesn't actually contain tracking
> data. Double-check the path and that the file finished writing or copying
> correctly.

> ⚠️ **Common failure:** stim or opto plots don't show up even though you
> know the file has that data — some acquisition setups write a generic
> `stim.csv` trigger log even for opto-only recordings, with no real looming
> parameters, so it's correctly skipped by default. Force it with
> `--only stim` / `--only opto` / `--only both`, or add `run_stim = true` /
> `run_opto = true` to a `[parameters]` table passed via `-p`.

## Development

```bash
uv run pytest        # tests
uv run ruff check    # lint
```

## Full documentation

[OptoFly Analysis README](../repos/optofly-analysis/README.md) — the full
troubleshooting list, the library API for custom scripts/notebooks, and the
`notebooks/` directory for exploring a single recording interactively.
