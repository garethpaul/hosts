---
title: "fix: Preserve every generated hosts backup"
type: fix
date: 2026-06-17
status: completed
---

# fix: Preserve every generated hosts backup

## Summary

Allocate each `--backup` file with an exclusive unique name so repeated hosts
publications within the same second cannot overwrite an earlier recovery copy.

## Problem

The atomic publication path currently names backups with second-resolution
timestamps and passes that path to `shutil.copy`. A second publication in the
same second reuses the path and silently replaces the first backup, reducing
the recovery history precisely when an operator is making rapid changes.

## Requirements

- R1. Every requested backup must use an exclusively allocated path in the
  selected output directory.
- R2. Backup names must retain the destination basename and readable timestamp
  while adding collision-safe uniqueness.
- R3. A failed copy must remove only its empty allocated backup artifact,
  preserve the existing destination, and safely discard the unpublished staged
  file.
- R4. Destination mode preservation, staged-file durability, atomic
  `os.replace`, directory sync, output containment, and target preservation
  must remain unchanged.
- R5. Maintained tests must publish twice under a fixed timestamp and prove two
  distinct backups preserve their respective prior destination contents.

## Implementation

1. Add a small backup helper using `tempfile.mkstemp` in the destination
   directory with a timestamped prefix.
2. Close the exclusive descriptor before `shutil.copy`, and remove only the
   allocated path if the copy fails.
3. Extend the portable baseline, documentation, changelog, and completed plan
   evidence with collision and failure-cleanup mutations.

## Verification

- Run the full portable Make gate and external-directory invocation.
- Exercise two same-second publications and assert distinct backup paths and
  ordered preserved contents.
- Simulate backup-copy failure and assert the destination, staged file, and
  pre-existing backups remain intact with no empty artifact.
- Reject mutations that restore deterministic timestamp-only naming, remove
  exclusive allocation, or weaken failure cleanup.

## Scope

This change does not alter source fetching, generated hosts contents,
privileged `/etc/hosts` replacement, DNS flushing, or backup retention policy.

## Work Completed

- Added exclusive, timestamp-prefixed backup allocation in the selected output
  directory and cleanup of the allocated path when copying fails.
- Kept backup creation before durable atomic destination replacement and
  preserved destination permissions, staged-file cleanup, and directory sync.
- Extended portable runtime coverage and operator guidance for collision-safe
  backups without executing live downloads or privileged system changes.

## Verification Completed

- All four Make gates passed: `make lint`, `make test`, `make build`, and
  `make check`.
- The external-directory absolute Makefile check passed from `/tmp`.
- `python3 -m py_compile updateFile.py scripts/check-baseline.py`,
  `python3 updateFile.py --help`, and `git diff --check` passed.
- Two publications under one fixed timestamp produced distinct backups that
  retained their respective prior destination contents.
- Simulated backup-copy failure preserved the destination and existing backups
  while removing only the allocated empty backup and unpublished staged file.
- Six isolated hostile mutations were rejected for exclusive allocation,
  timestamp-prefix preservation, copy-failure cleanup, documentation, plan
  status, and plan evidence.
- No live provider download, privileged hosts replacement, or DNS flush was
  executed.
