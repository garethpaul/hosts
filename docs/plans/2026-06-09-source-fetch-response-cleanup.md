# Hosts Source Fetch Response Cleanup

status: completed

## Context

`updateFile.py` fetches remote host source data with `urlopen`. The helper
validated HTTP(S) URL schemes and used a timeout, but it did not close response
objects after reading data.

## Objectives

- Preserve HTTP(S)-only source URL validation.
- Preserve the 30-second source fetch timeout.
- Close response objects after reading source data.
- Add side-effect-free baseline coverage with a fake `urlopen` response.

## Verification

- `make check`
- `python3 scripts/check-baseline.py`
- `git diff --check`
