# OptoFly Ecosystem Wiki

Documentation hub for the OptoFly project — covers the overall workflow, setup, and
consolidates docs from the individual repos that make up the project.

## Purpose

This repo is a consolidated wiki, not just a map. `docs/overview.md`, `workflow.md`,
`troubleshooting.md`, and `setup/*.md` are hand-written here and explain how the
pieces fit together. Everything under `docs/repos/**` is pulled in automatically at
build/preview time by `scripts/sync_repo_docs.py` from each component repo's own
docs — it is never hand-edited here and never committed (see `.gitignore`). If a
component repo's docs are wrong or out of date, fix them in that repo, not here;
the next build picks up the fix automatically.

## Structure

```
docs/
├── index.md                # site home page
├── overview.md            # what the project is, how the repos relate
├── setup/
│   ├── environment.md      # shared env/dependencies
│   ├── optofly-setup.md
│   ├── basler-charuco-calibrator-setup.md
│   ├── liquid-lens-calibration-setup.md
│   └── optotune-lens-setup.md
├── workflow.md              # end-to-end pipeline, data/control flow between repos
├── troubleshooting.md
└── repos/                 # auto-synced component repo docs (never hand-edited, see .gitignore)
```

Rendered as a static site via MkDocs Material. The hand-written pages
(`overview.md`, `workflow.md`, `troubleshooting.md`, `setup/*.md`) are
readable as plain Markdown on GitHub, but everything under `docs/repos/**`
only exists after a build (see Purpose above) — those links 404 on GitHub
itself. Use the built/served site, not the GitHub file browser, to read
component docs.

## Related repos

- [`mpinb/optofly`](https://github.com/mpinb/optofly) — the main real-time tracking and closed-loop optogenetic stimulation pipeline
- [`mpinb/basler-charuco-calibrator`](https://github.com/mpinb/basler-charuco-calibrator) — Basler camera intrinsic calibration
- [`mpinb/liquid-lens-calibration`](https://github.com/mpinb/liquid-lens-calibration) — builds the liquid lens's z → diopter lookup table
- [`mpinb/optotune-lens`](https://github.com/mpinb/optotune-lens) — Python driver library for the Optotune liquid lens hardware

## Conventions

- One topic per file. Split rather than let a page grow past ~1 screen of scrolling.
- Use Mermaid for pipeline/workflow diagrams (renders natively on GitHub and in MkDocs Material).
- Every setup doc should be copy-paste runnable — assume a new lab member with zero context.
- Cross-link with relative paths (`[setup](setup/optofly-setup.md)`), not hardcoded URLs.
- Keep `overview.md` and `workflow.md` as the entry points; everything else hangs off them.

## Writing style — audience is not tech-savvy

Assume the reader has never used the command line before and may not know what a
"repo," "environment," or "dependency" means unless it's explained on first use.

- Write short sentences. One instruction per step, numbered.
- Define jargon inline the first time it appears, or link to a glossary entry — don't assume it's known.
- Never assume a command "obviously" worked. State what the user should see if it succeeded,
  and what it looks like if it didn't.
- Prefer showing exact commands to copy-paste over describing what to do in prose.
- Avoid abbreviations, acronyms, or internal shorthand without spelling them out at least once.

## Mark fail points

For every setup or workflow doc, explicitly call out steps that commonly break, using a
consistent format, e.g.:

> ⚠️ **Common failure:** [what goes wrong] — [how to recognize it] — [how to fix it]

Things to flag this way: version mismatches, missing credentials/permissions, steps that
depend on a previous step finishing correctly, platform-specific quirks (Mac vs Windows vs Linux),
and anything that fails silently instead of throwing a clear error.

## Publishing (GitHub Pages via MkDocs Material)

The site builds from `docs/` using MkDocs Material and deploys automatically to
GitHub Pages on every push to `main` via `.github/workflows/deploy-docs.yml`.

- Config lives in `mkdocs.yml` at repo root — nav structure must be kept in sync with
  any new/renamed files in `docs/`, or they won't show up in the sidebar.
- Local preview: `pip install mkdocs-material` then `mkdocs serve` (site at `localhost:8000`).
- Live site: `https://mpinb.github.io/optofly-docs/`.
- First-time setup: enable Pages in repo Settings → Pages → Source: "Deploy
  from a branch", then select the `gh-pages` branch and `/ (root)`. The
  `gh-pages` branch is created automatically the first time the deploy
  workflow runs — if it isn't in the branch dropdown yet, push to `main`
  once first, wait for the Action to finish, then check again.
- ⚠️ **Common failure:** page doesn't appear on the site — usually means it's missing from
  the `nav:` list in `mkdocs.yml`, not a build error. Check there first.
- ⚠️ **Common failure:** Action runs but site doesn't update — check the Actions tab for a
  failed build before assuming it's a caching issue.

## When editing

- Prefer editing/splitting existing docs over adding new top-level files.
- If a setup step changes in one of the code repos, update the corresponding page here
  in the same session — don't let docs drift.
- Flag (don't silently fix) any instructions that look outdated or that you can't verify.
