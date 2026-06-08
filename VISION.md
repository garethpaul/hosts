## Hosts Vision

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

Next priorities:

- Document update commands and generated-file ownership
- Add validation for malformed hosts entries and duplicate handling
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

## What We Will Not Merge (For Now)

- Opaque blocklist sources with no provenance
- Generated data updates without source metadata review
- Tracking or telemetry about user browsing
- Broad category changes without false-positive consideration

This list is a roadmap guardrail, not a permanent rule.
Strong user demand and strong technical rationale can change it.
