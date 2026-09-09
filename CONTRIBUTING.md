# Contributing to b3dkit

Thank you for considering a contribution. Bug reports, fixes, docs and tests are
all welcome.

If you are unsure where to start, open an issue and describe your idea. Early
feedback prevents rework.

## Development Setup

1. Fork and clone the repository.
2. Create and activate a virtual environment (Python 3.11 or newer).
3. Install with the development extras:

```bash
pip install -e ".[dev]"
```

4. Run the tests:

```bash
pytest --cov
```

The `dev` extra pulls in `ocp_vscode` so the tests that execute each module's
`__main__` demo can run. The library itself never imports it — see
[Dependencies](#dependencies).

## Testing Standards

Tests are required for substantive changes.

- **Coverage floor is 90%**, measured on library code. It is a floor, not a
  target, and there is no ratchet: a change that lowers coverage while deleting
  a test that asserted nothing is an improvement.
- **Every test must be able to fail.** No test should pass without asserting on
  a value the code produced. Tests that exist only to execute lines for coverage
  credit are worse than no test, because they make the coverage number lie.
- **Assert on geometry, not just validity.** `is_valid` is true for nearly any
  closed solid, including one built with every argument ignored. Prefer volume,
  bounding box, solid count, or a raised exception. Where a change should alter
  geometry, assert that it *differs* from the default; where it should not,
  assert that it does not.
- **Bug fixes need a test that fails before the fix.**
- Run `pytest` before opening a pull request.

Two invariants are enforced mechanically rather than by review, because this
project is largely self-reviewed:

- `tests/test_public_api.py` walks `__all__` and checks that every export is
  b3dkit's own, is documented, and follows the Part object contract.
- `tests/test_docs.py` executes every fenced `python` block in `README.md` and
  `docs/`, in document order.

## Documentation Standards

Documentation is part of the change, not a follow-up. Update it in the same
commit.

- **Signatures and arguments are generated** by mkdocstrings from the source.
  Do not hand-write them in `docs/`; a second copy is what let the old
  documentation drift from the code.
- **Prose pages carry what the reference cannot**: what something is for, how to
  choose between two options, print settings, tolerances, troubleshooting.
- **Examples must run.** They are executed by the test suite.
- **State units.** All linear dimensions are in millimeters and all angles in
  degrees; say so for any argument where it could be ambiguous.
- Build the site locally with `mkdocs build --strict`.

## Dependencies

The library imports `build123d` and nothing else. `ocp_vscode` is an optional
`[viewer]` extra used only by the `__main__` demo blocks, so that installing
b3dkit headlessly does not pull a viewer, web server and tessellation stack.

If you add an import to library code, ask whether it belongs in
`dependencies` or in an extra.

## build123d Compatibility

b3dkit declares a minimum build123d version and CI runs one job pinned at
exactly that floor. Please keep it honest: if you use an API added in a newer
release, raise the floor in `pyproject.toml` in the same change. b3dkit 0.1.5
shipped code that could not run against its own advertised minimum, which is
what that CI job exists to prevent.

Do not add an upper bound. Caps propagate into every downstream resolution and
convert a runtime failure into an install failure for everyone.

## Public API

`b3dkit.__all__` is the public API. Anything not listed is an implementation
detail and may change. When adding an export, add it to the module's `__all__`
and to the package's, and give it a docstring — the contract tests check both.

## Versioning

b3dkit is `0.x`, so breaking changes ship in minor releases. Each release is
tagged `vX.Y.Z`, matching the version in `pyproject.toml`; the release workflow
refuses to publish if they disagree.

## Pull Request Checklist

- [ ] Tests added or updated, and each can fail
- [ ] `pytest` passes
- [ ] `ruff check .` and `black --check .` pass
- [ ] Documentation updated in the same commit
- [ ] `mkdocs build --strict` passes if you touched `docs/`
- [ ] PR describes what changed and why
