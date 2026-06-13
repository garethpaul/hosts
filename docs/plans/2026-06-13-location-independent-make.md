# Location-Independent Hosts Verification

status: planned

## Context

The maintained baseline passes from the checkout, but invoking the absolute
Makefile from another directory resolves `scripts/check-baseline.py` relative
to the caller.

## Priority

This is a narrow automation reliability gap. Multi-repository tooling should
be able to load the repository Makefile without first changing directories.

## Scope

1. Derive the repository root from `MAKEFILE_LIST`.
2. Invoke the Python baseline checker through its rooted path.
3. Add completed-plan, external-run, guidance, and hostile-mutation contracts.
4. Preserve updater behavior, provider policy, output containment, atomic
   metadata replacement, dependencies, and workflow files.

## Verification Plan

- Run lint, test, build, and check from the checkout and from a temporary
  directory through the absolute Makefile path.
- Run Python compilation, dependency consistency where available, shell
  syntax, and `git diff --check`.
- Reject root derivation, checker invocation, plan status/evidence, and
  documentation mutations.
- Inspect exact intended paths, secrets, and generated artifacts.

## Risk And Rollback

The change affects verification path resolution only. Rollback restores the
caller-relative recipe; no output files or system hosts state are modified.

## Work Completed

Pending implementation.

## Verification Completed

Pending implementation and validation. Run `make check` before completion.
