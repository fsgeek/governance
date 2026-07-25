#!/bin/bash
set -e

GIT_ROOT=$(git rev-parse --show-toplevel)
cd "$GIT_ROOT"

# Resolve ots the same way the post-commit hook does (venv first, uv fallback).
if [ -x "$GIT_ROOT/.venv/bin/ots" ]; then
    OTS=("$GIT_ROOT/.venv/bin/ots")
elif command -v uv >/dev/null 2>&1 && uv run --quiet ots --version >/dev/null 2>&1; then
    OTS=(uv run --quiet ots)
else
    echo "FATAL: ots client not found. Run: uv sync" >&2
    exit 1
fi

upgraded=0
pending=0
previously_completed=0
changed_paths=()
for f in timestamps/*.ots; do
    [ -f "$f" ] || continue
    original_hash=$(sha256sum "$f" | cut -d' ' -f1)
    if "${OTS[@]}" upgrade "$f" 2>/dev/null; then
        upgraded_hash=$(sha256sum "$f" | cut -d' ' -f1)
        if [ "$original_hash" != "$upgraded_hash" ]; then
            echo "upgraded: $f"
            upgraded=$((upgraded + 1))
            changed_paths+=("$f")
            if [ -f "$f.bak" ]; then
                changed_paths+=("$f.bak")
            fi
        else
	    previously_completed=$((previously_completed + 1))
        fi
    else
	pending=$((pending + 1))
        echo "pending:  $f"
    fi
done

echo ots: upgraded $upgraded, pending $pending, previously completed $previously_completed

if [ "$upgraded" -gt 0 ]; then
    git add -- "${changed_paths[@]}"
    git commit --only --no-verify \
        -m "ots: upgrade $upgraded timestamp(s)" -- "${changed_paths[@]}"
else
    echo "No timestamps ready to upgrade yet."
fi
