#!/bin/bash
set -euo pipefail

if grep -R -nE "^\s*(from|import)\s+pint\b" pylk/widgets 2>/dev/null; then
  echo "ERROR: PINT import found in pylk/widgets"
  exit 1
fi
