#!/usr/bin/env python3
"""Scraper 1: freepublicapis.com — full catalog via sitemap + detail pages.

Each detail page embeds its record in a <script type="application/json"
data-nuxt-data id="__NUXT_DATA__"> payload in devalue format: a JSON list
where values are integer indices into the same list; typed wrappers like
["ShallowReactive", idx] wrap refs; negative ints are special constants.

Output: raw/freepublicapis.json — list of dicts with title, description,
documentation, health, pricing, pricing_note, auth_type, key_features, faq,
methods, avg_reliability, avg_latency, cors_percentage, popularity, slug.
"""
import json
import re
import sys
import time

sys.path.insert(0, __import__("os").path.dirname(__file__))
from util import fetch_text, save_json  # noqa: E402

BASE = "https://www.freepublicapis.com"
EXCLUDE_PREFIXES = ("/tags", "/watch", "/sponsor", "/newsletter", "/learn", "/about")

WRAPPERS = {"ShallowReactive", "Reactive", "Ref", "Computed", "ShallowRef"}


def resolve(payload, idx, depth=0):
    """Resolve a devalue index to its value.

    Empirically (payload dump 2026-10-11): object properties hold indices;
    one lookup yields the value, and primitives (str/int/float/bool/None)
    at that position are LITERALS, not chained references. Only lists and
    dicts recurse (list elements and dict values are indices).
    """
    if depth > 12:
        return None
    if isinstance(idx, bool):
        return idx
    if not isinstance(idx, int):
        return idx
    if idx < 0 or idx >= len(payload):
        return None
    v = payload[idx]
    if v is None or isinstance(v, (bool, str, int, float)):
        return v
    if isinstance(v, list):
        if len(v) == 2 and isinstance(v[0], str) and v[0] in WRAPPERS:
            return resolve(payload, v[1], depth + 1)
        return [resolve(payload, x, depth + 1) for x in v]
    if isinstance(v, dict):
        return {k: resolve(payload, x, depth + 1) for k, x in v.items()}
    return None


def find_api_dict(payload):
    """Find the dict in the payload that looks like the API record."""
    found = []

    def walk(o):
        if isinstance(o, dict):
            if "title" in o and "health" in o and "slug" in o:
                found.append(o)
                return
            for v in o.values():
                walk(v)
        elif isinstance(o, list):
            # skip the wrapper-type lists' first string element
            for v in o:
                if isinstance(v, (dict, list)):
                    walk(v)

    walk(payload)
    return found[0] if found else None


FIELDS = ["title", "description", "documentation", "health", "pricing",
          "pricing_note", "auth_type", "key_features", "faq", "methods",
          "avg_reliability", "avg_latency", "cors_percentage", "popularity",
          "slug", "long_description"]


def scrape_detail(url):
    html = fetch_text(url)
    m = re.search(
        r'<script type="application/json"[^>]*data-nuxt-data[^>]*>(.*?)</script>',
        html, re.S)
    if not m:
        return None
    try:
        payload = json.loads(m.group(1))
    except Exception:  # noqa: BLE001
        return None
    if not isinstance(payload, list):
        return None
    api_dict = find_api_dict(payload)
    if not api_dict:
        return None
    rec = {}
    for f in FIELDS:
        try:
            rec[f] = resolve(payload, api_dict.get(f))
        except Exception:  # noqa: BLE001
            rec[f] = None
    rec["source_url"] = url
    return rec


def main():
    sm = fetch_text(f"{BASE}/sitemap.xml")
    urls = sorted(set(re.findall(r"<loc>(https://www\.freepublicapis\.com[^<]+)</loc>", sm)))
    api_urls = [u for u in urls
                if not any(re.match(rf"{BASE}{p}(/|$)", u) for p in EXCLUDE_PREFIXES)]
    print(f"sitemap urls: {len(urls)}, api detail pages: {len(api_urls)}")
    recs, fails = [], []
    for i, u in enumerate(api_urls):
        try:
            rec = scrape_detail(u)
            if rec and rec.get("title"):
                recs.append(rec)
            else:
                fails.append(u)
        except Exception as ex:  # noqa: BLE001
            fails.append(f"{u} :: {ex}")
        if (i + 1) % 50 == 0:
            print(f"  {i + 1}/{len(api_urls)} pages, {len(recs)} ok")
        time.sleep(0.5)  # polite
    save_json(__import__("os").path.join(
        __import__("os").path.dirname(__file__), "..", "raw", "freepublicapis.json"), recs)
    print(f"done: {len(recs)} records, {len(fails)} failures")
    if fails:
        with open("/tmp/fp-fails.txt", "w") as f:
            f.write("\n".join(fails[:50]))


if __name__ == "__main__":
    main()
