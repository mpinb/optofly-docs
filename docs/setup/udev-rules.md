# udev Rules (Linux/Ubuntu)

This page explains a Linux concept you'll hit as soon as you plug in the
project's cameras and Arduino: by default, USB devices are only accessible
to the `root` user, or get a random device name that changes every time you
unplug and replug them. **udev** is the part of Ubuntu that assigns
permissions and names to devices when they're plugged in. A **udev rule**
is a text file that tells udev "when this specific device shows up, give it
this fixed name and let normal users access it" — without one, tools in
this project either fail with a permissions error, or can't find the
device because its name changed.

This machine already has working udev rules for every device this project
uses. This page explains what they do and how to add one for a new device,
using the existing ones as reference.

## Where rules live

Rules are plain text files in `/etc/udev/rules.d/`, read in filename order.
Editing them requires `sudo` (they're a system-wide setting, not per-user).

```bash
ls /etc/udev/rules.d/
```

The ones relevant to this project on this machine:

| File | Device | What it does |
|------|--------|---------------|
| `69-basler-cameras.rules` | Basler tracking cameras | Any USB device from Basler (vendor ID `2676`) gets world-readable/writable access |
| `99-arduino.rules` | Arduino (opto-trigger board) | Fixes a stable name `/dev/opto_trigger` for the specific Arduino used for LED/backlight control, matched by its unique USB serial number |
| `99-optotune-icc1c.rules` | Optotune ICC1C lens driver | Fixed name `/dev/optotune_icc1c`, matched by serial number |
| `99-optotune.rules` | Optotune lens driver (older/other model) | Fixed name `/dev/optotune_ld`, matched by vendor/product ID only (no serial — any device of this exact model gets the name) |
| `99-pico.rules` | Raspberry Pi Pico | Fixed name `/dev/ttyPICO`, matched by serial number |
| `99-thorlabs.rules` | Thorlabs USB devices | Any device from Thorlabs (vendor ID `1313`) gets access |
| `99-ximea.rules` | XIMEA USB cameras | Any XIMEA USB camera (by vendor/product ID) gets access |
| `99-ximea-pcie.rules` | XIMEA PCIe cameras | Keeps XIMEA PCIe cameras powered on |

You can view any of these with `cat`, e.g.:

```bash
cat /etc/udev/rules.d/99-arduino.rules
```

## Why device names matter here

Several config files in this project (e.g. `optofly`'s `configs/config.toml`,
see [Opto Trigger](../repos/optofly/opto-trigger.md)) hardcode a device
path like `/dev/opto_trigger`. Without a udev rule, Linux would instead
call that same Arduino something like `/dev/ttyUSB0` or `/dev/ttyACM0` —
and which number it gets can change depending on what else is plugged in
and the order you plugged things in. The udev rule pins a fixed,
predictable name to that specific physical device (by its USB serial
number), so the config file never needs to change.

> ⚠️ **Common failure:** a tool can't find `/dev/opto_trigger` (or a similar
> named device) even though the Arduino is plugged in — either the udev
> rule for that exact device isn't installed on this machine, or you're
> using a *different* Arduino unit than the one the rule's serial number
> matches. Run `ls -l /dev/opto_trigger` — if it doesn't exist, see
> [Adding a new rule](#adding-a-new-rule-for-a-replacement-device) below.

## Checking a device already has a working rule

1. Plug the device in.
2. Check whether its expected symlink exists:

   ```bash
   ls -l /dev/opto_trigger /dev/optotune_icc1c /dev/optotune_ld /dev/ttyPICO
   ```

   Each line should point at a real device, e.g.:

   ```
   lrwxrwxrwx 1 root root 7 Jul 31 10:02 /dev/opto_trigger -> ttyUSB0
   ```

   If the symlink is missing, either the device isn't plugged in, or no
   rule matches it (see below).

3. For cameras (Basler, XIMEA, Thorlabs), there's no fixed name — the rule
   just grants permission. Confirm the *permission* worked instead of a
   symlink, by checking that the vendor tool (Basler Pylon Viewer, XIMEA's
   `xiCOP`, etc.) can open the camera without needing `sudo`.

## Adding a new rule (for a replacement device)

If you swap in a new Arduino, Optotune driver, or other board with a fixed
name expected by a config file, its USB serial number is different from
the old one, so the existing rule won't match it. You need a new rule
entry.

1. **Plug in only the new device** (unplug others of the same type
   temporarily, to avoid confusing it with another device).

2. **Find its vendor ID, product ID, and serial number:**

   ```bash
   udevadm info -a -n /dev/ttyUSB0
   ```

   Replace `/dev/ttyUSB0` with whatever it currently shows up as — check
   `dmesg | tail` right after plugging in to see the name Linux assigned.
   Look near the top of the output for a block like:

   ```
   ATTRS{idVendor}=="0403"
   ATTRS{idProduct}=="6001"
   ATTRS{serial}=="A10LT9BA"
   ```

   These three values uniquely identify this exact physical device.

3. **Write the rule.** Open the relevant existing file with `sudo` (or
   create a new one, e.g. `sudo nano /etc/udev/rules.d/99-arduino.rules`)
   and add a line following the pattern already used in that file:

   ```
   SUBSYSTEM=="tty", ATTRS{idVendor}=="0403", ATTRS{idProduct}=="6001", ATTRS{serial}=="A10LT9BA", SYMLINK+="opto_trigger", MODE="0666"
   ```

   Match `SUBSYSTEM` and the general shape to the existing entries in that
   file — serial-based rules use `tty` + `SYMLINK+=`, vendor-only rules
   (that just grant access to any device of that model) use `usb` +
   `GROUP=`.

4. **Reload udev and re-trigger it** so the new rule takes effect without
   a reboot:

   ```bash
   sudo udevadm control --reload-rules
   sudo udevadm trigger
   ```

5. **Unplug and replug the device**, then confirm the symlink appears:

   ```bash
   ls -l /dev/opto_trigger
   ```

> ⚠️ **Common failure:** the rule doesn't take effect after
> `udevadm trigger` — udev only re-evaluates rules for devices as they're
> *added*; existing connections aren't retroactively re-matched. Physically
> unplug and replug the device (or `sudo udevadm trigger --action=add`) —
> don't just reload the rules and expect an already-connected device to
> pick up the change.

> ⚠️ **Common failure:** `Permission denied` opening the device even though
> the symlink exists — some rules use `GROUP="dialout"` or
> `GROUP="plugdev"` instead of `MODE="0666"`. Check which group the rule
> uses (`cat` the rule file), then confirm your user is a member:
> `groups $USER`. If not, add yourself and log out/in for it to take
> effect: `sudo usermod -aG dialout $USER` (swap in the correct group
> name).

## Full documentation

For the full protocol and pin wiring of the Arduino this `99-arduino.rules`
file targets, see [Opto Trigger](../repos/optofly/opto-trigger.md).
