# Changes

## 2026-06-10

- Rejected malformed upstream hostnames before they can become generated block
  rules while preserving valid mixed-case and `www` domains.
- Required updater source payload URLs to use HTTPS and migrated the remaining
  plain-HTTP source metadata to working TLS endpoints.
- Added offline baseline coverage proving insecure source URLs are rejected
  before a network request is attempted.

## 2026-06-09

- Validated updater output subfolders so generated hosts writes stay inside the
  repository and reject absolute paths or parent traversal.
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
- Normalized custom exclusion domains to lowercase before compiling regexes so
  they match generated lowercase hostnames.

## 2026-06-08

- Added `make check` and a static baseline for generated hosts data, source metadata, README docs, and updater safety.
- Guarded updater source fetches so only HTTP(S) URLs are accepted and network reads use a timeout.
- Escaped custom exclusion domains before compiling regexes to reduce false-positive overmatching.
- Validated custom exclusions as plain domains before compiling regexes.
- Cleaned Python 3 syntax warnings in legacy regex and Windows-path strings.
- Kept updater syntax validation side-effect free by avoiding bytecode generation in `make check`.
- Documented generated-file ownership, source provenance, and non-network verification expectations.
