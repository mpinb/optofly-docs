# udev Rules (Linux/Ubuntu)

This page explains a Linux concept you'll hit as soon as you plug in the
project's cameras and Arduino: by default, USB devices are only accessible
to `root` (Linux's built-in administrator account — the one thing on the
system allowed to do anything, including things a normal user account
can't), or get a random device name that changes every time you unplug and
replug them. **udev** is the part of Ubuntu that assigns permissions and
names to devices when they're plugged in. A **udev rule** is a text file
that tells udev "when this specific device shows up, give it this fixed
name and let normal users access it" — without one, tools in this project
either fail with a permissions error, or can't find the device because its
name changed.

The fixed name a udev rule creates (e.g. `/dev/opto_trigger`) is technically
a **symlink** — a shortcut file that points at whatever the real,
auto-generated device name currently is (like `/dev/ttyUSB0`). You can
mostly ignore that detail and just treat `/dev/opto_trigger` as "the
Arduino's address," the same way you'd treat a nickname.

This machine already has working udev rules for every device this project
uses. This page explains what they do and how to add one for a new device,
using the existing ones as reference.

## Where rules live

Rules are plain text files in `/etc/udev/rules.d/`, read in filename order.
Editing them requires `sudo` — short for "superuser do," it runs a single
command with administrator privileges. It's needed here because
`/etc/udev/rules.d/` is a system-wide settings folder, not something a
normal user account can change. `sudo` will prompt for your account
password; nothing appears on screen as you type it, which is normal.

```bash
ls /etc/udev/rules.d/
```

The ones relevant to this project on this machine:

| File | Device | What it does |
|------|--------|---------------|
| `69-basler-cameras.rules` | Basler tracking cameras | Any USB device from Basler (vendor ID `2676`) is opened up so any user account on the machine can read from and write to it |
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

> This section is more advanced than the rest of this wiki, and something
> you'll only need rarely (when hardware is replaced). If you're not
> comfortable editing system files from the terminal, it's reasonable to
> ask a labmate or your PI to do this step rather than working through it
> alone the first time.

If you swap in a new Arduino, Optotune driver, or other board with a fixed
name expected by a config file, its USB serial number is different from
the old one, so the existing rule won't match it. You need a new rule
entry.

1. **Plug in only the new device** (unplug others of the same type
   temporarily, to avoid confusing it with another device).

2. **Find its vendor ID, product ID, and serial number** — three codes
   that together uniquely identify this exact physical device (not just
   "an Arduino," but *this* Arduino).

   First, find what temporary name Linux gave the device by running:

   ```bash
   dmesg | tail
   ```

   `dmesg` prints the system's recent hardware log; `| tail` (pronounced
   "pipe tail") shows just the last few lines, which will include
   something like `usb 3-2: cdc_acm converter now attached to ttyUSB0`
   right after you plug the device in. That `ttyUSB0` is the name to use
   next:

   ```bash
   udevadm info -a -n /dev/ttyUSB0
   ```

   Replace `/dev/ttyUSB0` with whatever `dmesg` showed you. This command
   prints a long block of device details — scroll up to the top of it and
   look for a block like:

   ```
   ATTRS{idVendor}=="0403"
   ATTRS{idProduct}=="6001"
   ATTRS{serial}=="A10LT9BA"
   ```

   These three values uniquely identify this exact physical device.

3. **Write the rule.** Open the relevant existing file with `sudo` and a
   terminal text editor — `nano` is the simplest one on Ubuntu:

   ```bash
   sudo nano /etc/udev/rules.d/99-arduino.rules
   ```

   Use the arrow keys to move to the end of the file and add a new line.
   To save and exit `nano`: press **Ctrl+O** then **Enter** to save, then
   **Ctrl+X** to exit.

   Add a line following the pattern already used in that file:

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
> the symlink exists — some rules grant access via `GROUP="dialout"` or
> `GROUP="plugdev"` instead of `MODE="0666"`. A **group** is Linux's way of
> bundling a set of permissions and handing them to whichever user
> accounts are members of it — this rule says "let anyone in the
> `dialout` group use this device." Check which group the rule uses
> (`cat` the rule file), then confirm your own account is a member:
> ```bash
> groups $USER
> ```
> This lists every group your account belongs to. If the group the rule
> needs isn't in that list, add yourself to it:
> ```bash
> sudo usermod -aG dialout $USER   # swap in the correct group name
> ```
> Then **log out and log back in** (not just close the terminal) — group
> membership is only re-read at login, so the device will still refuse
> access until you do.

## Full documentation

For the full protocol and pin wiring of the Arduino this `99-arduino.rules`
file targets, see [Opto Trigger](../repos/optofly/opto-trigger.md).
