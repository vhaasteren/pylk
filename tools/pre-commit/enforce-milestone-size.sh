#!/bin/bash
set -euo pipefail

# Sum added+deleted for staged changes
total=$(git diff --cached --numstat | awk '{add+=$1; del+=$2} END {print (add+del)+0}')

# No staged changes? exit clean
if [ -z "$total" ]; then exit 0; fi

echo "[milestone-size] total changed LOC: $total"

if [ "$total" -ge 300 ] && [ "$total" -le 500 ]; then
  echo "[milestone-size] NOTE: target is ~300 LOC per milestone; consider splitting."
fi

if [ "$total" -gt 500 ]; then
  echo "[milestone-size] ERROR: >500 LOC in one milestone. Please split."
  exit 1
fi
