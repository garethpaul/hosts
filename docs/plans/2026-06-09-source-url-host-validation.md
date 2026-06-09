# Source URL Host Validation

status: completed

## Context

The updater already rejected non-HTTP(S) source URLs, but malformed values such
as `https://` could still reach the fetch path before failing. Source metadata
should provide a concrete host before any network call is attempted.

## Completed Scope

- Required `get_file_by_url()` to reject HTTP(S) URLs without a host.
- Extended source metadata validation so checked-in source URLs must include
  both an HTTP(S) scheme and a host.
- Added baseline coverage proving hostless source URLs are rejected before
  `urlopen`.
- Updated README, SECURITY, VISION, and CHANGES notes for the source URL host
  guard.

## Verification

- `python3 scripts/check-baseline.py`
- `make check`
- `git diff --check`
