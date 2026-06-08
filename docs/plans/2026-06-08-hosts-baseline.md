# Hosts Baseline Plan

status: completed

## Context

`hosts` is a generated blocklist repository with source metadata in `readmeData.json`, generated hosts output in `hosts`, and legacy StevenBlack-derived update tooling in `updateFile.py`. Local verification should validate checked-in data without fetching remote lists or replacing `/etc/hosts`.

## Objectives

- Add a deterministic `make check` baseline for the generated hosts file and metadata.
- Verify the checked-in hosts count, duplicate handling, source metadata shape, and documentation guardrails.
- Harden update fetches against unsupported URL schemes and unbounded network reads.
- Preserve the generated data without rerunning remote updates in this baseline pass.

## Verification

- `make check`
- `python3 scripts/check-baseline.py`
- `python3 -W error::SyntaxWarning -m py_compile updateFile.py`
- `git diff --check`
