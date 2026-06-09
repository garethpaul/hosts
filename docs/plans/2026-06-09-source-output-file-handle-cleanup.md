# Source Output File Handle Cleanup

status: completed

## Context

`update_all_sources()` already closes source metadata files and fetched response
objects, but refreshed source hosts files were opened manually and closed only
after a successful write. A write failure could leave the generated source
output file handle open.

## Completed Scope

- Switched refreshed source hosts writes to a context manager.
- Added a baseline fixture that simulates a source hosts write failure and
  verifies the output file handle still closes.
- Preserved existing source URL validation, response cleanup, and source
  metadata cleanup checks.
- Updated README, SECURITY, VISION, and CHANGES notes for the output cleanup
  guard.

## Verification

- `python3 scripts/check-baseline.py`
- `make check`
- `git diff --check`
