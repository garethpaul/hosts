---
title: Issue 1 Urlopen Timeout
type: fix
status: active
date: 2026-06-08
origin: https://github.com/garethpaul/hosts/issues/1
execution: code
---

# Issue 1 Urlopen Timeout

## Summary

Add a bounded timeout to host-source downloads so a stalled upstream cannot
hang the update process indefinitely.

## Problem Frame

Issue #1 was filed because `updateFile.py` calls `urlopen(url)` without a
timeout in `get_file_by_url`. Python's default is to wait indefinitely.

## Requirements

- R1. `get_file_by_url` must pass a bounded timeout to `urlopen`.
- R2. The timeout value should be named and easy to adjust.
- R3. The existing cross-Python import path should remain intact.
- R4. The PR must reference `https://github.com/garethpaul/hosts/issues/1`.

## Implementation Unit

### U1. Download Timeout

- **Goal:** Define a `URL_TIMEOUT_SECONDS` constant, pass it to `urlopen`, and
  verify the helper sends that timeout.
- **Files:** `updateFile.py`, `updateFile_tests.py`, `scripts/check-baseline.sh`
- **Test Scenarios:** `get_file_by_url` returns decoded bytes from a fake
  response and calls `urlopen` with `URL_TIMEOUT_SECONDS`; source checks confirm
  there is no remaining bare `urlopen(url)`.
- **Verification:** `python3 updateFile_tests.py`, `python3 -m py_compile
  updateFile.py updateFile_tests.py`, `scripts/check-baseline.sh`, and
  `git diff --check`.
