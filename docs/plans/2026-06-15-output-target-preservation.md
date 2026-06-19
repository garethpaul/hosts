# Preserve Alternate Output Targets

status: completed

## Context

`main()` validates and constructs `settings["outputpath"]`, but
`remove_old_hosts_file()` always removes `BASEDIR_PATH/hosts`. Running with an
alternate `--output` therefore deletes or backs up the repository-root hosts
file even though generation writes to the selected subfolder.

## Requirements

- R1. Cleanup and backup must operate on the exact hosts path selected by
  `settings["outputpath"]` and `settings["hostfilename"]`.
- R2. Generating into an alternate output directory must preserve the
  repository-root `hosts` file byte-for-byte.
- R3. `--backup` must back up the selected output file beside that file and
  must not create a root backup for an alternate output.
- R4. Default root generation must retain its existing cleanup and backup
  behavior.
- R5. A missing selected output file must remain a valid first-generation
  case without requiring placeholder creation before output-directory setup.
- R6. Add mutation-sensitive runtime, source, guidance, and completed-plan
  contracts without exercising live downloads or privileged replacement.

## Implementation Units

### U1. Selected-target cleanup

- **File:** `updateFile.py`
- Pass the selected hosts path from `main()` into cleanup.
- Remove or back up only an existing selected target, leaving first-generation
  directory and file creation to the existing output writer.

### U2. Regression contracts

- **File:** `scripts/check-baseline.py`
- Exercise root, alternate, backup, and missing-target cases in isolated
  temporary directories.
- Require the selected-target call site and reject fallback to an implicit
  repository-root cleanup target.

### U3. Maintenance evidence

- **Files:** `AGENTS.md`, `README.md`, `SECURITY.md`, `VISION.md`, `CHANGES.md`
- Record that alternate output generation must not mutate root hosts data.

## Scope Boundaries

- Do not change output containment, hostname/IP normalization, source fetch,
  generated hosts contents, README metadata, privileged replacement, or DNS
  flushing.
- Do not run live source downloads, replace `/etc/hosts`, or flush DNS caches.
- Do not edit generated hosts data, source metadata, lockfiles, or workflows.

## Verification Plan

- Run all four Make gates and the absolute Makefile from `/tmp`.
- Compile both Python entry points and run `updateFile.py --help` without bytecode
  artifacts.
- Reject mutations that restore implicit root cleanup, remove selected-target
  binding, delete the alternate-output preservation assertion, weaken backup
  placement, remove guidance, or falsify completed plan evidence.
- Audit the exact intended diff, generated artifacts, generated-data and
  workflow exclusions, conflict markers, whitespace, and changed-line
  credential patterns.
- Push a stacked pull request and take one bounded exact-head hosted and
  security-alert snapshot without polling.

## Work Completed

- Bound cleanup and backup to the selected output hosts path.
- Preserved repository-root hosts data during alternate output generation.
- Added isolated root, alternate, backup, and missing-target contracts plus
  synchronized maintenance guidance.

## Verification Completed

- All four Make gates passed on the exact candidate implementation.
- The absolute Makefile passed from `/tmp`.
- `python3 -m py_compile updateFile.py scripts/check-baseline.py`,
  `PYTHONDONTWRITEBYTECODE=1 python3 updateFile.py --help`, and
  `git diff --check` passed.
- Six hostile mutations were rejected across implicit root cleanup,
  selected-target binding, root preservation, backup placement, guidance, and
  plan evidence.
- Exact intended-path, generated-artifact, generated-data/workflow exclusion,
  conflict-marker, whitespace, and changed-line credential scan passed.
- The hosted pull-request and security-alert snapshot is recorded separately
  after push; this plan claims only completed pre-push verification above.
