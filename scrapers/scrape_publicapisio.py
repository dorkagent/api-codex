#!/usr/bin/env python3
"""Scraper 2: publicapis.io — 44 category pages, listings embedded as JSON.

Each https://publicapis.io/category/<slug> embeds listings in
<script id="__NEXT_DATA__" type="application/json"> ->
props.pageProps.categoryApis (plain JSON list).

Output: raw/publicapisio.json
"""
import json
import re
import sys

sys.path.insert(0, __import__("os").path.dirname(__file__))
from util import fetch_text, save_json  # noqa: E402

CATEGORIES = ["analytics", "animals", "anime", "art-and-design", "books",
              "business", "calendar", "cloud-storage-and-file-sharing",
              "cryptocurrency", "currency-exchange", "data-access",
              "development", "dictionaries", "documents-and-productivity",
              "environment", "events", "finance", "food-and-drink",
              "games-and-comics", "geocoding", "government", "health", "iot",
              "jobs", "machine-learning", "media", "music", "news",
              "open-data", "parcel-tracking", "personality", "photography",
              "science", "security", "shopping", "social", "sports-and-fitness",
              "text-analysis", "transportation", "url-shorteners", "utilities",
              "vehicle", "video", "weather"]


def main():
    all_apis = []
    for c in CATEGORIES:
        html = fetch_text(f"https://publicapis.io/category/{c}")
        m = re.search(
            r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>',
            html, re.S)
        if not m:
            print(f"  !! no NEXT_DATA on {c}")
            continue
        pp = json.loads(m.group(1)).get("props", {}).get("pageProps", {})
        apis = pp.get("categoryApis") or []
        print(f"  {c}: {len(apis)}")
        all_apis.extend(apis)
    import os
    save_json(os.path.join(os.path.dirname(__file__), "..", "raw",
                           "publicapisio.json"), all_apis)


if __name__ == "__main__":
    main()
