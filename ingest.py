#!/usr/bin/env python3
"""
Fetches RSS feeds from AI companies, classifies signals, and writes public/signals.json.
Run manually or schedule with cron.
"""

import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path

import bleach
import feedparser

FEEDS = [
    ("OpenAI",      "https://openai.com/blog/rss.xml"),
    ("Anthropic",   "https://news.google.com/rss/search?q=Anthropic+AI&hl=en-US&gl=US&ceid=US:en"),
    ("Google",      "https://blog.google/technology/ai/rss"),
    ("Microsoft",   "https://news.google.com/rss/search?q=Microsoft+AI+Copilot&hl=en-US&gl=US&ceid=US:en"),
    ("Apple",       "https://www.apple.com/newsroom/rss-feed.rss"),
    ("Perplexity",  "https://news.google.com/rss/search?q=Perplexity+AI&hl=en-US&gl=US&ceid=US:en"),
    ("Meta",        "https://news.google.com/rss/search?q=Meta+AI&hl=en-US&gl=US&ceid=US:en"),
    ("Amazon",      "https://news.google.com/rss/search?q=Amazon+Ring+AI&hl=en-US&gl=US&ceid=US:en"),
]

HOT_KEYWORDS   = {"launch", "introducing", "announcing", "released", "new model", "breakthrough", "unveil"}
WATCH_KEYWORDS = {"partnership", "funding", "acquisition", "rumor", "leak", "hiring"}

MAX_ENTRIES = 5
SUMMARY_LEN = 200


def classify(title: str, summary: str) -> str:
    text = (title + " " + summary).lower()
    for kw in HOT_KEYWORDS:
        if kw in text:
            return "hot"
    for kw in WATCH_KEYWORDS:
        if kw in text:
            return "watch"
    return "new"


def strip_html(raw: str) -> str:
    if not raw:
        return ""
    cleaned = bleach.clean(raw, tags=[], strip=True)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned[:SUMMARY_LEN]


def parse_date(entry) -> str:
    if getattr(entry, "published_parsed", None):
        dt = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
        return dt.strftime("%Y-%m-%d")
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def fetch_signals() -> list[dict]:
    signals = []
    for company, url in FEEDS:
        print(f"Fetching {company}…", end=" ", flush=True)
        try:
            result = subprocess.run(
                ["curl", "-sL", "--max-time", "15", "-A", "Mozilla/5.0", url],
                capture_output=True,
            )
            feed = feedparser.parse(result.stdout)
            entries = feed.entries[:MAX_ENTRIES]
            for entry in entries:
                title   = entry.get("title", "").strip() or "Untitled"
                link    = entry.get("link", "#")
                raw     = entry.get("summary", entry.get("description", ""))
                summary = strip_html(raw)
                signals.append({
                    "company": company,
                    "title":   title,
                    "url":     link,
                    "summary": summary,
                    "badge":   classify(title, summary),
                    "date":    parse_date(entry),
                })
            print(f"({len(entries)} entries)")
        except Exception as exc:
            print(f"ERROR — {exc}")

    signals.sort(key=lambda s: s["date"], reverse=True)
    return signals


def main():
    signals  = fetch_signals()
    out_path = Path(__file__).parent / "public" / "signals.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)

    payload = {
        "updated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S"),
        "signals": signals,
    }

    with open(out_path, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=2, ensure_ascii=False)

    print(f"\nWrote {len(signals)} signals → {out_path}")


if __name__ == "__main__":
    main()
