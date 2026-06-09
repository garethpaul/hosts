# Changes

## 2026-06-09

- Closed updater source fetch response objects after reads while preserving
  HTTP(S)-only URL validation and the existing network timeout.
- Closed source metadata file handles while reading update JSON data, with
  baseline coverage for malformed metadata parse failures.

## 2026-06-08

- Added `make check` and a static baseline for generated hosts data, source metadata, README docs, and updater safety.
- Guarded updater source fetches so only HTTP(S) URLs are accepted and network reads use a timeout.
- Escaped custom exclusion domains before compiling regexes to reduce false-positive overmatching.
- Validated custom exclusions as plain domains before compiling regexes.
- Cleaned Python 3 syntax warnings in legacy regex and Windows-path strings.
- Kept updater syntax validation side-effect free by avoiding bytecode generation in `make check`.
- Documented generated-file ownership, source provenance, and non-network verification expectations.
