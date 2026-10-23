#!/usr/bin/env python3
"""Generate REPORT.md from catalog.json + raw source files."""
import json
import os
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.join(HERE, "..")
CAT = os.path.join(BASE, "catalog.json")
RAW = os.path.join(BASE, "raw")
OUT = os.path.join(BASE, "REPORT.md")

SOURCE_FILES = {
    "freepublicapis": "freepublicapis.json",
    "publicapis.io": "publicapisio.json",
    "apis.guru": "apisguru.json",
    "public-apis": "public-apis.json",
    "free-for-dev": "free-for-dev.json",
}


def main():
    catalog = json.load(open(CAT))
    total = len(catalog)
    with_free = sum(1 for e in catalog if e["free_tier_known"])
    with_docs = sum(1 for e in catalog if e["docs_url"])
    multi = sum(1 for e in catalog if len(e["provenance"]) > 1)

    raw_counts = {}
    for src, fn in SOURCE_FILES.items():
        p = os.path.join(RAW, fn)
        try:
            raw_counts[src] = len(json.load(open(p)))
        except Exception:  # noqa: BLE001
            raw_counts[src] = "MISSING"

    # category spread (top 15)
    cats = {}
    for e in catalog:
        c = e.get("category") or "uncategorized"
        cats[c] = cats.get(c, 0) + 1
    top_cats = sorted(cats.items(), key=lambda t: t[1], reverse=True)[:15]

    # auth breakdown
    auths = {}
    for e in catalog:
        a = e.get("auth") or "unknown"
        auths[a] = auths.get(a, 0) + 1

    samples = catalog[:5]

    lines = []
    A = lines.append
    A("# API Codex — Scrape Report")
    A("")
    A(f"**Generated:** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}")
    A("")
    A("## Per-source counts (raw)")
    A("")
    A("| Source | Records | Notes |")
    A("|---|---|---|")
    notes = {
        "freepublicapis": "sitemap + detail pages, embedded devalue JSON; richest free-tier data",
        "publicapis.io": "44 category pages, embedded __NEXT_DATA__ JSON",
        "apis.guru": "single list.json, OpenAPI-described providers",
        "public-apis": "marcelscruz/public-apis README tables (shallow clone)",
        "free-for-dev": "ripienaar/free-for-dev README entries (shallow clone)",
    }
    for src in SOURCE_FILES:
        A(f"| {src} | {raw_counts[src]} | {notes[src]} |")
    A("")
    A("## Merged catalog")
    A("")
    A(f"- **Total unique APIs:** {total}")
    A(f"- With free-tier info (`free_tier_known`): {with_free} ({with_free/total*100:.1f}%)")
    A(f"- With docs URL: {with_docs} ({with_docs/total*100:.1f}%)")
    A(f"- Listed in 2+ sources: {multi} ({multi/total*100:.1f}%)")
    A("")
    A("### Top categories")
    A("")
    for c, n in top_cats:
        A(f"- {c}: {n}")
    A("")
    A("### Auth breakdown (top 10)")
    A("")
    for a, n in sorted(auths.items(), key=lambda t: t[1], reverse=True)[:10]:
        A(f"- {a}: {n}")
    A("")
    A("## Sample entries (full JSON)")
    A("")
    for e in samples:
        A("```json")
        A(json.dumps(e, indent=1, ensure_ascii=False)[:1500])
        A("```")
        A("")
    A("## Data-quality notes and gaps")
    A("")
    A("- **Free-tier coverage is uneven.** Only freepublicapis ships structured "
      "pricing/quota data per API; free-for-dev entries describe free tiers in "
      "prose. publicapis.io, apis.guru, and the public-apis list carry no "
      "per-entry free-limit data — those entries are tagged "
      "`free_tier_known: false`, not dropped.")
    A("- **Dedupe is name-based.** Same service under different names across "
      "directories (e.g. 'Alpha Vantage' vs 'AlphaVantage API') may appear "
      "twice; domain tie-breaking reduces but does not eliminate this.")
    A("- **Descriptions vary in quality.** Directory blurbs are marketing copy; "
      "treat them as leads, not verified claims. Free-tier verification rule "
      "still applies before adding anything to the toolkit.")
    A("- **apis.guru skews enterprise.** Its ~2.5k OpenAPI-described providers "
      "include many paid-only APIs; they are kept for the docs/spec links, "
      "with `free_tier_known: false`.")
    A("- **Scraper rot risk.** freepublicapis and publicapis.io embed data in "
      "page structure (`__NUXT_DATA__` / `__NEXT_DATA__`); a redesign breaks "
      "the parsers. The merge step fails loudly if any source drops below "
      "50% of its record floor.")
    A("")
    A("## Runtime")
    A("")
    A("- freepublicapis: ~750 detail pages at 0.5s politeness delay.")
    A("- publicapis.io: 44 category pages. apis.guru: 1 JSON file. "
      "GitHub lists: 2 shallow clones.")
    A("- Recommended refresh cadence: twice a month.")
    A("")

    with open(OUT, "w") as f:
        f.write("\n".join(lines))
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
