#!/usr/bin/env python3
"""Scraper 3: apis.guru — full OpenAPI directory as one JSON file.

https://api.apis.guru/v2/list.json -> {provider: {preferred, versions:
{ver: {info: {title, description}, swaggerUrl, link}}}}.

Output: raw/apisguru.json
"""
import sys

sys.path.insert(0, __import__("os").path.dirname(__file__))
from util import fetch_json, save_json  # noqa: E402


def main():
    data = fetch_json("https://api.apis.guru/v2/list.json")
    recs = []
    for provider, entry in data.items():
        vers = entry.get("versions") or {}
        pref = entry.get("preferred")
        v = vers.get(pref) or next(iter(vers.values()), {})
        info = v.get("info") or {}
        if isinstance(info, str):
            info = {}
        recs.append({
            "provider": provider,
            "title": (info.get("title") or "").strip(),
            "description": (info.get("description") or "").strip(),
            "spec_url": v.get("swaggerUrl") or v.get("link") or "",
            "versions": sorted(vers.keys()),
        })
    import os
    save_json(os.path.join(os.path.dirname(__file__), "..", "raw",
                           "apisguru.json"), recs)


if __name__ == "__main__":
    main()
