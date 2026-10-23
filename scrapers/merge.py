#!/usr/bin/env python3
"""Merge the five codex sources into one deduped catalog.json.

Dedupe by normalized lowercase name; tie-break with website domain.
Every entry keeps full provenance. Focus is FREE APIs: free-tier info is
preserved where present; entries lacking it are tagged
free_tier_known=false rather than dropped.

Validation floors (per source). If any source drops below 50% of its
floor, exit non-zero and report — never silently ship a gutted catalog.
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(HERE, "..", "raw")
OUT = os.path.join(HERE, "..", "catalog.json")

sys.path.insert(0, HERE)
from util import norm_name, domain_of  # noqa: E402

FLOORS = {
    "freepublicapis": 400,
    "publicapis.io": 1000,
    "apis.guru": 1500,
    "public-apis": 1000,
    "free-for-dev": 100,
}

FAILURES = []


RAW_FILES = {
    "freepublicapis": "freepublicapis.json",
    "publicapis.io": "publicapisio.json",
    "apis.guru": "apisguru.json",
    "public-apis": "public-apis.json",
    "free-for-dev": "free-for-dev.json",
}


def load(name):
    p = os.path.join(RAW, RAW_FILES[name])
    try:
        with open(p) as f:
            return json.load(f)
    except Exception as ex:  # noqa: BLE001
        FAILURES.append(f"{name}: could not load {p}: {ex}")
        return []


def clean(s):
    if not s:
        return None
    s = str(s).strip()
    return s or None


# ---- per-source adapters: each yields unified dicts ---------------------

def adapt_freepublicapis(recs):
    for r in recs:
        pricing = clean(r.get("pricing"))
        note = clean(r.get("pricing_note"))
        free_text = pricing
        if note and note != pricing:
            free_text = f"{pricing} — {note}" if pricing else note
        yield {
            "name": clean(r.get("title")) or "unknown",
            "description": clean(r.get("description")) or clean(r.get("long_description")),
            "docs_url": clean(r.get("documentation")),
            "website": clean(r.get("documentation")),
            "category": None,
            "auth": clean(r.get("auth_type")),
            "pricing_free": free_text,
            "free_tier_known": bool(free_text),
            "health": r.get("health"),
            "extra": {
                "key_features": r.get("key_features"),
                "faq": r.get("faq"),
                "avg_reliability": r.get("avg_reliability"),
                "avg_latency": r.get("avg_latency"),
                "cors_percentage": r.get("cors_percentage"),
                "popularity": r.get("popularity"),
            },
            "source_id": clean(r.get("slug")),
        }


def adapt_publicapisio(recs):
    for r in recs:
        site = clean(r.get("website"))
        yield {
            "name": clean(r.get("title")) or "unknown",
            "description": clean(r.get("description")),
            "docs_url": site,
            "website": site,
            "category": clean(r.get("category")),
            "auth": None,
            "pricing_free": None,
            "free_tier_known": False,
            "health": None,
            "extra": {"hostname": clean(r.get("hostname"))},
            "source_id": clean(r.get("slug")),
        }


def adapt_apisguru(recs):
    for r in recs:
        title = clean(r.get("title")) or clean(r.get("provider")) or "unknown"
        yield {
            "name": title,
            "description": clean(r.get("description")),
            "docs_url": clean(r.get("spec_url")),
            "website": None,
            "category": None,
            "auth": None,
            "pricing_free": None,
            "free_tier_known": False,
            "health": None,
            "extra": {"openapi_spec": clean(r.get("spec_url"))},
            "source_id": clean(r.get("provider")),
        }


def adapt_public_apis(recs):
    for r in recs:
        auth = clean(r.get("auth"))
        # the list uses "No" to mean no authentication required
        if auth and auth.lower() == "no":
            auth = "none"
        yield {
            "name": clean(r.get("api")) or "unknown",
            "description": clean(r.get("description")),
            "docs_url": clean(r.get("link")),
            "website": clean(r.get("link")),
            "category": clean(r.get("category")),
            "auth": auth,
            "pricing_free": None,
            "free_tier_known": False,  # list is public APIs; free tier not specified per-entry
            "health": None,
            "extra": {
                "https": clean(r.get("https")),
                "cors": clean(r.get("cors")),
            },
            "source_id": None,
        }


def adapt_free_for_dev(recs):
    for r in recs:
        yield {
            "name": clean(r.get("name")) or "unknown",
            "description": clean(r.get("description")),
            "docs_url": clean(r.get("url")),
            "website": clean(r.get("url")),
            "category": clean(r.get("category")),
            "auth": None,
            "pricing_free": clean(r.get("free_tier")),
            "free_tier_known": True,  # the whole list is free-tier offerings
            "health": None,
            "extra": {},
            "source_id": None,
        }


ADAPTERS = {
    "freepublicapis": adapt_freepublicapis,
    "publicapis.io": adapt_publicapisio,
    "apis.guru": adapt_apisguru,
    "public-apis": adapt_public_apis,
    "free-for-dev": adapt_free_for_dev,
}

SOURCE_ORDER = ["freepublicapis", "publicapis.io", "apis.guru",
                "public-apis", "free-for-dev"]


def merge_field(entries, field):
    """First non-null value wins, preferring richer sources first."""
    for e in entries:
        v = e.get(field)
        if v:
            return v
    return None


def main():
    per_source_counts = {}
    # (norm_name, domain) -> list of (source, entry)
    buckets = {}
    for src in SOURCE_ORDER:
        recs = load(src)
        per_source_counts[src] = len(recs)
        floor = FLOORS[src]
        if len(recs) < floor * 0.5:
            FAILURES.append(
                f"{src}: only {len(recs)} records, floor is {floor} "
                f"(50% = {floor * 0.5:.0f}) — source likely broken")
        for e in ADAPTERS[src](recs):
            key = (norm_name(e["name"]), domain_of(e.get("website") or ""))
            buckets.setdefault(key, []).append((src, e))

    catalog = []
    for (nkey, dom), items in buckets.items():
        # order items by source richness for field merging
        items.sort(key=lambda t: SOURCE_ORDER.index(t[0]))
        merged = {
            "name": merge_field([e for _, e in items], "name"),
            "description": merge_field([e for _, e in items], "description"),
            "docs_url": merge_field([e for _, e in items], "docs_url"),
            "website": merge_field([e for _, e in items], "website"),
            "category": merge_field([e for _, e in items], "category"),
            "auth": merge_field([e for _, e in items], "auth"),
            "pricing_free": merge_field([e for _, e in items], "pricing_free"),
            "free_tier_known": any(e.get("free_tier_known") for _, e in items),
            "health": merge_field([e for _, e in items], "health"),
            "provenance": [s for s, _ in items],
            "source_ids": {s: e.get("source_id") for s, e in items
                           if e.get("source_id")},
        }
        # merge extras shallowly
        extra = {}
        for _, e in items:
            for k, v in (e.get("extra") or {}).items():
                if v and k not in extra:
                    extra[k] = v
        merged["extra"] = extra
        catalog.append(merged)

    catalog.sort(key=lambda e: (e["name"] or "").lower())
    with open(OUT, "w") as f:
        json.dump(catalog, f, indent=1)

    stats = {
        "total_unique": len(catalog),
        "per_source": per_source_counts,
        "with_free_tier": sum(1 for e in catalog if e["free_tier_known"]),
        "with_docs": sum(1 for e in catalog if e["docs_url"]),
        "multi_source": sum(1 for e in catalog if len(e["provenance"]) > 1),
    }
    print(json.dumps(stats, indent=1))
    if FAILURES:
        print("\nFAILURES:", file=sys.stderr)
        for fl in FAILURES:
            print("  -", fl, file=sys.stderr)
        sys.exit(2)
    return stats


if __name__ == "__main__":
    main()
