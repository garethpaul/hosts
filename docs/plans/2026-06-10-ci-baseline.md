# CI Baseline

status: completed

## Context

The portfolio remediation plan calls for lightweight CI on active repos with
passing local checks. This repo already has a no-network static baseline, so CI
can run the same `make check` gate without fetching blocklist sources or
touching the local hosts file.

## Completed Scope

- Added a GitHub Actions workflow for pushes, pull requests, and manual runs.
- Configured CI to run `make check` with Python 3.10, 3.12, and 3.14.
- Pinned actions, disabled persisted checkout credentials, and retained
  repository-wide read-only permissions.
- Extended `scripts/check-baseline.py` and docs so the CI gate remains visible.

## Verification

- `make check`
- `git diff --check`
