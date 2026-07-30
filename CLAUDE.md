# Project Wiki

Documentation hub for [PROJECT NAME] — covers the overall workflow, setup, and links
out to the individual repos that make up the project.

## Purpose

This repo is the map, not a mirror. It explains how the pieces (repo-a, repo-b, repo-c, ...)
fit together and how to get a working environment set up. Implementation details stay
in each repo's own README; don't duplicate them here — link out instead.

## Structure

```
docs/
├── overview.md            # what the project is, how the repos relate
├── setup/
│   ├── environment.md      # shared env/dependencies
│   ├── repo-a-setup.md
│   └── repo-b-setup.md
├── workflow.md              # end-to-end pipeline, data/control flow between repos
├── troubleshooting.md
└── protocols/                # lab-specific step-by-step instructions, if any
```

Rendered as a static site via MkDocs Material (or browsed as plain Markdown on GitHub
if no site is set up yet).

## Related repos

- `your-org/repo-a` — [one-line description]
- `your-org/repo-b` — [one-line description]
- `your-org/repo-c` — [one-line description]

## Conventions

- One topic per file. Split rather than let a page grow past ~1 screen of scrolling.
- Use Mermaid for pipeline/workflow diagrams (renders natively on GitHub and in MkDocs Material).
- Every setup doc should be copy-paste runnable — assume a new lab member with zero context.
- Cross-link with relative paths (`[setup](setup/repo-a-setup.md)`), not hardcoded URLs.
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
- Live site: `https://your-org.github.io/project-wiki` (update once repo is named/created).
- First-time setup: enable Pages in repo Settings → Pages → Source: "GitHub Actions".
- ⚠️ **Common failure:** page doesn't appear on the site — usually means it's missing from
  the `nav:` list in `mkdocs.yml`, not a build error. Check there first.
- ⚠️ **Common failure:** Action runs but site doesn't update — check the Actions tab for a
  failed build before assuming it's a caching issue.

## When editing

- Prefer editing/splitting existing docs over adding new top-level files.
- If a setup step changes in one of the code repos, update the corresponding page here
  in the same session — don't let docs drift.
- Flag (don't silently fix) any instructions that look outdated or that you can't verify.
