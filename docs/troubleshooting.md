# Troubleshooting

This page covers issues that span repos. For issues inside `optofly`
itself once it's running, see
[OptoFly's own Troubleshooting doc](repos/optofly/troubleshooting.md).

## `git clone` fails or points at the wrong place

5 of the 7 repos moved to the `mpinb` GitHub organization
(`braid-opto-power-measure` and `optofly-analysis` are the exceptions —
still under a personal account). If you have an old clone of one of the
other 5 that still points at a personal account, check and fix it:

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

## Braid crashed while recording, leaving a `.braid` folder behind

While Braid is recording a tracking session, it writes data into a folder
whose name ends in `.braid` (e.g. `20260731_143022.braid`). On this
project's machines that folder is saved under `/mnt/data/experiments/` —
this is set by `experiments_path` in `optofly`'s own
`configs/config.toml` (see
[`optofly`'s Getting Started doc](repos/optofly/getting-started.md)), which
must match Braid's own `output_base_dirname` config. (Braid's own default,
if you're on a machine that hasn't been configured this way, is
`~/BRAID-DATA/`.) When a recording stops normally, Braid
automatically compresses that folder into a single `.braidz` file (a
**`.braidz` file** is just a ZIP file with a fixed set of contents) and
deletes the folder. If Braid, or the whole computer, crashes while a
recording is still running, that last step never happens — you're left
with the raw `.braid` folder and no `.braidz` file.

Braid's own code (a separate project called `strand-braid`, **not** one of
the 7 repos this wiki otherwise covers — see
[Environment Setup](setup/environment.md#4-braid)) includes a small Rust
tool that does exactly this compression step by hand:
`braidz-writer-cli`. `optofly` also ships a pure-Python script,
`scripts/braidz_writer.py`, that does the same thing without needing the
Rust toolchain — use that unless you have a reason to prefer the Rust tool
(see [the alternative below](#alternative-the-rust-braidz-writer-cli-tool)).

1. **Find the crashed folder.** Look under `/mnt/data/experiments/` for a
    folder ending in `.braid` (not `.braidz`) with a timestamp matching the
    crash.

2. **Zip the crashed folder,** using the Python script from inside
    `optofly` (replace the folder name with your own):

    ```bash
    cd ~/src/OptoFly
    uv run python scripts/braidz_writer.py /mnt/data/experiments/20260731_143022.braid
    ```

    This writes a new `20260731_143022.braidz` file next to the folder and
    does **not** delete or modify the original folder. It refuses to
    overwrite an existing `.braidz` file unless you add `--force`.

    > ⚠️ **Common failure:** zipping the folder by hand instead (e.g.
    > `zip -r out.braidz 20260731_143022.braid`). This bakes the folder's
    > name into every path inside the archive, which produces a file that
    > looks fine but that Braid's own tools (and the online viewer) will
    > refuse to read correctly. Always use the script above instead of a
    > manual `zip` command.

3. **Check the result** before deleting anything:

    ```bash
    unzip -l /mnt/data/experiments/20260731_143022.braidz
    ```

    You should see plain filenames with no folder prefix — `README.md`,
    `braid_metadata.yml`, `kalman_estimates.csv.gz`, and similar. If you see
    `20260731_143022.braid/README.md` instead, something went wrong in step
    2 above.

    > ⚠️ **Common failure:** the last second or so of tracking data is
    > missing or unreadable in the new file. This is expected, not a
    > mistake in these steps — Braid only writes data to disk roughly once
    > per second, so anything not yet written at the exact moment of the
    > crash is genuinely lost. Everything recorded before that point should
    > still be intact.

4. **Clean up.** Once the `.braidz` file checks out, it's safe to delete
    the original `.braid` folder — this is the same cleanup Braid would
    have done itself on a normal, non-crash shutdown.

### Alternative: the Rust `braidz-writer-cli` tool

If you'd rather use Braid's own Rust tool instead of the Python script in
step 2 above, build it once from inside `strand-braid` (assumes that repo
is already on this machine, typically at `~/src/strand-braid` — it's
needed to build Braid itself):

```bash
cd ~/src/strand-braid
cargo build --release -p braidz-writer-cli
```

Then run it, **always passing `--dest` explicitly**:

```bash
~/src/strand-braid/target/release/braidz-writer-cli \
  /mnt/data/experiments/20260731_143022.braid \
  --dest /mnt/data/experiments/20260731_143022.braidz
```

> ⚠️ **Common failure:** omitting `--dest`. Without it, this tool's
> default naming produces `20260731_143022.braid.braidz` (a doubled-up
> `.braid.braidz` extension), not the clean `20260731_143022.braidz` name
> Braid itself would use — a quirk in the tool's own default-name logic,
> confirmed by running it. Passing `--dest` explicitly sidesteps it
> entirely.

> ⚠️ **Common failure:** `cargo: command not found`. `cargo` is Rust's
> build tool — the same one used to build Braid itself. If it's missing,
> Rust isn't installed on this machine; see Braid's own setup docs
> (installing Braid and Rust is outside this wiki's scope, as noted in
> [Environment Setup](setup/environment.md#4-braid)).
