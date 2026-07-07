"""Shared Slack Web API helpers. Stdlib only — no pip installs needed."""

import json
import os
import sys
import time
import urllib.parse
import urllib.request

TOKEN_ENV_FILE = os.path.expanduser("~/.slack/tech-entrepreneurship.env")
API_BASE = "https://slack.com/api/"


def load_token() -> str:
    token = os.environ.get("SLACK_BOT_TOKEN")
    if not token and os.path.exists(TOKEN_ENV_FILE):
        with open(TOKEN_ENV_FILE) as f:
            for line in f:
                line = line.strip()
                if line.startswith("SLACK_BOT_TOKEN="):
                    token = line.split("=", 1)[1].strip().strip('"')
    if not token:
        sys.exit(
            "No Slack token: set SLACK_BOT_TOKEN or put it in " + TOKEN_ENV_FILE
        )
    return token


def api(method: str, token: str, **params) -> dict:
    """Call a Slack Web API method, retrying on rate limits."""
    for attempt in range(5):
        data = urllib.parse.urlencode(params).encode()
        req = urllib.request.Request(
            API_BASE + method,
            data=data,
            headers={"Authorization": f"Bearer {token}"},
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            body = json.load(resp)
        if body.get("ok"):
            return body
        if body.get("error") == "ratelimited":
            wait = int(resp.headers.get("Retry-After", 2 ** (attempt + 1)))
            time.sleep(wait)
            continue
        raise RuntimeError(f"{method} failed: {body.get('error')} ({body})")
    raise RuntimeError(f"{method}: still rate-limited after 5 attempts")


def channel_ids(token: str) -> dict:
    """Map of channel name -> id for all public channels."""
    out, cursor = {}, ""
    while True:
        resp = api(
            "conversations.list",
            token,
            types="public_channel",
            limit=200,
            cursor=cursor,
        )
        for ch in resp["channels"]:
            out[ch["name"]] = ch["id"]
        cursor = resp.get("response_metadata", {}).get("next_cursor", "")
        if not cursor:
            return out


def post(token: str, channel_id: str, text: str, **kw) -> dict:
    return api("chat.postMessage", token, channel=channel_id, text=text, **kw)
