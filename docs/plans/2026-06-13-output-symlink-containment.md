# Contain Symlinked Output Paths

status: planned

## Context

The updater rejects absolute `--output` values and parent traversal before
joining the requested subfolder to the repository root. A relative path can
still name an in-repository symbolic link whose target is outside the
repository, allowing the generated `hosts` file to escape the intended output
boundary.

## Requirements

- R1. Existing root and ordinary relative output subfolders must remain valid.
- R2. Relative paths that resolve outside the repository through symbolic links
  must be rejected before directory creation or file writes.
- R3. Symbolic links that resolve to a directory inside the repository must
  remain valid.
- R4. Absolute paths, Windows-style roots, and parent traversal must remain
  rejected.
- R5. Validation must stay dependency-free and compatible with the supported
  Python 3.10, 3.12, and 3.14 matrix.
- R6. Network fetching, generated content, privileged replacement, and DNS
  flushing must remain unchanged and unexercised by tests.

## Scope Boundaries

- Do not fetch source lists or write outside isolated temporary fixtures.
- Do not change source URL, response-size, target-IP, or atomic-refresh policy.
- Do not execute `/etc/hosts` replacement or DNS-cache commands.

## Verification

- `make lint`
- `make test`
- `make build`
- `make check`
- `python3 -m py_compile updateFile.py scripts/check-baseline.py`
- `PYTHONDONTWRITEBYTECODE=1 python3 updateFile.py --help`
- `git diff --check`
- Hostile mutations must reject removal of realpath containment, naive prefix
  matching, acceptance of an escaping symlink, stale plan status, and missing
  verification evidence.

## Work Completed

Pending implementation.

## Verification Completed

Pending implementation and verification.
