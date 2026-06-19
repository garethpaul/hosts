# Network Error Redaction

status: completed

## Context

`update_all_sources()` now logs only a source directory, but
`get_file_by_url()` still interpolates caught exception text. A valid HTTPS
source may include a sensitive query token, and network exceptions can include
the full requested URL. That path can disclose query credentials even though
userinfo-bearing URLs are rejected before fetching.

## Priority

Close the remaining log-exposure path without changing fetch, redirect,
timeout, response-size, decoding, or atomic replacement behavior.

## Scope

1. Replace exception-detail logging in `get_file_by_url()` with one generic
   source-fetch failure message.
2. Add an offline regression using a valid token-bearing HTTPS URL and an
   exception whose text echoes that URL.
3. Prove the token, URL, and exception detail are absent while failure remains
   visible and the response path returns `None`.
4. Add mutation-sensitive checker and completed-plan contracts.
5. Synchronize README, SECURITY, VISION, CHANGES, and AGENTS guidance.

## Non-Goals

- Removing query strings from valid source URLs.
- Changing source URL validation, HTTPS redirects, download limits, timeouts,
  decoding, cached files, output paths, README metadata, or privileged hosts
  replacement.
- Adding live network tests.

## Verification Plan

- Run the focused baseline checker and all four Make gates from the root.
- Run the absolute Makefile check from an external directory.
- Compile Python sources without retaining bytecode.
- Reject exception-detail restoration, regression removal, generic-message
  removal, and plan-evidence drift mutations.
- Audit the exact diff, generated artifacts, modes, and credential-shaped
  additions before committing.
- Capture one bounded exact-head hosted and security snapshot after push.

## Work Completed

- Replaced interpolated source-fetch exception output with one generic failure
  message while preserving the existing `None` return path.
- Added executable offline coverage proving a valid query-bearing HTTPS URL is
  fetched but its URL, token, and exception detail are not logged on failure.
- Added static contracts for the generic message, checker invocation, completed
  plan evidence, and synchronized project guidance.
- Updated README, SECURITY, VISION, CHANGES, and AGENTS guidance to cover the
  remaining exception-redaction boundary.

## Verification Completed

- All four Make gates (`make check`, `make lint`, `make test`, and `make build`)
  passed in an isolated completed-plan fixture.
- The absolute Makefile check passed from an external directory.
- `python3 -m py_compile updateFile.py scripts/check-baseline.py` passed with
  bytecode redirected outside the repository.
- `python3 updateFile.py --help` and the focused source-fetch redaction
  regression passed.
- Four isolated hostile mutations were rejected: exception-detail restoration,
  regression invocation removal, generic-message removal, and plan-evidence
  drift.
- `git diff --check` and the final artifact, mode, and credential-shaped diff
  audits passed before commit.
