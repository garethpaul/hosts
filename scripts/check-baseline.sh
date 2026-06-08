#!/usr/bin/env sh
set -eu

ROOT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)

if grep -Fq "urlopen(url)" "$ROOT_DIR/updateFile.py"; then
  printf '%s\n' "updateFile.py must not call urlopen(url) without a timeout." >&2
  exit 1
fi

grep -Fq "URL_TIMEOUT_SECONDS = 10" "$ROOT_DIR/updateFile.py"
grep -Fq "urlopen(url, timeout=URL_TIMEOUT_SECONDS)" "$ROOT_DIR/updateFile.py"

printf '%s\n' "hosts urlopen timeout baseline checks passed."
