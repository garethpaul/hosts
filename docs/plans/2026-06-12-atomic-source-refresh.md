# Atomic Source Refresh

status: completed

## Context

`update_all_sources()` opens each cached source `hosts` file directly in write
mode. If encoding, filesystem, or disk-capacity errors occur during the write,
the previous source data has already been truncated and the updater continues
after logging the failure. A transient refresh failure can therefore discard
the last known-good input used to generate the combined hosts file.

## Completed Scope

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

## Work Completed

- Wrote refreshed source data to a same-directory temporary file, flushed and
  synced it, and atomically replaced the cached destination only after a
  complete write.
- Preserved the last known-good cached hosts file and removed incomplete
  temporary files on refresh failure.
- Added dependency-free success and failure fixtures plus maintenance
  documentation for the atomic refresh guarantee.

## Verification Completed

- All four Make gates, `python3 -m py_compile updateFile.py scripts/check-baseline.py`,
  and `git diff --check` passed locally.
- Implementation push run `27394221497` and pull-request run `27394225763`
  passed at commit `24971bab959ef78830c7aa2dcb101ee323c01771`.
- Post-merge push run `27394241606` and CodeQL setup run `27402322510` passed
  at default-branch merge commit `4686938e9a01d89e566af2e7a03c9f90f1cb1f15`.
- Mutations restoring direct destination writes or removing temporary-file
  cleanup were rejected by the baseline.
