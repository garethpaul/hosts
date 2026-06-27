# Location-Independent Hosts Verification

status: completed

## Context

The maintained baseline passes from the checkout, but invoking the absolute
Makefile from another directory resolves `scripts/check-baseline.py` relative
to the caller. GNU Make also splits a loaded absolute Makefile path containing
spaces before the repository root is derived.

## Priority

This is a narrow automation reliability gap. Multi-repository tooling should
be able to load the repository Makefile without first changing directories.

## Scope

1. Derive the repository root from the single loaded Makefile path while preserving spaces.
2. Invoke the Python baseline checker through its rooted path.
3. Add completed-plan, external-run, recursive spaced-path, guidance, and hostile-mutation contracts.
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

- Derived `ROOT` from the sole loaded Makefile and invoked the checker through
  its absolute repository path while rejecting ambiguous Makefile inputs.
- Added a recursive-safe full-baseline regression against a copied checkout
  whose absolute path contains spaces.
- Added rooted-recipe, completed-plan, external-run, and synchronized-guidance
  contracts.
- Preserved updater behavior, generated data, dependencies, and workflows.

## Verification Completed

- Root and external-directory Make gates passed for `lint`, `test`, `build`,
  and `check`; every target exercised the complete generated-data baseline.
- GNU Make 4.2 and 4.4 space-containing absolute Makefile paths passed.
- Preloaded, overridden, additional, and recipe-replacement Makefiles failed closed.
- The root-derivation mutation failed.
- The checker-invocation mutation failed.
- The plan-status mutation failed.
- The plan-evidence mutation failed.
- The documentation mutation failed.
- Python compilation, updater help, shell syntax, dependency-manifest
  inventory, diff hygiene, exact intended-path review, secret scanning, and
  generated-artifact inspection passed. No dependency manifest is tracked.
