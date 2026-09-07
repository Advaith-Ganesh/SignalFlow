# Contributing

SignalFlow is primarily a personal research/portfolio project built around a
single historical event study. It isn't run as a community project with a
roadmap or a maintainer team, but genuine improvements are welcome:

- **Bug reports** — if you find a real defect (a calculation that's wrong,
  a broken link, a test that doesn't actually test what it claims to), please
  open an issue with enough detail to reproduce it.
- **Methodology feedback** — if you think the event-study design, the
  diffusion models, or a hypothesis test has a real flaw, open an issue.
  This project cares more about being statistically honest than about
  defending existing choices.
- **Extensions** — see the Future Improvements section of `README.md` for
  the kind of extension (e.g. a cross-sectional multi-event version) that
  would genuinely add value.

## Before opening a PR

1. Run the checks this project actually uses:
   ```bash
   pytest -q
   ruff check src backend scripts tests
   ruff format --check src backend scripts tests
   mypy src/signalflow
   cd frontend && npm run lint && npm run build
   ```
2. Keep changes to `src/signalflow/` backed by a test — see `tests/` for the
   existing pattern (synthetic data with a known, injected effect, checked
   for correct recovery).
3. Don't add real-looking data that isn't real. See `data/README.md` for how
   this project distinguishes REAL, DERIVED, MODEL OUTPUT, and SYNTHETIC
   data — that distinction is a core design principle here, not a formality.

There's no formal code of conduct beyond: be specific, be honest about what
you tested, and don't submit AI-generated changes you haven't verified
yourself.
