#!/usr/bin/env bash
set -euo pipefail

# Print headers + contents for an explicit list of files (in order).
# Inputs (priority): args > FILES env > FILELIST env > stdin
# - FILES="path1 path2 …"
# - FILELIST=filelist.txt  (one path per line; # and blank lines ignored)
# - Globs are expanded via nullglob. Non-matches vanish silently.
# - Skips directories and non-text files (heuristic matches snapshot.sh).

is_text() {
  local f="$1" mime=""
  if mime=$(file -I -b "$f" 2>/dev/null); then
    case "$mime" in
      text/*|*json*|*xml*|*yaml*|*toml*|*javascript*|*x-shellscript*|*x-python*|*x-empty*|*inode/x-empty*) return 0 ;;
    esac
  elif mime=$(file -bi "$f" 2>/dev/null); then
    case "$mime" in
      text/*|*json*|*xml*|*yaml*|*toml*|*javascript*|*x-empty*|*inode/x-empty*) return 0 ;;
    esac
  fi
  LC_ALL=C grep -aqI . "$f"
}

gather_list_from_file() {
  # $1 = path to list file (or /dev/stdin)
  local line trimmed
  while IFS= read -r line || [ -n "${line-}" ]; do
    # trim leading/trailing spaces
    trimmed="${line#"${line%%[![:space:]]*}"}"
    trimmed="${trimmed%"${trimmed##*[![:space:]]}"}"
    [ -z "${trimmed}" ] && continue
    case "${trimmed}" in \#*) continue ;; esac
    INPUTS+=("${trimmed}")
  done < "$1"
}

# --- main ---
shopt -s nullglob

# Arrays (declare before use to satisfy set -u)
INPUTS=()
EXPANDED=()
FILES_OUT=()

# Priority: args > FILES > FILELIST > stdin
if [ "$#" -gt 0 ]; then
  while [ "$#" -gt 0 ]; do INPUTS+=("$1"); shift; done
elif [ -n "${FILES-}" ]; then
  # shellcheck disable=SC2206
  for tok in $FILES; do INPUTS+=("$tok"); done
elif [ -n "${FILELIST-}" ]; then
  gather_list_from_file "$FILELIST"
elif [ ! -t 0 ]; then
  gather_list_from_file /dev/stdin
else
  echo "partial_snapshot.sh: no input files provided (use FILES, FILELIST, args, or stdin)" >&2
  exit 2
fi

# Expand globs and normalize ./prefix
for p in "${INPUTS[@]}"; do
  case "$p" in
    *[\*\?\[]*)
      # With nullglob on, non-matching globs disappear (=> no entries)
      matches=( $p )
      for m in "${matches[@]:-}"; do
        m="${m#./}"
        EXPANDED+=("$m")
      done
      ;;
    *)
      p="${p#./}"
      EXPANDED+=("$p")
      ;;
  esac
done

# De-dup while preserving order (Bash 3 + set -u safe)
for f in "${EXPANDED[@]:-}"; do
  # skip duplicates
  already="false"
  for e in "${FILES_OUT[@]:-}"; do
    if [ "$e" = "$f" ]; then already="true"; break; fi
  done
  if [ "$already" = "true" ]; then
    continue
  fi
  FILES_OUT+=("$f")
done

# Emit
for f in "${FILES_OUT[@]:-}"; do
  [ -d "$f" ] && continue
  [ -f "$f" ] || continue
  if ! is_text "$f"; then continue; fi
  echo "===== $f ====="
  cat "$f"
  echo
  echo
done

