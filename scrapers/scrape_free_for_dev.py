#!/usr/bin/env python3
"""Scraper 5: ripienaar/free-for-dev — parse README service entries.

Entry format: * [Name](url) - description including free-tier details.
Category comes from the preceding `## ` section header.

Usage: scrape_free_for_dev.py <path-to-cloned-repo>
Output: raw/free-for-dev.json
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(__file__))
from util import save_json  # noqa: E402

ENTRY = re.compile(r"^\s*\*\s+\[(.+?)\]\((.+?)\)\s*[-:–]\s*(.+?)\s*$")


def parse_readme(path):
    recs = []
    category = None
    with open(path, encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.rstrip("\n")
            m = re.match(r"^##\s+(.+?)\s*$", line)
            if m:
                category = m.group(1).strip()
                continue
            em = ENTRY.match(line)
            if em:
                name, url, desc = (g.strip() for g in em.groups())
                recs.append({
                    "name": name,
                    "url": url,
                    "description": desc,
                    "free_tier": desc,  # the list is free-tier offerings; desc states the terms
                    "category": category,
                })
    return recs


def main():
    repo = sys.argv[1] if len(sys.argv) > 1 else "/tmp/free-for-dev"
    recs = parse_readme(os.path.join(repo, "README.md"))
    print(f"parsed {len(recs)} entries")
    save_json(os.path.join(os.path.dirname(__file__), "..", "raw",
                           "free-for-dev.json"), recs)


if __name__ == "__main__":
    main()
