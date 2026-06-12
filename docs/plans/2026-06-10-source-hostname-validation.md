# Source Hostname Validation

status: completed

## Context

The source rule parser extracted hostnames with a permissive character class
that accepted underscores, empty labels, and leading or trailing hyphens. Those
malformed names could become generated blocking rules, increasing false-positive
and platform-specific resolver behavior.

## Completed Scope

- Added source-hostname validation for DNS label boundaries, lengths, and
  characters.
- Preserved valid mixed-case normalization and ordinary `www` hostnames.
- Rejected malformed upstream names before writing normalized rules.
- Added dependency-free characterization checks and maintenance documentation.

## Verification

- `make lint`
- `make test`
- `make build`
- `make check`
- `git diff --check`
