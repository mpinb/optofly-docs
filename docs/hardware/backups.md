# Backups

Three separate, independent jobs run automatically on `nfc3008` to protect
against losing data. Automatic here means a **cron job** — a task the
computer runs by itself at a scheduled time, with nobody needing to be
logged in — or a similar tool doing the same thing a different way. You
don't need to start these by hand, and under normal circumstances you'll
never see them running.

Each job protects against a different kind of loss — read the "protects
against" column below carefully, since none of them protects against
everything.

("Mirror" here means a job that copies files to another disk on a
schedule — a different use of the word than the RAID1 disk mirror
described on the [Storage](storage.md) page, where "mirror" means two
drives holding identical copies at all times.)

## At a glance

| Job | Copies | Schedule | Protects against | Status |
|---|---|---|---|---|
| Local mirror | `/mnt/data` → `/mnt/storage` | Daily, 12:00 | The working disk failing, or a finished file being accidentally deleted before it's archived | Working |
| Offsite mirror | `/mnt/storage` → a remote server | Daily, 13:00 | Losing the entire machine (theft, fire, complete hardware failure) | Working |
| Home folder backup | `/home/nfc` → `/mnt/system_backups` | Weekly | Losing installed software, configuration, and code on the main drive | Working, but see note below |

## Local mirror: `/mnt/data` → `/mnt/storage`

Every day at noon, this command runs automatically:

```bash
rsync -a --exclude=".Trash-1000/" --include="*.braidz" --exclude="*" \
  /mnt/data/experiments/ /mnt/storage/experiments/

rsync -a --prune-empty-dirs --exclude=".Trash-1000/" --include="*/" \
  --include="*.mp4" --include="*.csv" --exclude="*" \
  /mnt/data/videos/ /mnt/storage/videos/
```

`rsync` is a program that copies files from one folder to another, only
copying files that are new or changed since the last time it ran — much
faster than copying everything every time. The `--include`/`--exclude`
flags mean it only copies `.braidz` tracking files, plus `.mp4` video and
`.csv` files, skipping everything else (including `.Trash-1000`, a hidden
folder the file manager uses for its own Trash/Recycle Bin).

This job only ever *adds* files to `/mnt/storage` — it never deletes
anything there, even if the original is deleted from `/mnt/data`. That's
also why `/mnt/storage` keeps filling up over time (see
[Storage](storage.md#common-failures)).

Its log file (a text file recording what happened each time it ran) is at
`/home/nfc/rsync-data-to-storage.log`. To check today's run:

```bash
tail /home/nfc/rsync-data-to-storage.log
```

`tail` shows the last few lines of a file — useful for logs, which grow
over time and where only the most recent entries usually matter.

## Offsite mirror: `/mnt/storage` → a remote server

A second job, structured the same way, runs daily at 13:00 and copies
`/mnt/storage` to a remote server over the network (the lab's institutional
computing cluster) instead of another local disk — this is what protects
against losing the whole machine, not just one disk. Its real command uses
a real server address, username, and remote folder path; since this wiki
is public on the internet, those specific values aren't published here.
Shaped like this instead:

```bash
rsync -a --no-owner --no-group --include="*.braidz" --exclude="*" \
  /mnt/storage/experiments/ <remote-user>@<remote-host>:<remote-path>/experiments/
```

A second, near-identical command (not shown) does the same for
`/mnt/storage/videos/`.

Anyone working directly on `nfc3008` can see the real values by running
`crontab -l` in a terminal.

> ⚠️ **Common failure: `Permission denied` in this job's log.** This job
> logs in to the remote server over SSH — a way for one computer to
> securely control another over the network — using a saved login key
> instead of typing a password. If the remote server stops trusting that
> key, every run ends with `Permission denied` in this job's log,
> `/home/nfc/rsync-storage-to-*.log` (the offsite job's log and lock
> files are named after the remote server, whose real name isn't
> published on this public wiki — the `*` matches whatever it's actually
> called on this machine). This actually happened on this machine: every
> run failed this way up through 2026-08-02, then started working again
> on its own a day or two later — most likely because something changed
> on the remote server's side, since nothing on this machine's own setup
> was touched. As of 2026-08-13, this job is confirmed working: the files
> it copies match the remote server's copy exactly. If you see
> `Permission denied` in this job's log again, it means the remote server
> has stopped trusting this machine's login key — ask whoever manages
> accounts on that remote server to check it's still authorized there.
> This isn't something you can fix from `nfc3008` alone.

## Home folder backup: `/home/nfc` → `/mnt/system_backups`

A tool called `duplicity` backs up the entire `/home/nfc` folder (code,
configuration, this wiki, everything a user would lose if the main drive
failed) into `/mnt/system_backups`. Instead of copying the full 159GB
folder every time, it made one full copy on 2026-06-25, and now saves only
a small "what changed" file roughly once a week — much faster, and much
less disk space, than a fresh full copy every time.

> **Not verified:** this wiki couldn't confirm exactly what schedules
> `duplicity` to run — it isn't in the `nfc` user's own scheduled jobs, and
> checking the machine's own administrator (root) schedule needs
> administrator access this wiki's author didn't have when writing this
> page. Whoever has administrator access on this machine can check with:
> ```bash
> sudo crontab -l -u root
> ```
> and update this page once confirmed. Not knowing the trigger doesn't
> mean the backup itself is unreliable, though: the job demonstrably has
> been running on schedule, roughly weekly, based on the timestamps of
> the backup files already sitting in `/mnt/system_backups` — this is a
> documentation gap, not evidence of a broken job.

## Restoring a file

**From the long-term storage disk** (`/mnt/storage`): these are just
plain folders, so getting a file back is a plain copy. (The offsite
copy on the remote server should have the same files, but restoring
from it isn't documented here — it needs a separate login on that
remote server, which most people reading this wiki won't have.)

```bash
cp /mnt/storage/experiments/some_experiment.braidz ~/Desktop/
```

**From the home folder backup**: use `duplicity`'s own restore command,
telling it which backup to read from (`file:///mnt/system_backups`) and
where to put the restored files:

```bash
duplicity restore file:///mnt/system_backups ~/restored_home
```

This creates a new folder, `~/restored_home`, with a full copy of the
backup as of the most recent run. The backup was made of `/home/nfc`'s
full path from the filesystem root, so the restored files actually land
under `~/restored_home/home/nfc/...` — not directly inside
`~/restored_home/` itself — look one level deeper than you might
expect. This also restores the *entire* ~159GB backup, so it can take a
while and use a lot of disk space.

To restore just a single file instead, add `--path-to-restore` with the
file's path as it's stored inside the backup (starting with
`home/nfc/...`):

```bash
duplicity restore --path-to-restore home/nfc/some/file.txt \
  file:///mnt/system_backups ~/restored_file
```

This restores only that one file, saving you from restoring everything
just to get it back.

Either command refuses to run — with an error, rather than silently
overwriting anything — if its destination folder (`~/restored_home` or
`~/restored_file` above) already exists. Pick a different destination
folder name if you need to restore more than once.

If you need an older version specifically, ask a labmate for help —
`duplicity` supports restoring to a specific date, but it's easy to get
wrong.

## Common failures

> ⚠️ **Common failure: an empty-looking log doesn't always mean a job is
> broken.** `rsync` normally prints nothing at all when it succeeds — so
> a job that's working perfectly and a job that's been dead for days can
> look identical in the log. Since 2026-08-13, both backup jobs print a
> line like `[2026-08-13 13:00:03] backup completed successfully` at the
> end of every successful run, so you can tell the two apart:
> ```bash
> tail -n 5 /home/nfc/rsync-data-to-storage.log
> tail -n 5 /home/nfc/rsync-storage-to-*.log
> ```
> If the last line isn't one of these "completed successfully" lines
> with a recent date, something went wrong on that run — read the lines
> above it for the actual error. Runs from before 2026-08-13 won't have
> this line even though they succeeded — that's expected, not a sign of
> a problem.

> ⚠️ **Common failure:** a backup job silently doesn't run because the
> computer was turned off, asleep, or restarting at its scheduled time
> (noon or 1pm). Plain cron jobs like these don't "catch up" and run later
> the way some of the computer's own built-in maintenance tasks do — if
> the computer is off at 12:00, that day's local mirror simply doesn't
> happen, with no error or notification anywhere. If you're not sure the
> backups are current, check the log files' timestamps and last line (see
> above):
> ```bash
> ls -l /home/nfc/rsync-*.log
> ```

> ⚠️ **Common failure:** a backup job appears to stop running entirely,
> with no error anywhere. Each job uses a **lock file** — a marker file
> that says "this job is already running," so two copies of the same job
> never run at the same time and collide. If a job crashes partway through
> without cleaning up after itself, that marker file can get left behind,
> and every future run will quietly refuse to start (checking for the
> marker, seeing it, and stopping) instead of showing an error. If a log
> file (see above) hasn't grown in several days, check whether its lock
> file still exists:
> ```bash
> ls -l /tmp/rsync-*.lock
> ```
> Only delete one of these files after confirming (`ps aux | grep rsync`)
> that the job genuinely isn't still running — deleting the marker while
> the job is actually in progress could let two copies run at once.
