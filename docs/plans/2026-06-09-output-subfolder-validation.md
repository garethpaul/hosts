# Output Subfolder Validation

status: completed

## Context

The updater writes generated hosts files under the configured `--output`
subfolder by joining that value with the repository root. Without validation,
absolute paths or parent traversal segments could direct generated output
outside the repository before any optional `/etc/hosts` replacement prompt.

## Completed Scope

- Added `is_safe_output_subfolder()` to accept only relative output subfolders
  without parent traversal.
- Rejected unsafe `--output` values through the CLI parser before computing the
  output path or writing generated hosts data.
- Added side-effect-free baseline coverage for accepted and rejected output
  subfolders.
- Updated README, SECURITY, VISION, and CHANGES with the new guardrail.

## Verification

- `python3 scripts/check-baseline.py`
- `make lint`
- `make test`
- `make build`
- `make check`
- `git diff --check`
