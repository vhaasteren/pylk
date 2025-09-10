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
if ! ragcode dump -q "$QUERY" --k "$K" --out "$OUT" --profile "$PROFILE"; then
  echo "Error: RAG query failed. Check profile ($PROFILE) and index (~/.ragcode/indexes/$PROFILE)." >&2
  echo "Try: ragcode index --profile pint --incremental" >&2
  exit 1
fi
echo "Wrote RAG context to $OUT"
