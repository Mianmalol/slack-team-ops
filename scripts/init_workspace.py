#!/usr/bin/env python3
"""One-time workspace initialization: channels, topics, starter pins.

Idempotent — safe to re-run; existing channels are reused, not duplicated.
Writes the resulting channel IDs to config/channels.json for the automations.
"""

import json
import os

from slack_common import api, channel_ids, load_token, post

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

CHANNELS = [
    {
        "name": "announcements",
        "topic": "Team-wide announcements: deadlines, meetings, decisions",
        "purpose": "Low-noise channel for things everyone must see.",
        "pin": (
            ":wave: *Welcome! How this workspace is organized*\n"
            "• *#announcements* — deadlines, meetings, decisions. Low noise, everyone reads it.\n"
            "• *#research-findings* — post findings as: what you found, source link, why it matters.\n"
            "• *#code-progress* — what you shipped or are stuck on; GitHub notifications land here too.\n"
            "• *#team-feed* — the bot posts a daily AI summary and relevant articles here.\n"
            "\n*Inviting teammates:* click the workspace name → Invite people to <this workspace>.\n"
            "*Heads-up:* we're on Slack's free plan, so messages older than 90 days become inaccessible. "
            "Anything worth keeping long-term goes in a doc, not just Slack."
        ),
    },
    {
        "name": "research-findings",
        "topic": "Market / user / competitor research",
        "purpose": "One message per finding so the daily brief can pick them up.",
        "pin": (
            ":mag: *Posting convention for findings*\n"
            "One message per finding, in this shape:\n"
            "• *Finding:* the one-line takeaway\n"
            "• *Source:* link\n"
            "• *So what:* what it means for our project\n"
            "Threads for discussion. The daily brief in #team-feed summarizes this channel every morning."
        ),
    },
    {
        "name": "code-progress",
        "topic": "What shipped, what's blocked, PRs & commits",
        "purpose": "Codebase progress updates and GitHub notifications.",
        "pin": (
            ":hammer_and_wrench: *Posting convention*\n"
            "Short updates: what you shipped, what you're working on, where you're stuck.\n"
            "Once our project repo exists, connect GitHub notifications by installing the official "
            "GitHub app for Slack and running:\n"
            "`/github subscribe <owner>/<repo>`\n"
            "in this channel — commits, PRs and issues will post here automatically."
        ),
    },
    {
        "name": "team-feed",
        "topic": "Bot feed: daily AI brief + relevant articles",
        "purpose": "Automated content only — daily summary and article pushes.",
        "pin": (
            ":robot_face: *What posts here*\n"
            "• *Daily brief* (weekday mornings): AI summary of yesterday's activity in "
            "#research-findings, #code-progress and #general. Skipped on quiet days.\n"
            "• *Article feed* (weekday mornings): up to 3 relevant articles matched against keywords in "
            "`config/keywords.yml` in our slack-team-ops repo — edit that file to tune the feed.\n"
            "Keep discussion in threads so the feed stays scannable."
        ),
    },
]


def main() -> None:
    token = load_token()
    existing = channel_ids(token)
    ids = {}

    for spec in CHANNELS:
        name = spec["name"]
        created = name not in existing
        if created:
            cid = api("conversations.create", token, name=name)["channel"]["id"]
            print(f"#{name}: created ({cid})")
        else:
            cid = existing[name]
            print(f"#{name}: already exists ({cid})")
        ids[name] = cid

        api("conversations.join", token, channel=cid)
        api("conversations.setTopic", token, channel=cid, topic=spec["topic"])
        api("conversations.setPurpose", token, channel=cid, purpose=spec["purpose"])

        if created:
            ts = post(token, cid, spec["pin"], unfurl_links="false")["ts"]
            api("pins.add", token, channel=cid, timestamp=ts)
            print(f"#{name}: starter message pinned")

    # #general exists by default; join it so the daily brief can read it.
    if "general" in existing:
        api("conversations.join", token, channel=existing["general"])
        ids["general"] = existing["general"]

    out = os.path.join(REPO_ROOT, "config", "channels.json")
    with open(out, "w") as f:
        json.dump(ids, f, indent=2)
    print(f"Channel IDs written to {out}")


if __name__ == "__main__":
    main()
