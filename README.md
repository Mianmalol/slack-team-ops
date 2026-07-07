# slack-team-ops

Automation for our tech entrepreneurship class Slack workspace. Everything a
teammate needs to know is here; everything secret is *not* here.

## What runs, and where

| Thing | Where it runs | When | Posts to |
|---|---|---|---|
| Morning pipeline (`scripts/morning.sh`): daily AI brief (`daily_brief.py`) + Claude-ranked article feed (`article_feed.py`) | Marco's Mac via launchd, using `claude -p` | Weekdays 8:50am (delayed to wake-up if the laptop is asleep) | `#team-feed` |
| Article feed fallback | GitHub Actions (`article-feed.yml`), manual `workflow_dispatch` only | On demand | `#team-feed` |
| Workspace init (`scripts/init_workspace.py`) | One-time, local | — | creates channels + pins |

The article feed prefilters RSS items by keyword, then `claude -p` ranks the
candidates against `docs/research-brief.md` and rejects garbage (SEO listicles,
vendor marketing, crypto-token noise); each pick gets a one-line "why it
matters" note. If Claude judges nothing worthwhile, nothing is posted. The
Actions fallback has no Claude and degrades to keyword-count ranking.

The Q&A chatbot idea was considered and deferred: a polling bot answers in
~30 min, which barely beats asking an AI directly. If the team wants it later,
the options are an Actions polling job on an `#ask-ai` channel or a Socket
Mode bot that needs always-on hosting.

## Tuning the article feed

Edit `config/keywords.yml` (keywords, feeds, `max_posts`) and push. The current
keywords are **placeholders** — replace them once the team picks a project.
Dedupe state lives in `state/posted_links.json`; the workflow commits it back.
No matches on a given day = no post (by design, no "no news today" spam).

## Secrets

- `SLACK_BOT_TOKEN` (xoxb) lives in **GitHub Actions encrypted secrets** and in
  `~/.slack/tech-entrepreneurship.env` (chmod 600) on Marco's machine. Never in
  this repo, never in a prompt.
- The daily brief pipes message text to Claude for summarization only; Claude
  never sees the token and has no tool access.

## Slack plan caveats (free plan)

- Message history older than 90 days becomes inaccessible — put anything
  durable in a doc.
- Max 10 installed apps.

## Admin / bus-factor notes

- Slack app "Team Ops Bot" is owned by Marco (marco0111ml@gmail.com); the app
  manifest is `slack-app-manifest.yml`. To change scopes: edit the manifest at
  api.slack.com/apps and reinstall the app.
- If Marco leaves the team: make another teammate a Slack workspace owner,
  transfer this repo, regenerate the bot token, update the Actions secret.
- Failures of the article feed email the repo owner automatically (GitHub
  Actions failure notifications). Daily-brief logs:
  `~/Library/Logs/slack-daily-brief.log` on Marco's Mac.

## Connecting the project repo to #code-progress

Install the official GitHub app for Slack, then in `#code-progress` run:
`/github subscribe <owner>/<repo>`
