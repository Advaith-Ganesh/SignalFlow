## What changed and why

<!-- One or two sentences. Link an issue if there is one. -->

## Checklist

- [ ] `pytest -q` passes
- [ ] `ruff check src backend scripts tests` passes
- [ ] `ruff format --check src backend scripts tests` passes
- [ ] `mypy src/signalflow` passes (and `mypy app` from `backend/`, if backend code changed)
- [ ] `cd frontend && npm run lint && npm run build` passes (if frontend code changed)
- [ ] New logic in `src/signalflow/` is covered by a test (see `tests/` for the pattern)
- [ ] Nothing added here presents synthetic/mocked data as real (see `data/README.md`)

## Notes for the reviewer

<!-- Anything a reviewer should know: a tradeoff you made, an alternative you
considered, or a limitation you're aware of but leaving as-is. -->
