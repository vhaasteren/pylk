#!/usr/bin/env bash
set -euo pipefail

# Snapshot text files (with headers) to stdout.
# Defaults (overridable):
#   SNAPSHOT_EXCLUDES="node_modules .venv dist out *.patch"
#   INCLUDE_UNTRACKED=1  # include untracked-but-not-ignored files (git repos)
#   SNAPSHOT_PATHS=""    # space-separated include roots; if set, only these paths are considered

DEFAULT_EXCLUDES="node_modules .venv dist out *.patch"
EXCL_RAW="${SNAPSHOT_EXCLUDES:-$DEFAULT_EXCLUDES}"
PATHS_RAW="${SNAPSHOT_PATHS:-}"

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

in_git_repo=false
if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  in_git_repo=true
fi

# Build git pathspec-style excludes (use :(exclude) for wide compatibility)
build_git_excludes() {
  local token
  for token in $EXCL_RAW; do
    if [[ "$token" == *"*"* || "$token" == *"?"* || "$token" == *"["* ]]; then
      echo ":(exclude)$token"
    else
      echo ":(exclude)$token"
      echo ":(exclude)$token/**"
    fi
  done
}

# Build list of include roots (if any)
read -r -a INCLUDE_PATHS <<< "$PATHS_RAW"

files=()

if $in_git_repo; then
  EXCL_OPTS=()
  while IFS= read -r line; do
    [ -n "$line" ] && EXCL_OPTS+=("$line")
  done < <(build_git_excludes || true)

  # Tracked files
  if [ ${#INCLUDE_PATHS[@]} -gt 0 ]; then
    if [ ${#EXCL_OPTS[@]} -gt 0 ]; then
      while IFS= read -r -d '' f; do files+=("$f"); done \
        < <(git ls-files -z -- "${INCLUDE_PATHS[@]}" "${EXCL_OPTS[@]}")
    else
      while IFS= read -r -d '' f; do files+=("$f"); done \
        < <(git ls-files -z -- "${INCLUDE_PATHS[@]}")
    fi
  else
    if [ ${#EXCL_OPTS[@]} -gt 0 ]; then
      while IFS= read -r -d '' f; do files+=("$f"); done \
        < <(git ls-files -z -- . "${EXCL_OPTS[@]}")
    else
      while IFS= read -r -d '' f; do files+=("$f"); done \
        < <(git ls-files -z)
    fi
  fi

  # Untracked (but not ignored)
  if [ "${INCLUDE_UNTRACKED:-1}" = "1" ]; then
    if [ ${#INCLUDE_PATHS[@]} -gt 0 ]; then
      if [ ${#EXCL_OPTS[@]} -gt 0 ]; then
        while IFS= read -r -d '' f; do files+=("$f"); done \
          < <(git ls-files -z --others --exclude-standard -- "${INCLUDE_PATHS[@]}" "${EXCL_OPTS[@]}")
      else
        while IFS= read -r -d '' f; do files+=("$f"); done \
          < <(git ls-files -z --others --exclude-standard -- "${INCLUDE_PATHS[@]}")
      fi
    else
      if [ ${#EXCL_OPTS[@]} -gt 0 ]; then
        while IFS= read -r -d '' f; do files+=("$f"); done \
          < <(git ls-files -z --others --exclude-standard -- . "${EXCL_OPTS[@]}")
      else
        while IFS= read -r -d '' f; do files+=("$f"); done \
          < <(git ls-files -z --others --exclude-standard)
      fi
    fi
  fi
fi

# Non-git fallback
if [ ${#files[@]} -eq 0 ]; then
  # Build a prune group so we never descend into excluded directories/globs
  SKIP="$EXCL_RAW"
  build_find_with_prune() {
    local root="$1"
    local -a prune=()
    local s
    for s in $SKIP; do
      if [[ "$s" == *"*"* || "$s" == *"?"* || "$s" == *"["* ]]; then
        prune+=( -name "$s" -o )
      else
        prune+=( -path "$root/$s" -o -path "$root/$s/*" -o -path "*/$s" -o -path "*/$s/*" -o )
      fi
    done
    if [ "${#prune[@]}" -gt 0 ]; then unset 'prune[${#prune[@]}-1]'; fi
    if [ "${#prune[@]}" -gt 0 ]; then
      find "$root" \( "${prune[@]}" \) -prune -o -type f -print0
    else
      find "$root" -type f -print0
    fi
  }

  if [ ${#INCLUDE_PATHS[@]} -gt 0 ]; then
    for root in "${INCLUDE_PATHS[@]}"; do
      while IFS= read -r -d '' f; do files+=("$f"); done < <(build_find_with_prune "$root")
    done
  else
    while IFS= read -r -d '' f; do files+=("$f"); done < <(build_find_with_prune ".")
  fi
fi

# Emit snapshot
for f in "${files[@]}"; do
  [ -f "$f" ] || continue
  if is_text "$f"; then
    echo "===== $f ====="
    cat "$f"
    echo
    echo
  fi
done

