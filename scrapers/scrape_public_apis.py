#!/usr/bin/env python3
"""Scraper 4: marcelscruz/public-apis — parse README tables.

Table format: | API | Description | Auth | CORS | (some tables have HTTPS too).
Category comes from the preceding `### ` section header.

Usage: scrape_public_apis.py <path-to-cloned-repo>
Output: raw/public-apis.json
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(__file__))
from util import save_json  # noqa: E402


def parse_readme(path):
    recs = []
    category = None
    with open(path, encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.rstrip("\n")
            m = re.match(r"^###\s+(.+?)\s*$", line)
            if m:
                category = m.group(1).strip()
                continue
            if not line.startswith("|"):
                continue
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if len(cells) < 3:
                continue
            if re.match(r"^:?-+:?$", cells[0]):
                continue  # separator row
            if cells[0].lower() == "api":
                continue  # header row
            name_m = re.match(r"\[(.+?)\]\((.+?)\)", cells[0])
            if not name_m:
                continue
            rec = {
                "api": name_m.group(1).strip(),
                "link": name_m.group(2).strip(),
                "description": cells[1] if len(cells) > 1 else "",
                "auth": cells[2].strip("` ") if len(cells) > 2 else "",
                "category": category,
            }
            # remaining columns: HTTPS and/or CORS in either order
            for extra in cells[3:]:
                e = extra.strip().lower()
                if e in ("yes", "no"):
                    # CORS is usually last; HTTPS second-to-last — store generically
                    rec.setdefault("cors_or_https", []).append(extra.strip())
            if "cors_or_https" in rec:
                vals = rec.pop("cors_or_https")
                if len(vals) == 2:
                    rec["https"], rec["cors"] = vals
                elif len(vals) == 1:
                    rec["cors"] = vals[0]
            recs.append(rec)
    return recs


def main():
    repo = sys.argv[1] if len(sys.argv) > 1 else "/tmp/public-apis"
    recs = parse_readme(os.path.join(repo, "README.md"))
    print(f"parsed {len(recs)} entries")
    save_json(os.path.join(os.path.dirname(__file__), "..", "raw",
                           "public-apis.json"), recs)


if __name__ == "__main__":
    main()
