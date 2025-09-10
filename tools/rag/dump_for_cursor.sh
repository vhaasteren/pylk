#!/usr/bin/env bash
set -euo pipefail
QUERY="${1:-}"
K="${K:-12}"
OUT="${OUT:-.cursor/rag_context.md}"
PROFILE="${PROFILE:-pint}"

if [[ -z "$QUERY" ]]; then
  echo "Usage: $0 'your query' [K=12 OUT=.cursor/rag_context.md PROFILE=pint]" >&2
  exit 1
fi

mkdir -p .cursor
ragcode dump -q "$QUERY" --k "$K" --out "$OUT" --profile "$PROFILE"
echo "Wrote RAG context to $OUT"
