# Hosts Exclusion Regex Guard Plan

status: completed

## Context

`updateFile.py` lets users exclude domains from generated blocklists. The
legacy helper compiled user-supplied domain text directly into a regular
expression, so metacharacters such as `.` could match unintended domains and
cause overbroad exclusions.

## Objectives

- Escape user-supplied exclusion domains before compiling regexes.
- Preserve matching for the requested domain and its subdomains.
- Add a no-bytecode baseline check for the exclusion helper behavior.
- Document the false-positive prevention guardrail.

## Work Items

1. Updated `exclude_domain` to use `re.escape(domain)`.
2. Added `check_exclusion_regex_escaping` to the static baseline.
3. Updated README, VISION, CHANGES, and this plan with the exclusion guardrail.

## Verification

- `make check`
- `python3 scripts/check-baseline.py`
- `git diff --check`
