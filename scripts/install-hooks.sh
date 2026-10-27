#!/bin/sh
# Use the committed hooks in scripts/git-hooks/ for this clone (run once after cloning).
set -e
cd "$(git rev-parse --show-toplevel)"
git config core.hooksPath scripts/git-hooks
echo "hooks installed: $(git config core.hooksPath)"
