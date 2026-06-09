# Source Data File Handle Cleanup

status: completed

## Context

`updateFile.py` reads local `update.json` source metadata from core data folders
and extensions before composing generated hosts metadata. Those JSON reads
should close file handles promptly, matching the existing response cleanup
guard for remote source fetches.

## Objectives

- Use context managers when reading source metadata JSON files.
- Preserve the existing generated-hosts and source-provenance baseline.
- Add static baseline coverage so future edits keep the file-handle cleanup.
- Document the guard alongside the source fetch cleanup work.

## Verification

- `make check`
- `python3 scripts/check-baseline.py`
- `git diff --check`
