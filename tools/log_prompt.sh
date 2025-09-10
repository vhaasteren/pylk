#!/usr/bin/env bash
set -euo pipefail
PROMPT="${PROMPT:-}"
RESPONSE="${RESPONSE:-}"

if [ -z "$PROMPT" ]; then
  echo "Usage: PROMPT='your prompt' RESPONSE='your response' tools/log_prompt.sh" >&2
  exit 1
fi

LOG_DIR="prompts/log"
mkdir -p "$LOG_DIR"
LOG_FILE="$LOG_DIR/$(date +%Y-%m-%d-%H-%M-%S)-$(echo "$PROMPT" | tr ' ' '-').md"

{
  echo "# Prompt"
  echo
  echo "$PROMPT"
  echo
  echo "## Response"
  echo
  echo "$RESPONSE"
} >> "$LOG_FILE"

echo "Logged to $LOG_FILE"
