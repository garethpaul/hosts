# Target IP Validation

status: completed

## Context

The `--ip` command-line value is copied directly into every normalized hosts
rule. It is not currently validated before source discovery, optional network
refresh, or output creation.

A malformed value containing whitespace or a newline can corrupt generated
hosts syntax or inject additional output lines. Hostnames and out-of-range
numeric addresses are also accepted even though the option promises an IP
address.

## Priority

Generated hosts files affect name resolution and can be installed with elevated
privileges. User-controlled target addresses must be validated before any side
effect or generated-data mutation.

## Requirements

- R1. Accept valid IPv4 and IPv6 literals for `--ip`.
- R2. Reject empty values, surrounding/internal whitespace, hostnames,
  out-of-range IPv4 octets, malformed IPv6, and newline injection.
- R3. Run validation immediately after argument parsing and before source
  discovery, source refresh, output removal, or file generation.
- R4. Report invalid values through `argparse` without echoing unsafe content.
- R5. Preserve the default `0.0.0.0`, normalization behavior, replacement
  prompts, and privileged operations for valid input.
- R6. Add dependency-free offline helper tests and a source-order contract.

## Implementation Units

### U1. Validate target addresses

- **Files:** `updateFile.py`
- Add a strict socket-backed literal validator and call `parser.error` before
  settings or filesystem/network work.

### U2. Extend deterministic verification

- **Files:** `scripts/check-baseline.py`
- Exercise accepted and rejected address forms and enforce pre-side-effect call
  ordering.

### U3. Document the generated-data boundary

- **Files:** `README.md`, `SECURITY.md`, `VISION.md`, `CHANGES.md`
- Record strict target-IP validation and output-injection prevention.

## Scope Boundaries

- Do not run source downloads, `--replace`, or DNS-flush operations in tests.
- Do not alter source URL policy, generated hostnames, exclusions, or checked-in
  hosts data.
- Do not normalize user input into a different address representation.

## Verification

- `make lint`
- `make test`
- `make build`
- `make check`
- `python3 -m py_compile updateFile.py scripts/check-baseline.py`
- `PYTHONDONTWRITEBYTECODE=1 python3 updateFile.py --help`
- `git diff --check`
- Hostile mutations removing IPv4, IPv6, whitespace, parser-order, plan status,
  or verification evidence must be rejected.

## Work Completed

- Added strict IPv4/IPv6 literal validation using `socket.inet_pton`.
- Rejected empty, hostname, malformed, whitespace, out-of-range, and injected
  target values before settings, source discovery, or output work.
- Added dependency-free offline accepted/rejected fixtures and source-order
  enforcement.
- Updated README, security, vision, and change documentation.

## Verification Completed

- All four Make gates passed locally.
- `python3 -m py_compile updateFile.py scripts/check-baseline.py`,
  `PYTHONDONTWRITEBYTECODE=1 python3 updateFile.py --help`, and
  `git diff --check` passed.
- Seven isolated hostile mutations were rejected: IPv4 and IPv6 family removal,
  whitespace weakening, validation moved after settings, parser rejection
  removal, stale plan status, and missing verification evidence.
