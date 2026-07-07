#!/usr/bin/env python3
"""Daily article push: RSS feeds -> keyword filter -> dedupe -> #team-feed.

Runs in GitHub Actions on a weekday cron. Posts nothing on days with no
matches. State (already-posted links) lives in state/posted_links.json and is
committed back by the workflow. Stdlib only.

Usage: article_feed.py [--dry-run]
"""

import json
import os
import re
import sys
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

from slack_common import load_token, post

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG = os.path.join(REPO_ROOT, "config", "keywords.yml")
STATE = os.path.join(REPO_ROOT, "state", "posted_links.json")
CHANNELS = os.path.join(REPO_ROOT, "config", "channels.json")
STATE_CAP = 500  # keep the newest N links so the file never grows unbounded

USER_AGENT = "slack-team-ops article feed (class project bot)"


def load_config() -> dict:
    """Parse our minimal keywords.yml (flat keys + '- item' lists only)."""
    cfg, current_list = {"keywords": [], "feeds": [], "max_posts": 3}, None
    with open(CONFIG) as f:
        for raw in f:
            line = raw.rstrip()
            if not line.strip() or line.strip().startswith("#"):
                continue
            if line.startswith("  - "):
                if current_list is not None:
                    current_list.append(line.strip()[2:].strip())
            elif line.endswith(":"):
                key = line[:-1].strip()
                cfg.setdefault(key, [])
                current_list = cfg[key]
            elif ":" in line:
                key, val = (p.strip() for p in line.split(":", 1))
                cfg[key] = int(val) if val.isdigit() else val
                current_list = None
    return cfg


def canonical(url: str) -> str:
    """Strip tracking params and fragments so dedupe survives utm noise."""
    p = urllib.parse.urlsplit(url)
    query = "&".join(
        kv
        for kv in p.query.split("&")
        if kv and not kv.lower().startswith(("utm_", "ref=", "fbclid", "gclid"))
    )
    return urllib.parse.urlunsplit(
        (p.scheme.lower(), p.netloc.lower(), p.path.rstrip("/"), query, "")
    )


def fetch(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=20) as resp:
        return resp.read()


def parse_feed(xml_bytes: bytes) -> list:
    """Yield {title, link, summary} from RSS 2.0 or Atom."""
    root = ET.fromstring(xml_bytes)
    items = []
    for item in root.iter("item"):  # RSS 2.0
        items.append(
            {
                "title": (item.findtext("title") or "").strip(),
                "link": (item.findtext("link") or "").strip(),
                "summary": (item.findtext("description") or "").strip(),
            }
        )
    ns = "{http://www.w3.org/2005/Atom}"
    for entry in root.iter(f"{ns}entry"):  # Atom
        link = ""
        for el in entry.findall(f"{ns}link"):
            if el.get("rel") in (None, "alternate"):
                link = el.get("href", "")
                break
        items.append(
            {
                "title": (entry.findtext(f"{ns}title") or "").strip(),
                "link": link.strip(),
                "summary": (entry.findtext(f"{ns}summary") or "").strip(),
            }
        )
    return items


def url_alive(url: str) -> bool:
    try:
        req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        with urllib.request.urlopen(req, timeout=15) as resp:
            return resp.status < 400
    except Exception:
        return False


def strip_html(text: str) -> str:
    return re.sub(r"<[^>]+>", " ", text)


def main() -> None:
    dry_run = "--dry-run" in sys.argv
    cfg = load_config()
    with open(STATE) as f:
        state = json.load(f)
    seen = set(state["posted"])

    keywords = [k.lower() for k in cfg["keywords"]]
    picks = []
    for feed_url in cfg["feeds"]:
        try:
            entries = parse_feed(fetch(feed_url))
        except Exception as e:
            print(f"WARN: feed {feed_url} failed: {e}", file=sys.stderr)
            continue
        for e in entries:
            if not e["link"] or not e["title"]:
                continue
            text = strip_html(f"{e['title']} {e['summary']}").lower()
            matched = [
                k for k in keywords if re.search(r"\b" + re.escape(k) + r"\b", text)
            ]
            if not matched:
                continue
            key = canonical(e["link"])
            if key in seen or any(p["key"] == key for p in picks):
                continue
            picks.append({**e, "key": key, "matched": matched})

    # Prefer articles matching more keywords; cap the count; drop dead links.
    picks.sort(key=lambda p: len(p["matched"]), reverse=True)
    picks = [p for p in picks[: cfg["max_posts"] * 2] if url_alive(p["link"])]
    picks = picks[: cfg["max_posts"]]

    if not picks:
        print("No new matching articles today — posting nothing.")
        return

    lines = [":newspaper: *Today's picks*"]
    for p in picks:
        lines.append(f"• <{p['link']}|{p['title']}>  _(matched: {', '.join(p['matched'])})_")
    message = "\n".join(lines)

    if dry_run:
        print("DRY RUN — would post:\n" + message)
        return

    with open(CHANNELS) as f:
        channel = json.load(f)["team-feed"]
    post(load_token(), channel, message, unfurl_links="false")
    print(f"Posted {len(picks)} article(s) to #team-feed")

    state["posted"] = (state["posted"] + [p["key"] for p in picks])[-STATE_CAP:]
    with open(STATE, "w") as f:
        json.dump(state, f, indent=2)


if __name__ == "__main__":
    main()
