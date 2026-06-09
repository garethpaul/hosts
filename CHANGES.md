# Changes

## 2026-06-09

- Added local `make lint`, `make test`, and `make build` gate aliases for the
  static generated-data baseline.
- Required updater source URLs to include HTTP(S) schemes and hosts before
  fetch attempts.
- Closed updater source fetch response objects after reads while preserving
  HTTP(S)-only URL validation and the existing network timeout.
- Closed source metadata file handles while reading update JSON data, with
  baseline coverage for malformed metadata parse failures.
- Closed source output file handles while writing refreshed hosts data, with
  baseline coverage for write failures.

## 2026-06-08

- Added `make check` and a static baseline for generated hosts data, source metadata, README docs, and updater safety.
- Guarded updater source fetches so only HTTP(S) URLs are accepted and network reads use a timeout.
- Escaped custom exclusion domains before compiling regexes to reduce false-positive overmatching.
- Validated custom exclusions as plain domains before compiling regexes.
- Cleaned Python 3 syntax warnings in legacy regex and Windows-path strings.
- Kept updater syntax validation side-effect free by avoiding bytecode generation in `make check`.
- Documented generated-file ownership, source provenance, and non-network verification expectations.
