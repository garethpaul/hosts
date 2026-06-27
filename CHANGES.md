# Changes

- Preserved absolute Makefile roots containing spaces and added a recursive-safe full-baseline regression.
- Rejected ambiguous Makefile inputs so later recipes cannot replace verification.

## 2026-06-26 11:41 PDT - P1 - Preserve rules whose comments mention IPv6

- **Summary:** Parse hosts fields before deciding whether a source line is an
  IPv6 loopback record, and normalize retained comments to one output line.
- **Files:** Updated `updateFile.py`, focused parser tests, repository guidance,
  and the implementation plan.
- **Tests:** Added a failing regression for an IPv4 block rule whose comment
  mentions `::1`; the focused and complete updater suites pass after the fix.
- **Findings:** The old raw substring check silently dropped a valid domain;
  removing it also exposed embedded source newlines in preserved comments.
- **Blockers:** No live source refresh or privileged hosts replacement ran.
- **Next action:** Require hosted Python matrices on the exact PR head, attempt
  Codex review once, merge only the green SHA, and verify post-merge CI.

## 2026-06-19

- Preserved every valid hostname alias on multi-host source lines while
  applying exclusions independently to avoid losing unrelated block entries.
- Closed atomic-publication races by copying backups through their exclusively
  allocated descriptors, rejecting symlink destinations, preserving ownership,
  and syncing parent directories after replacement.

## 2026-06-17

- Backup allocation is exclusive, so same-second publications preserve distinct recovery copies.

## 2026-06-16

- Generated hosts outputs preserve the last good file until atomic publication.

## 2026-06-15

- Alternate --output generation removes or backs up only the selected hosts file and leaves the repository-root hosts data unchanged.
- Source fetch exceptions are reported generically without URL, query, or
  exception details.

## 2026-06-14

- Ensured credential-bearing source URLs are never reproduced in refresh logs
  while preserving non-sensitive source-directory context.

## 2026-06-13

- Made every Make verification target derive the checkout root so the
  generated-data baseline works from external directories.
- Rejected output subfolders whose symbolic links resolve outside the
  repository while preserving internal symlink targets.
- Validated `--ip` as a strict IPv4 or IPv6 literal before source discovery or
  output generation, rejecting hostnames, malformed addresses, whitespace, and
  line injection.

## 2026-06-10

- Rejected malformed upstream hostnames before they can become generated block
  rules while preserving valid mixed-case and `www` domains.
- Required updater HTTPS source payload URLs and migrated the remaining
  plain-HTTP source metadata to working TLS endpoints.
- Added offline baseline coverage proving insecure source URLs are rejected
  before a network request is attempted.
- Added GitHub Actions CI that runs the no-network `make check` baseline.
- Rejected credential-bearing, IP-literal, malformed, and downgrade-redirect
  source URLs, and limited each source response to 32 MiB.
- Pinned the read-only Python 3.10/3.12/3.14 workflow, disabled persisted
  checkout credentials, enforced its full shape, and added CODEOWNERS.
- Made source refreshes atomic so failed writes preserve the last known-good
  cached hosts data and remove incomplete temporary files.
- Made `readmeData.json` writes atomic so failed serialization or filesystem
  writes preserve the last-known-good provenance metadata.
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
