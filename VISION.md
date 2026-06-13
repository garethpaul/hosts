## Hosts Vision

This document explains the current state and direction of the project.
Project overview and developer docs: [`README.md`](README.md)

Hosts is a blocklist project for ads, distractions, tracking, malware, and other
unwanted domains using generated hosts data from multiple third-party sources.

The repository is useful as a curated hosts-file aggregation with source
metadata, alternates, and update tooling. Source metadata lives in
[`readmeData.json`](readmeData.json).

The goal is to keep blocklists useful, transparent, and auditable so users can
understand where entries came from and how to report issues.

The current focus is:

Priority:

- Preserve source provenance for every included list
- Keep generated hosts data and README metadata aligned
- Avoid silently adding sources with unclear ownership or issue paths
- Treat false positives as real user-impacting defects
- Reject malformed upstream DNS labels before generating blocking rules
- Keep `scripts/check-baseline.py` passing for hosts syntax, generated counts,
  duplicate scope, JSON metadata, updater syntax, and custom exclusion escaping
- Keep custom exclusion inputs limited to plain domains before regex compilation
- Normalize custom exclusions to lowercase before matching generated hostnames
- Ensure source URLs use HTTPS and include hosts before the updater fetches them
- Keep output subfolders inside the repository before generated hosts writes
- Keep `make lint`, `make test`, `make build`, and `make check` available as
  local verification gates
- Keep GitHub Actions running the no-network `make check` baseline
- Keep source redirects HTTPS-only and source responses bounded to 32 MiB
- Validate `--ip` as a strict IPv4 or IPv6 literal before source or output work

Next priorities:

- Track source freshness, availability, and issue URLs
- Add clear guidance for reporting false positives or source-level problems

Contribution rules:

- One PR = one focused source, generation, validation, or documentation change.
- Keep source URLs, home URLs, and issue links accurate.
- Explain additions/removals of blocklist sources.
- Verify generated hosts output before pushing data changes.

## Security And Reliability

Canonical security policy and reporting:

- [`SECURITY.md`](SECURITY.md)

Hosts files can block important services or fail to block harmful domains if
source data is wrong. Changes should prioritize provenance, reproducibility, and
clear rollback paths.

Do not add sources that require private credentials or collect user browsing
behavior.

Current baseline: `make lint`, `make test`, `make build`, and `make check` run
`scripts/check-baseline.py`, which validates the checked-in hosts snapshot,
metadata JSON, duplicate handling, generated rule count, and legacy updater
syntax without fetching remote source lists or replacing the local `/etc/hosts`
file. The updater guardrails also cover HTTPS-only source fetches, fetch
timeouts, response cleanup, source URLs use HTTPS and include hosts, and source metadata file handles.
Source authorities reject credentials, IP literals, malformed ports, and
invalid DNS labels before network access; redirects remain inside that policy.
Source refreshes sync a same-directory temporary file before atomic replacement,
preserving the last known-good source and cleaning up partial writes on failure.
Output subfolders are constrained to relative paths within the repository.
Custom exclusions are normalized to lowercase before matching generated hosts.

## What We Will Not Merge (For Now)

- Opaque blocklist sources with no provenance
- Generated data updates without source metadata review
- Tracking or telemetry about user browsing
- Broad category changes without false-positive consideration

This list is a roadmap guardrail, not a permanent rule.
Strong user demand and strong technical rationale can change it.
