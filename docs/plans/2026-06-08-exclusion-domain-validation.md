# Hosts Exclusion Domain Validation

status: completed

## Context

`updateFile.py` lets users enter custom domains to exclude from the generated
blocklist. The regex escaping guard prevents metacharacters from becoming active
regular expressions, but the input validator still accepted malformed values
such as URL paths, spaces, wildcard prefixes, or doubled dots.

## Objectives

- Accept plain dotted domains such as `example.com` and `ads.example.co.uk`.
- Continue rejecting `www.` and `http(s)://` inputs with the existing guidance.
- Reject malformed custom exclusions before compiling exclusion regexes.
- Add side-effect-free baseline coverage for accepted and rejected inputs.

## Verification

- `make check`
- `python3 scripts/check-baseline.py`
- `git diff --check`
