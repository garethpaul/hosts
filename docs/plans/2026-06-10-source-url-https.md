# Source URL HTTPS Enforcement

status: completed

## Context

The updater validated source URL schemes and hosts, but still accepted plain
HTTP for downloaded blocklist payloads. Two providers were repeated across 30
generated metadata variants using HTTP even though both resources are
available over HTTPS.

## Completed Scope

- Required `get_file_by_url()` to accept only HTTPS source URLs with hosts.
- Migrated the remaining source payload references to verified HTTPS endpoints.
- Kept informational home and issue links outside the fetch restriction.
- Added side-effect-free baseline coverage proving plain HTTP is rejected
  before `urlopen` is called.
- Extended documentation and metadata validation to preserve the HTTPS rule.

## Verification

- `python3 scripts/check-baseline.py`
- `make lint`
- `make test`
- `make build`
- `make check`
- `git diff --check`
- `curl -L -I --max-time 15 https://someonewhocares.org/hosts/zero/hosts`
- `curl -L -I --max-time 15 https://winhelp2002.mvps.org/hosts.txt`
