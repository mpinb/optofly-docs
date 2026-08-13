# OptoFly Ecosystem Wiki

Documentation hub for the OptoFly project. It covers the overall workflow, setup
instructions, and consolidates documentation from the individual repos that make
up the project.

Live site: **https://mpinb.github.io/optofly-docs/**

## What's in here

- `docs/overview.md`, `docs/workflow.md`, `docs/troubleshooting.md`, and
  `docs/setup/*.md` are hand-written in this repo and explain how the pieces of
  the OptoFly ecosystem fit together.
- `docs/repos/**` is pulled in automatically at build/preview time by
  `scripts/sync_repo_docs.py` from each component repo's own docs. It is never
  hand-edited here and is not committed (see `.gitignore`). If a component
  repo's docs are wrong or out of date, fix them in that repo — the next build
  picks up the fix automatically.

## Related repos

- [`mpinb/optofly`](https://github.com/mpinb/optofly) — the main real-time tracking and closed-loop optogenetic stimulation pipeline
- [`mpinb/basler-charuco-calibrator`](https://github.com/mpinb/basler-charuco-calibrator) — Basler camera intrinsic calibration
- [`mpinb/liquid-lens-calibration`](https://github.com/mpinb/liquid-lens-calibration) — builds the liquid lens's z → diopter lookup table
- [`mpinb/optotune-lens`](https://github.com/mpinb/optotune-lens) — Python driver library for the Optotune liquid lens hardware
- [`mpinb/ximea-py`](https://github.com/mpinb/ximea-py) — Python driver library for XIMEA camera hardware
- [`mpinb/braid-opto-power-measure`](https://github.com/mpinb/braid-opto-power-measure) — measures the spatial distribution of optogenetic LED power/irradiance across the arena
- [`mpinb/optofly-analysis`](https://github.com/mpinb/optofly-analysis) — post-hoc analysis of finished `.braidz` recordings: behavior stats, stimulus/optogenetic response, group comparisons

## Local preview

```bash
pip install mkdocs-material
mkdocs serve
```

Then open `http://localhost:8000`.

## Publishing

The site builds from `docs/` using MkDocs Material and deploys automatically to
GitHub Pages on every push to `main` via `.github/workflows/deploy-docs.yml`.

## Contributing

See `CLAUDE.md` for conventions on structure, writing style, and how the
auto-synced `docs/repos/**` content works.

## License

GPLv3 — see [LICENSE](LICENSE).
