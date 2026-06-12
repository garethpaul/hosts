# Source URL HTTPS Baseline

status: completed

## Context

The portfolio remediation plan calls out active plaintext integrations as a
high-priority risk. The checked-in source metadata still used `http://` fetch
URLs for the someonewhocares.org and MVPS hosts sources even though both exact
paths are available over HTTPS.

## Completed Scope

- Replaced active `readmeData.json` source fetch URLs for someonewhocares.org
  and MVPS with HTTPS URLs.
- Preserved non-fetching homepage and issue metadata as provenance links.
- Extended `scripts/check-baseline.py` so future source fetch URLs must use
  HTTPS.

## Verification

- `curl -L -I --max-time 15 https://someonewhocares.org/hosts/zero/hosts`
- `curl -L -I --max-time 15 https://winhelp2002.mvps.org/hosts.txt`
- `make check`
- `git diff --check`
