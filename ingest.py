#!/usr/bin/env python3
"""
Fetches RSS feeds from AI companies, classifies signals, and writes public/signals.json.
Merges with existing signals and deduplicates by URL so re-runs never add duplicates.
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

MAX_FRESH    = 5   # entries fetched per company per run
MAX_STORED   = 10  # entries kept per company in the JSON


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
    cleaned = re.sub(r"[\xa0\s]+", " ", cleaned).strip()
    return cleaned[:200]


def parse_date(entry) -> str:
    if getattr(entry, "published_parsed", None):
        dt = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
        return dt.strftime("%Y-%m-%d")
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def load_existing(out_path: Path) -> dict[str, dict]:
    """Returns existing signals keyed by URL."""
    if not out_path.exists():
        return {}
    try:
        with open(out_path, encoding="utf-8") as fh:
            data = json.load(fh)
        return {s["url"]: s for s in data.get("signals", []) if s.get("url")}
    except Exception:
        return {}


def merge(fresh: list[dict], existing: dict[str, dict]) -> list[dict]:
    """Merge fresh signals with existing, dedup by URL, cap per company."""
    merged: dict[str, dict] = {s["url"]: s for s in fresh}
    for url, sig in existing.items():
        if url not in merged:
            merged[url] = sig

    by_company: dict[str, list] = {}
    for sig in merged.values():
        by_company.setdefault(sig["company"], []).append(sig)

    result = []
    for sigs in by_company.values():
        sigs.sort(key=lambda s: s["date"], reverse=True)
        result.extend(sigs[:MAX_STORED])

    result.sort(key=lambda s: s["date"], reverse=True)
    return result


def fetch_fresh() -> list[dict]:
    signals = []
    for company, url in FEEDS:
        print(f"Fetching {company}…", end=" ", flush=True)
        try:
            result = subprocess.run(
                ["curl", "-sL", "--max-time", "15", "-A", "Mozilla/5.0", url],
                capture_output=True,
            )
            feed    = feedparser.parse(result.stdout)
            entries = feed.entries[:MAX_FRESH]
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
    return signals


def main():
    out_path = Path(__file__).parent / "public" / "signals.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)

    existing = load_existing(out_path)
    fresh    = fetch_fresh()
    signals  = merge(fresh, existing)

    new_count = sum(1 for s in fresh if s["url"] not in existing)
    print(f"\n{new_count} new signal(s), {len(signals)} total → {out_path}")

    with open(out_path, "w", encoding="utf-8") as fh:
        json.dump(
            {"updated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S"),
             "signals": signals},
            fh, indent=2, ensure_ascii=False,
        )


if __name__ == "__main__":
    main()
