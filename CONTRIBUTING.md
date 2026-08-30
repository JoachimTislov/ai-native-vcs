# Contributing

Thanks for contributing to the AI-native VCS project.

## Development model

This repository follows a session-first, spec-driven workflow.

- Start from `SPEC_LIST.md`.
- Create or update the relevant issue before major design work.
- Keep work scoped by domain and contract.
- Validate with the smallest relevant test.
- Record drift or design issues in the spec tracker and issue backlog.

## Issue policy

- Prefer issue labels over title prefixes such as `Future:` or `Parent:`.
- Use the project issue forms in `.github/ISSUE_TEMPLATE`.
- Keep issue titles concise and descriptive.

## Local validation

```bash
python -m pytest tests/test_core.py -q
```

## Release process

- use semantic versioning in `pyproject.toml`
- create the release via the workflow in `.github/workflows/release.yml`
- tag the release with `vX.Y.Z`
