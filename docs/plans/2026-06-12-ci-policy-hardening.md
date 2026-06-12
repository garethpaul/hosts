# Harden Hosted Baseline Policy

status: completed

## Context

The prepared workflow ran the offline baseline, but used mutable action tags,
persisted checkout credentials, an unbounded runner label, and substring-only
policy checks.

## Completed Scope

- Pin checkout v6.0.3 and setup-python v6.1.0 by immutable commit.
- Disable persisted checkout credentials and keep read-only permissions.
- Run bounded Ubuntu 24.04 jobs on Python 3.10, 3.12, and 3.14.
- Keep `check.yml` as the only hosted workflow and compare its full contents
  against the canonical local policy.
- Assign repository-wide ownership in `.github/CODEOWNERS`.

## Verification

- `make check`
- `git diff --check`
- Hostile workflow mutations covering mutable actions, credentials,
  permissions, commands, matrix entries, and hidden workflows must fail.
