# Environment Setup

These are things every repo in this project needs. Do this once per
machine, before setting up any individual tool.

## 1. Install `uv`

`uv` is the tool all 4 repos use to install their Python dependencies. It
replaces `pip` and virtual environment management with one command.

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Confirm it worked:

```bash
uv --version
```

You should see something like `uv 0.x.y`.

> ⚠️ **Common failure:** `uv: command not found` right after installing —
> the installer added `uv` to a directory not yet on your shell's `PATH`.
> Close and reopen your terminal, or run `source ~/.bashrc` (or
> `~/.zshrc` if you use zsh).

## 2. Set up a shared source directory

Some repos expect their sibling repos checked out next to them (for example,
`liquid-lens-calibration` and `optofly` both load `optotune-lens` from
`../optotune-lens`). Clone all repos into the **same parent directory**:

```bash
mkdir -p ~/src
cd ~/src
git clone git@github.com:mpinb/optofly.git
git clone git@github.com:mpinb/optotune-lens.git
git clone git@github.com:mpinb/liquid-lens-calibration.git
git clone git@github.com:mpinb/basler-charuco-calibrator.git
git clone git@github.com:mpinb/ximea-py.git
```

After this, you should see all five as sibling folders:

```bash
ls ~/src
# basler-charuco-calibrator  liquid-lens-calibration  optofly  optotune-lens  ximea-py
```

> ⚠️ **Common failure:** `git clone` asks for a username and password, then
> fails — you're using the HTTPS URL without credentials set up. Use the
> `git@github.com:...` (SSH) URL shown above, and make sure you've added an
> SSH key to your GitHub account first (GitHub's own
> [SSH key setup guide](https://docs.github.com/en/authentication/connecting-to-github-with-ssh)
> covers this).

## 3. Hardware SDKs

Two repos need vendor SDKs installed system-wide (not through `uv`) before
`uv sync` will fully work. On a completely fresh machine, neither SDK is
installed yet — do both of these before anything else in this section.

- **Basler Pylon SDK** — required by `basler-charuco-calibrator` and
  `liquid-lens-calibration` (both use Basler cameras).

  [Braid](https://strawlab.org/braid/) (the tracking system this project
  builds on) only supports up to **Pylon 7.3** — do not install a newer
  version. Download it directly from
  [Basler's downloads page, pinned to version 7.3.0](https://www.baslerweb.com/de-de/downloads/software/?downloadCategory.values.label.data=pylon&softwareVersion.data=7.3.0).

  1. Download the Linux `.tar.gz` archive for your architecture.
  2. Unzip it:
     ```bash
     tar -xzf basler_pylon_*.tar.gz
     ```
  3. Open the extracted folder and follow the steps in its `INSTALL` file
     — Basler's installer is a script inside the archive, not a single
     command documented here.

  > ⚠️ **Common failure:** picking the newest Pylon version instead of
  > 7.3 — Braid won't work with it. Double-check the version number on the
  > downloaded filename before installing.

- **XIMEA xiAPI runtime** (`libm3api.so.2`) — required by
  `liquid-lens-calibration` (uses a XIMEA camera to measure focus
  sharpness) and by `ximea-py`, the driver library it talks to that camera
  through. Install the latest driver using the install script shipped in
  the `optofly` repo (not from XIMEA's site directly):

  ```bash
  cd ~/src/optofly/scripts
  sudo ./install_ximea_driver.sh
  ```

  You need `optofly` already cloned first — see
  [step 2 below](#2-set-up-a-shared-source-directory) if you haven't done
  that yet.

These are one-time, per-machine installs — you won't need to repeat them
when setting up an individual repo below.

## 4. Braid

Several tools in this project assume [Braid](https://strawlab.org/braid/)
(the multi-camera 3D tracking system this project builds on) is already
installed and running. Braid is a separate, external project — installing
it is outside the scope of this wiki. See Braid's own documentation for
setup instructions.

## 5. udev rules (device permissions and names)

Ubuntu doesn't let normal users access USB devices like the cameras or
Arduino by default, and doesn't guarantee they get the same device name
every time you plug them in. This machine already has the rules needed for
every device this project uses — see [udev Rules](udev-rules.md) for what
they do and how to add one if you swap in a replacement device.

## Next step

Once this is done, follow the setup page for whichever tool you need:

- [udev Rules](udev-rules.md) — device permissions, only needed if you're setting up a new machine or replacing hardware
- [Basler ChArUco Calibrator](basler-charuco-calibrator-setup.md) — camera calibration (do this first)
- [Liquid Lens Calibration](liquid-lens-calibration-setup.md) — lens calibration (after Braid is tracking)
- [OptoFly](optofly-setup.md) — running experiments (set up last)
- [Optotune Lens](optotune-lens-setup.md) — the lens driver library (usually installed automatically as a dependency of the two tools above, not run standalone)
- [Ximea Py](ximea-py-setup.md) — the XIMEA camera driver library used by `liquid-lens-calibration` (usually installed automatically as a dependency, not run standalone)
