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

## At a glance

| Job | Copies | Schedule | Protects against | Status |
|---|---|---|---|---|
| Local mirror | `/mnt/data` → `/mnt/storage` | Daily, 12:00 | The working disk failing, or a finished file being accidentally deleted before it's archived | Working |
| Offsite mirror | `/mnt/storage` → a remote server | Daily, 13:00 | Losing the entire machine (theft, fire, complete hardware failure) | **Broken — see below** |
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

Anyone working directly on `nfc3008` can see the real values by running
`crontab -l` in a terminal.

> ⚠️ **Common failure — this job is currently broken.** Every run ends
> with `Permission denied` in its log
> (`/home/nfc/rsync-storage-to-soma.log`). This is a known, existing issue
> as of 2026-08-13, not something wrong with your setup — it hasn't been
> fixed yet. Until it is, **`/mnt/storage` is the only backup this
> machine's data has** — there is currently no true offsite copy.

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
> and update this page once confirmed.

## Restoring a file

**From the local or offsite mirror** (`/mnt/storage`): these are just
plain folders, so getting a file back is a plain copy:

```bash
cp /mnt/storage/experiments/some_experiment.braidz ~/Desktop/
```

**From the home folder backup**: use `duplicity`'s own restore command,
telling it which backup to read from (`file:///mnt/system_backups`) and
where to put the restored files:

```bash
duplicity restore file:///mnt/system_backups ~/restored_home
```

This creates a new folder, `~/restored_home`, with a full copy of
`/home/nfc` as of the most recent backup — it won't overwrite anything
that's already there. If you need an older version specifically, ask a
labmate for help — `duplicity` supports restoring to a specific date, but
it's easy to get wrong.

## Common failures

> ⚠️ **Common failure:** the offsite mirror is currently broken — see
> above. Check `/home/nfc/rsync-storage-to-soma.log` if you want to
> confirm it's still failing.

> ⚠️ **Common failure:** a backup job silently doesn't run because the
> computer was turned off, asleep, or restarting at its scheduled time
> (noon or 1pm). Plain cron jobs like these don't "catch up" and run later
> the way some of the computer's own built-in maintenance tasks do — if
> the computer is off at 12:00, that day's local mirror simply doesn't
> happen, with no error or notification anywhere. If you're not sure the
> backups are current, check the log files' timestamps:
> ```bash
> ls -l /home/nfc/rsync-data-to-storage.log /home/nfc/rsync-storage-to-soma.log
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
> ls -l /tmp/rsync-data-to-storage.lock /tmp/rsync-storage-to-soma.lock
> ```
> Only delete one of these files after confirming (`ps aux | grep rsync`)
> that the job genuinely isn't still running — deleting the marker while
> the job is actually in progress could let two copies run at once.
