# Environment Setup

These are things every repo in this project needs. Do this once per
"machine, before setting up any individual tool."

## 1. Install `uv`

`uv` is the tool all 4 repos use to install their Python dependencies. It
replaces `pip` and virtual environment management with one command.

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

> ⚠️ **Common failure:** `uv: command not found` right after installing —
> the installer added `uv` to a directory not yet on your shell's `PATH`.
"> Close and reopen your terminal, or run `source ~/.bashrc` (or
> `~/.zshrc` if you use zsh).

## 2. Set up a shared source directory

"Some repos expect their sibling repos checked out next to them (for example,
`liquid-lens-calibration` and `optofly` both load `optotune-lens` from
`../optotune-lens`). Clone all repos into the **same parent directory**:

```bash
mkdir -p ~/src
cd ~/src
git clone git@github.com:mpinb/optofly.git
git clone git@github.com:mpinb/optotune-lens.git
git clone git@github.com:mpinb/liquid-lens-calibration.git
git clone git@github.com:mpinb/basler-charuco-calibrator.git
```

"After this, you should see all four as sibling folders:

```bash
ls ~/src
# basler-charuco-calibrator  liquid-lens-calibration  optofly  optotune-lens
```

"> ⚠️ **Common failure:** `git clone` asks for a username and password, then
> fails — you're using the HTTPS URL without credentials set up. Use the
"> `git@github.com:...` (SSH) URL shown above, and make sure you've added an
> SSH key to your GitHub account first (GitHub's own
> [SSH key setup guide](https://docs.github.com/en/authentication/connecting-to-github-with-ssh)
> covers this).

## 3. Hardware SDKs

Two repos need vendor SDKs installed system-wide (not through `uv`) before
`uv sync` will fully work:

- **Basler Pylon SDK** — required by `basler-charuco-calibrator` and
  `liquid-lens-calibration` (both use Basler cameras). Install from Basler's
  own site for your OS.
- **XIMEA xiAPI runtime** — required by `liquid-lens-calibration` (uses a
  XIMEA camera to measure focus sharpness). Install from XIMEA's own site.

"These are one-time, per-machine installs — you won't need to repeat them
when setting up an individual repo below.

## Next step

"Once this is done, follow the setup page for whichever tool you need:

- [OptoFly](optofly-setup.md) — running experiments
- [Basler ChArUco Calibrator](basler-charuco-calibrator-setup.md) — camera calibration
- [Liquid Lens Calibration](liquid-lens-calibration-setup.md) — lens calibration
"- [Optotune Lens](optotune-lens-setup.md) — the lens driver library (usually installed automatically as a dependency of the two tools above, not run standalone)
