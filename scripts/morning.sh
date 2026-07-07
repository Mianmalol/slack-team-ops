#!/bin/zsh
# Weekday-morning pipeline, run by launchd (com.marco.slack-daily-brief):
# daily AI brief + Claude-ranked article feed, then push dedupe state.
set -uo pipefail
REPO="$HOME/github/slack-team-ops"
PY=/opt/anaconda3/bin/python3

cd "$REPO" || exit 1
git pull --rebase --quiet || echo "WARN: git pull failed; continuing with local state"

"$PY" scripts/daily_brief.py
"$PY" scripts/article_feed.py

if ! git diff --quiet state/posted_links.json; then
    git add state/posted_links.json
    git commit --quiet -m "chore: update posted-links state (local run)"
    git push --quiet || echo "WARN: git push failed; state committed locally"
fi
