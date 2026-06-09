# Exclusion Domain Case Normalization

status: completed

## Context

Generated hosts entries are normalized to lowercase before duplicate and
exclusion checks. Custom exclusion domains were validated and escaped, but the
regex was compiled from the user-provided casing. An exclusion such as
`Example.COM` would therefore fail to match the generated `example.com` host.

## Completed Scope

- Normalized custom exclusion domains to lowercase before compiling exclusion
  regexes.
- Added a baseline fixture for uppercase custom exclusions matching lowercase
  generated hostnames.
- Preserved regex escaping so dots in user-provided domains still match
  literally.
- Updated README, VISION, and CHANGES to document the normalization guardrail.

## Verification

- `make check`
- `git diff --check`
