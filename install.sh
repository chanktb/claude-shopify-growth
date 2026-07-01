#!/usr/bin/env bash
# Install the claude-collection-optimizer skills + scripts into ~/.claude.
#
# Copies the four collection-* skills to ~/.claude/skills/ and the helper
# scripts to ~/.claude/scripts/ so Claude Code loads them by slash command.
# Re-run after pulling updates. Your knowledge-base/ and .env stay in the repo.
set -euo pipefail

CLAUDE_HOME="${CLAUDE_HOME:-$HOME/.claude}"
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

SKILLS_DST="$CLAUDE_HOME/skills"
SCRIPTS_DST="$CLAUDE_HOME/scripts"
mkdir -p "$SKILLS_DST" "$SCRIPTS_DST"

echo "Installing claude-collection-optimizer -> $CLAUDE_HOME"

# Skills
for dir in "$REPO"/skills/*/; do
  name="$(basename "$dir")"
  rm -rf "${SKILLS_DST:?}/$name"
  cp -R "$dir" "$SKILLS_DST/$name"
  echo "  skill  $name"
done

# Scripts
for f in "$REPO"/scripts/*.py; do
  cp -f "$f" "$SCRIPTS_DST/$(basename "$f")"
  echo "  script $(basename "$f")"
done

echo ""
echo "Done. In Claude Code, run /reload-plugins or restart the session."
echo "Optional: create knowledge-base/INDEX.md + pk-*.md, and copy"
echo "config.example.env to .env if you want publish notifications."
