# Atomic README Metadata Update

status: planned

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
