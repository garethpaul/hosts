# AGENTS.md

## Repository purpose

`garethpaul/hosts` maintains a generated hosts-file blocklist and a legacy
Python updater that downloads, normalizes, filters, and optionally installs
source lists.

## Project structure

- `Makefile` - repository verification targets
- `scripts` - baseline checks and helper scripts
- `docs` - plans, notes, and generated README assets

## Development commands

- Install dependencies: no repository-specific install command is documented.
- Full baseline: `make check`
- Lint/static checks: `make lint`
- Tests: `make test`
- Build gate: `make build`
- If a command above skips because a platform toolchain is missing, verify on a machine with that SDK before claiming platform behavior is tested.

## Coding conventions

- Language mix noted in the README: Python (1).
- Prefer dependency-free tests or stdlib checks when legacy packages are unavailable.

## Testing guidance

- The dependency-free baseline executes focused updater helpers without network
  access and validates the checked-in hosts snapshot and metadata.
- Hosted CI runs the baseline on Python 3.10, 3.12, and 3.14.
- Start with the narrowest relevant test or Make target, then run `make check` before handing off if the change is not documentation-only.
- Keep README verification notes in sync when commands, fixtures, or supported toolchains change.

## PR / change guidance

- Keep diffs focused on the requested repository and avoid unrelated modernization or formatting churn.
- Preserve public APIs, sample behavior, file formats, and documented environment variables unless the task explicitly changes them.
- Update tests, README notes, or docs/plans when behavior, security posture, or validation commands change.
- Call out skipped platform validation, legacy toolchain assumptions, and any risky files touched in the final summary.

## Safety and gotchas

- No required secret or credential file was identified in the repository scan. If you add integrations later, keep secrets out of git.
- Treat false positives as security and reliability issues: an overbroad entry can block account recovery, updates, payments, or other important services.
- Source URLs require HTTP(S) schemes and hosts before the updater fetches them.
- `updateFile.py --replace` and DNS flush behavior can affect the local machine's `/etc/hosts`; review generated output and keep backups before privileged replacement.
- See `SECURITY.md` for vulnerability reporting and safe research guidance.
- See `VISION.md` for project direction and contribution guardrails.
- Keep source downloads credential-free, HTTPS-only across redirects, bounded
  to 32 MiB, and protected by the documented timeout.
- Never run updater replacement or DNS-flush options during automated testing;
  those paths can invoke privileged system commands.
- Keep `check.yml` as the sole pinned, read-only workflow without persisted
  checkout credentials.

## Agent workflow

1. Inspect the README, Makefile, manifests, and the files directly related to the request.
2. Make the smallest source or docs change that satisfies the task; avoid generated, vendored, or local-environment files unless required.
3. Run the narrowest useful validation first, then `make check` or the documented package/platform gate when available.
4. If a required SDK, service credential, or external runtime is unavailable, record the skipped command and why.
5. Summarize changed files, commands run, and remaining risks or follow-up validation.
