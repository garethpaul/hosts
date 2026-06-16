# Publish Generated Hosts Atomically

Status: Completed

## Problem

`main()` removes or backs up the selected hosts output before generation, and
`remove_dups_and_excl()` opens the destination directly with truncation. A
decode, normalization, header, flush, or write failure after cleanup can leave
the selected output missing or partially written even though the previous file
was valid.

## Priorities

1. P0: Preserve the last good selected hosts output until a complete new file
   is durable and ready to publish.
2. P0: Keep backup behavior adjacent to the selected destination and make the
   replacement atomic on the destination filesystem.
3. P1: Preserve root/alternate output selection, generated contents,
   privileged copy prompts, and the existing offline validation boundary.

## Requirements

1. Generation must write to a temporary file created inside the selected
   output directory rather than truncating the destination.
2. The temporary output must be flushed and synced before one atomic
   replacement of the selected hosts path.
3. Any handled generation or publication failure before replacement must leave
   an existing selected output byte-for-byte unchanged and remove only the
   owned temporary file.
4. `--backup` must copy the existing selected output beside that destination
   only after generation succeeds and immediately before replacement.
5. Existing destination permissions must be preserved; a first publication
   must use the maintained default mode.
6. Privileged `/etc/hosts` replacement must read from the published selected
   output path, not the now-moved temporary filename.
7. Root and alternate output behavior, symlink containment, generated content,
   README metadata, source fetching, DNS flushing, and prompt semantics must
   otherwise remain unchanged.
8. Portable runtime checks, guidance, and this plan must record truthful
   verification without live downloads or privileged host replacement.

## Implementation Units

### U1. Durable staged output

**File:** `updateFile.py`

Create the generated file in the selected output directory with an owned
temporary name. Flush, sync, and apply the destination mode before publication.
Keep cleanup scoped to the unpublished temporary file.

### U2. Atomic publication and backup

**File:** `updateFile.py`

Replace pre-generation deletion with a publication helper that optionally
backs up the existing selected target, atomically replaces it, syncs the parent
directory when supported, and returns the published path for privileged copy.

### U3. Failure-sensitive contracts

**File:** `scripts/check-baseline.py`

Exercise successful root and alternate publication, backup placement,
permission preservation, first publication, generation failure, replacement
failure, temporary cleanup, and published-path privileged-copy ownership.

### U4. Maintained evidence

**Files:** `AGENTS.md`, `README.md`, `SECURITY.md`, `VISION.md`, `CHANGES.md`, and
this plan.

Document last-good-output preservation and the limits of process-crash,
filesystem, live-download, and privileged replacement validation.

## Test Scenarios

- A complete generated file atomically replaces the selected root output.
- Alternate output publication leaves the root hosts file untouched.
- Backup mode copies the old selected output beside it before replacement.
- Existing destination mode survives replacement; first publication uses
  `0644`.
- A generation exception leaves an existing destination unchanged and removes
  the unpublished temporary file.
- A replacement exception leaves the existing destination unchanged and
  removes the unpublished temporary file while retaining any requested backup.
- Privileged replacement receives the final selected output path.
- Removing staged output, sync, atomic replacement, failure preservation,
  backup ordering, path ownership, guidance, or completed evidence fails the
  portable gate.

## Scope Boundaries

- Do not change source download, URL validation, rule normalization,
  exclusions, generated header content, README metadata schema, DNS flushing,
  or prompt decisions.
- Do not run live provider downloads, write `/etc/hosts`, flush DNS caches, or
  claim process-crash/power-loss recovery beyond same-filesystem atomic replace.
- Do not edit generated hosts data, source metadata, workflows, dependencies,
  or lockfiles.

## Verification

- Run all four Make gates and the absolute Makefile from `/tmp`.
- Compile both Python entry points and run `updateFile.py --help` with bytecode
  disabled.
- Reject isolated hostile mutations for staging, fsync, atomic replacement,
  failure preservation, backup ordering, permission mode, published-path copy,
  guidance, and plan status.
- Audit the exact diff, generated artifacts/data, workflow/dependency drift,
  secrets, conflict markers, and whitespace before commit.

## Verification Completed

- All four Make gates passed the exact candidate and live implementation.
- The absolute Makefile passed from `/tmp`.
- `python3 -m py_compile updateFile.py scripts/check-baseline.py`,
  `PYTHONDONTWRITEBYTECODE=1 python3 updateFile.py --help`, and
  `git diff --check` passed.
- Ten isolated hostile mutations were rejected for destination-local staging,
  staged-file fsync, atomic replacement, prior-output preservation, backup
  ordering, permission preservation, published-path privileged copy,
  directory sync, guidance, and plan status; hostile mutations were rejected
  without weakening the checker.
- The exact intended-path, generated-artifact/data, workflow/dependency drift,
  conflict-marker, whitespace, and changed-line audits passed. The changed-line credential scan passed.
- No live provider download, privileged hosts replacement, or DNS flush was executed.
- Handled failures before replacement preserve the prior output. Process
  termination, power loss, kernel/filesystem failure, and failures after the
  atomic replacement remain outside the verified guarantee.
