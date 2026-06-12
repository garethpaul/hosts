# Bound Source Network Inputs

status: completed

## Context

Initial source URLs used HTTPS and a timeout, but malformed authorities could
pass a nonempty-netloc check, redirects could leave the HTTPS boundary, and
response bodies were read without a memory limit.

## Completed Scope

- Require credential-free HTTPS URLs with valid DNS hostnames and valid ports.
- Reject IP literals, whitespace, userinfo, malformed DNS labels, and invalid
  authorities before opening a connection.
- Reject redirects that leave the same validated HTTPS URL policy.
- Bound each source response read to 32 MiB and close oversized responses.
- Keep the existing 30-second socket timeout and response cleanup.

## Verification

- `make check`
- `python3 -m py_compile updateFile.py scripts/check-baseline.py`
- `git diff --check`
- Hostile network mutations restoring netloc-only validation, redirect
  downgrades, or unbounded reads must fail.
