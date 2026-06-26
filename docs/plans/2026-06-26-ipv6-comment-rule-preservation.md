---
title: "fix: Preserve rules with IPv6 text in comments"
type: fix
date: 2026-06-26
status: completed
---

# fix: Preserve rules with IPv6 text in comments

## Context

The parser discarded any source line containing raw `::1`, so a valid IPv4
block rule was lost when only its comment mentioned IPv6 loopback. Removing
that prefilter also exposed source newlines retained inside comments.

## Decision

Let field parsing reject non-IPv4 source records and strip comment payloads
before rebuilding one normalized line. Real `::1 localhost` records remain
excluded without treating comment text as an address field.

## Alternatives

- Search only before `#`: rejected because it duplicates field parsing.
- Special-case comment wording: rejected because comments are arbitrary.
- Add IPv6 source-rule support: deferred as a separate compatibility change.

## Verification Completed

- The regression failed with empty output before implementation.
- The focused regression and complete updater suite pass after implementation.
- An isolated restoration of the raw substring prefilter is rejected.
- Full Make aliases and diff hygiene pass before delivery.

## Boundary

No network refresh, privileged replacement, or DNS flush is exercised or
changed by this parser-only fix.
