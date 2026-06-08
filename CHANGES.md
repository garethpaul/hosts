# Changes

## 2026-06-08

- Added `make check` and a static baseline for generated hosts data, source metadata, README docs, and updater safety.
- Guarded updater source fetches so only HTTP(S) URLs are accepted and network reads use a timeout.
- Cleaned Python 3 syntax warnings in legacy regex and Windows-path strings.
- Documented generated-file ownership, source provenance, and non-network verification expectations.
