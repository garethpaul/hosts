# Atomic Source Refresh

status: planned

## Context

`update_all_sources()` opens each cached source `hosts` file directly in write
mode. If encoding, filesystem, or disk-capacity errors occur during the write,
the previous source data has already been truncated and the updater continues
after logging the failure. A transient refresh failure can therefore discard
the last known-good input used to generate the combined hosts file.

## Scope

- Write refreshed source data to a temporary file in the destination directory.
- Flush and sync the completed temporary file before atomically replacing the
  cached source `hosts` file.
- Remove incomplete temporary files on every failed refresh while preserving
  the previous destination file.
- Add dependency-free regression coverage for successful replacement and
  failed-write cleanup without network access.
- Document the last-known-good preservation guarantee in repository guidance.

## Verification

- `python3 scripts/check-baseline.py`
- `make check`
- `python3 -m py_compile updateFile.py scripts/check-baseline.py`
- `git diff --check`
- Mutations that restore direct destination writes or skip temporary-file
  cleanup must fail the baseline.
