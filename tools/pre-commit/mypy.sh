#!/bin/bash
set -euo pipefail

# Run mypy on the pylk package only
cd "$(dirname "$0")/../.."
mypy --explicit-package-bases pylk/
