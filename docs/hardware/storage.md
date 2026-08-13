# Storage

This page describes the physical disks (hard drives) inside `nfc3008`, the
computer this lab uses to run OptoFly experiments — which cameras connect to
it, which software runs on it, and where all of the data it produces lives.
If you're reading this on a different computer, none of this applies; ask a
labmate which machine is `nfc3008` if you're not sure.

The exact amount of free space on each disk changes constantly as
experiments run — don't worry if the numbers below don't match what you see
when you check yourself. What doesn't change is the *layout*: which disk
holds what kind of data, and why.

## The disks, in plain terms

A computer's storage is split across separate physical disks, and each disk
is attached to the file system at a **mount point** — the folder name Linux
uses as the "front door" into that disk. When you look inside a mount
point's folder, you're looking at files on that specific physical disk, not
the computer's main disk. This machine has four disks, described below in
the order you're likely to care about them.

### The main drive (`/`)

Mount point: `/` (a single forward slash — this is the "root" of the whole
file system, not a specific folder name).

This drive holds the operating system (Ubuntu Linux), every program
installed on the machine, and the `nfc` user's home folder
(`/home/nfc` — code checkouts, this wiki, editor settings, and so on). It's
a 1TB NVMe SSD (a fast type of solid-state drive that plugs directly into
the motherboard rather than connecting with a cable) — a Samsung 970 EVO
Plus.

### The working data disk (`/mnt/data`)

Mount point: `/mnt/data`.

This is where `optofly` writes recordings — video files and `.braidz`
tracking files — while an experiment is running, and where they stay
immediately afterward. It's a separate 2TB NVMe SSD (a Samsung 990 PRO),
chosen specifically because it's fast enough to keep up with several
cameras recording video at once, which the main drive doesn't need to be
optimized for.

### The long-term storage disk (`/mnt/storage`)

Mount point: `/mnt/storage`.

Once a recording is finished, a copy of it ends up here permanently (see
[Backups](backups.md) for exactly how and when). Unlike the other disks,
this one isn't a single physical drive — it's **two** matched 8TB hard disk
drives (traditional spinning-platter drives, not solid-state) set up as
what's called a **RAID1 mirror**: every file written here is automatically
duplicated onto both drives at once, so if one drive physically breaks,
nothing is lost and the computer keeps working normally off the other
drive. Linux presents both drives to you as a single folder,
`/mnt/storage` — you never interact with the two drives separately.

### The backup disk (`/mnt/system_backups`)

Mount point: `/mnt/system_backups`.

A 1TB SATA SSD (a solid-state drive that connects via a cable, rather than
plugging directly into the motherboard like the main and working drives
do) dedicated entirely to holding a backup of the `nfc` user's home folder.
See [Backups](backups.md) for what that means and how it works — this page
is only about the disk itself.

## At a glance

| Disk | Size | Type | Mount point | What it's for |
|---|---|---|---|---|
| Samsung 970 EVO Plus | 1TB | NVMe SSD | `/` | Operating system, programs, home folder |
| Samsung 990 PRO | 2TB | NVMe SSD | `/mnt/data` | Active/recent experiment recordings |
| 2× 8TB HDD (RAID1 mirror) | 7.3TB usable | HDD | `/mnt/storage` | Permanent storage of finished recordings |
| Samsung 860 EVO | 1TB | SATA SSD | `/mnt/system_backups` | Backup of the home folder |

## Checking how full a disk is

Open a terminal and run:

```bash
df -h
```

`df` stands for "disk free" — it lists every disk and how much space is
used. The `-h` flag means "human-readable," so it shows sizes like `1.8T`
instead of a huge number of bytes. You'll see a line for each disk in the
table above, plus some you can ignore (they're internal to the system). As
of 2026-08-13, the ones that matter looked like this:

```
Filesystem      Size  Used Avail Use% Mounted on
/dev/nvme1n1p2  915G  203G  666G  24% /
/dev/nvme0n1    1.8T  1.3T  500G  72% /mnt/data
/dev/md0        7.3T  6.1T  803G  89% /mnt/storage
/dev/sdc1       916G   46G  824G   6% /mnt/system_backups
```

The `Use%` column is the one to watch — it's how full that disk currently is.

## Common failures

> ⚠️ **Common failure:** `/mnt/storage` (the long-term storage disk) is
> already at 89% full as of 2026-08-13, and it only ever grows — the daily
> copy job that fills it (see [Backups](backups.md)) never deletes
> anything, even if the original file is deleted from `/mnt/data`. Nothing
> on this machine automatically frees up space. If a backup or copy job
> starts failing with a message like "No space left on device" in its log
> file, this disk is likely full — someone needs to manually go through
> old recordings and delete or move ones that are no longer needed.

> ⚠️ **Common failure:** one of the two drives in the `/mnt/storage`
> mirror fails. Check its health with:
> ```bash
> cat /proc/mdstat
> ```
> A healthy mirror shows `[UU]` (both drives Up). A failed drive shows
> something like `[U_]` (one drive missing) instead. Nothing on this
> machine automatically alerts anyone when this happens — recognizing it
> requires someone to run this command and look. If you see anything
> other than `[UU]`, treat it as urgent: with one drive already down, a
> second failure would lose everything on `/mnt/storage`.

> ⚠️ **Common failure:** after a reboot, one of the `/mnt/*` disks seems to
> be "missing" — but the machine boots up normally with no error message
> at all. This machine's disk configuration (`/etc/fstab`) is deliberately
> set to boot normally even if a disk fails to attach, rather than getting
> stuck on an error screen. That means a missing disk fails *silently*: a
> folder like `/mnt/data` will still exist and look empty, instead of
> showing an error. If a mount point looks unexpectedly empty, that's the
> first thing to suspect — compare against the "at a glance" table above,
> and ask a labmate for help checking the physical drive connection.
