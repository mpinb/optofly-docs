# OptoFly Ecosystem Docs — Design

Date: 2026-07-30

## Purpose

`optofly-docs` becomes a consolidated MkDocs Material wiki for the OptoFly project
ecosystem: the main pipeline (`optofly`) plus three calibration/support repos
(`liquid-lens-calibration`, `basler-charuco-calibrator`, `optotune-lens`). It
supersedes the "map, not mirror" philosophy in the original CLAUDE.md scaffold —
that guidance predates this design and is being rewritten as part of it.

Each of the 4 component repos also gets a detailed `CLAUDE.md` (tracked, not
gitignored) with instructions on installing and using Claude Code, so a new
contributor working in any of them has consistent guidance.

## Repos involved

All under the `mpinb` GitHub org, currently private (org owner is being asked
to make them public — see "Known blocker" below), cloned locally under `~/src/`:

| GitHub repo | Local path | Current CLAUDE.md state |
|---|---|---|
| `mpinb/optofly` | `~/src/OptoFly` (branch `docs/sync-with-code`) | Tracked, 2389 words, has unrelated uncommitted edits in progress |
| `mpinb/liquid-lens-calibration` | `~/src/liquid_lens_calibration` | Exists on disk, untracked **and gitignored** |
| `mpinb/basler-charuco-calibrator` | `~/src/basler_charuco_calibrator` | Tracked, but also listed in `.gitignore`; repo has unrelated uncommitted changes (gui.py, configs) |
| `mpinb/optotune-lens` | `~/src/optotune-lens` | Does not exist |

All 4 currently have `origin` → `github.com/elhananby/*`.

## 1. Remote reorganization

Across all 5 repos (the 4 above + `optofly-docs` itself):

- Where `origin` already points at `elhananby/*`: rename that remote to `personal`,
  then add a new `origin` pointing at `mpinb/*`.
- `optofly-docs` has no remote yet: add `origin` → `mpinb/optofly-docs` directly.

This is local git config only — no pushes to the 4 component repos happen until
step 2 produces commits.

## 2. Per-repo CLAUDE.md work

For each of the 4 component repos:

1. Fix tracking issues:
   - `liquid-lens-calibration`: remove `CLAUDE.md` from `.gitignore`, `git add CLAUDE.md`.
   - `basler-charuco-calibrator`: remove the stale `CLAUDE.md` entry from `.gitignore`
     (file is already tracked). Stage only `CLAUDE.md`/`.gitignore` — the repo has
     other unrelated uncommitted changes (`gui.py`, `configs/*.yaml`, a deleted
     `docs/plans/*` file) that must be left untouched.
   - `optofly`: no tracking issue. The repo has unrelated in-progress uncommitted
     edits to `CLAUDE.md` and `docs/architecture.md` (a doc-sync effort already
     underway) — the new section is appended without touching existing content or
     the pending diff.
   - `optotune-lens`: write a new `CLAUDE.md` from scratch covering architecture,
     dev commands, and testing, based on the existing README and code structure.
2. Append an "Installing and Using Claude Code" section to each repo's CLAUDE.md,
   sourced via the `claude-code-guide` agent for accuracy (install methods, auth,
   `/init`, basic usage) rather than from memory.
3. One commit per repo, pushed to the new `mpinb` `origin`, on whatever branch is
   currently checked out (`docs/sync-with-code` for `optofly`, `main` for the rest).

## 3. `optofly-docs` wiki structure

```
docs/
├── index.md
├── overview.md              # what the 4 repos are, how they relate
├── workflow.md               # end-to-end pipeline, cross-repo data/control flow
├── troubleshooting.md        # cross-repo issues only
├── setup/
│   ├── environment.md
│   ├── optofly-setup.md
│   ├── liquid-lens-calibration-setup.md
│   ├── basler-charuco-calibrator-setup.md
│   └── optotune-lens-setup.md
└── repos/                    # populated at build/preview time — gitignored
    ├── optofly/               # mirrors optofly's docs/ (excluding docs/superpowers/)
    ├── liquid-lens-calibration/README.md
    ├── basler-charuco-calibrator/README.md
    └── optotune-lens/README.md
```

- `overview.md`, `workflow.md`, `troubleshooting.md`, and `setup/*` are authored
  directly in this repo, written for a reader with no command-line experience,
  per the existing CLAUDE.md style rules.
- `docs/repos/**` is never committed. It's regenerated before every build/preview
  by `scripts/sync_repo_docs.py`, which the pulled-in content inherits its own
  audience (developer-level) from — no rewriting of source repos' docs.
- `optofly-docs`' own CLAUDE.md "Purpose" section is rewritten to describe this
  consolidated-with-fresh-sync model, replacing "map, not mirror."

## 4. Sync mechanism

`scripts/sync_repo_docs.py`:
- For each of the 4 repos, `git clone --depth 1 https://github.com/mpinb/<repo>.git`
  into a temp dir (plain, unauthenticated — relies on the repos being public).
- Copies the relevant doc files into `docs/repos/<name>/` per the mapping above.
- Runnable both locally (before `mkdocs serve`) and in CI (before `mkdocs build`).

`.github/workflows/deploy-docs.yml`:
1. Checkout `optofly-docs`
2. `pip install mkdocs-material`
3. Run `scripts/sync_repo_docs.py`
4. `mkdocs build`
5. Deploy to GitHub Pages

## Known blocker

The 4 component repos are currently **private**. Unauthenticated clone in CI will
fail until the org owner makes them public — the user is raising this with the
org owner directly. No PAT/secret workaround is being built; the deploy workflow
will simply fail with a clear "repository not found" error until visibility changes.
This blocks a *working* Pages deploy, but not the rest of this work (remotes, the
component repos' CLAUDE.md files, and authoring the wiki content itself all proceed
regardless).

## Out of scope

- Rewriting source repos' own docs to a beginner-friendly style.
- Deep link-rewriting for relative links inside pulled-in markdown (known
  limitation, not addressed in this pass).
- Any change to `optofly`'s in-progress `docs/sync-with-code` branch content
  beyond appending the new CLAUDE.md section.
