# Atomic README Metadata Update

status: completed

## Context

`update_readme_data()` currently opens `readmeData.json` directly in write
mode. A serialization, filesystem, or disk-capacity failure after that open can
truncate the repository's generated provenance metadata even though source
refreshes already preserve their last known-good files atomically.

## Requirements

- R1. Preserve the existing metadata object and update only the selected
  extension key.
- R2. Write replacement JSON to a temporary file in the destination directory,
  flush and sync it, then atomically replace the destination.
- R3. Remove incomplete temporary files and preserve the last known-good
  metadata when serialization or writing fails.
- R4. Keep the implementation dependency-free and compatible with the Python
  3.10, 3.12, and 3.14 matrix.
- R5. Exercise the behavior without source downloads, generated hosts output,
  privileged replacement, or DNS-cache commands.

## Scope Boundaries

- Do not change metadata keys, JSON formatting, or source provenance values.
- Do not change source refresh, target-IP, output containment, or hosts-file
  replacement behavior.
- Do not modify checked-in generated hosts data or `readmeData.json` content.

## Verification

- `make lint`
- `make test`
- `make build`
- `make check`
- `python3 -m py_compile updateFile.py scripts/check-baseline.py`
- `PYTHONDONTWRITEBYTECODE=1 python3 updateFile.py --help`
- `git diff --check`
- Hostile mutations must reject direct destination writes, replacement before
  sync, missing failed-write preservation, stale plan status, and missing
  verification evidence.

## Work Completed

- Serialized generated provenance into a same-directory temporary file and
  flushed and synced it before atomic replacement.
- Preserved destination permissions and removed incomplete temporary files on
  every failed write.
- Added isolated success and partial-serialization fixtures that preserve
  unrelated metadata variants and the last-known-good JSON.
- Documented the atomic generated-metadata guarantee in repository guidance.

## Verification Completed

- All four Make gates passed the dependency-free offline baseline.
- `python3 -m py_compile updateFile.py scripts/check-baseline.py`,
  `PYTHONDONTWRITEBYTECODE=1 python3 updateFile.py --help`, and
  `git diff --check` passed.
- Five isolated hostile mutations were rejected: direct destination writes,
  removal of the metadata sync, missing failed-write cleanup, stale plan
  status, and missing verification evidence.
- No source download, generated repository output, local hosts replacement, or
  DNS-cache flush path was executed.
- Generated-artifact and intended-file secret-pattern scans passed.
