---
title: "fix: Preserve every generated hosts backup"
type: fix
date: 2026-06-17
status: planned
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
- R3. A failed copy must remove only its empty allocated backup artifact and
  leave the existing destination and staged publication intact.
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
