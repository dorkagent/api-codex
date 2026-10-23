"""Shared helpers for api-codex scrapers."""
import json
import time
import urllib.request
import urllib.error

UA = "dork-api-codex/1.0"
TIMEOUT = 30


def fetch_text(url, retries=3):
    """Fetch a URL, return decoded text. Retries on transient errors."""
    last = None
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
                return r.read().decode("utf-8", errors="replace")
        except Exception as ex:  # noqa: BLE001
            last = ex
            time.sleep(2 * (attempt + 1))
    raise RuntimeError(f"fetch failed after {retries} tries: {url}: {last}")


def fetch_json(url, retries=3):
    return json.loads(fetch_text(url, retries))


def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=1)
    print(f"wrote {path} ({len(data) if isinstance(data, list) else 'obj'})")


def norm_name(name):
    """Normalize a name for dedupe keys."""
    import re
    n = (name or "").lower().strip()
    n = re.sub(r"\s+(api|apis)\s*$", "", n)  # trailing "API"
    n = re.sub(r"[^a-z0-9]+", " ", n)
    return re.sub(r"\s+", " ", n).strip()


def domain_of(url):
    """Extract registrable-ish domain from a URL for tie-breaking."""
    if not url:
        return ""
    import re
    m = re.search(r"https?://([^/\"' >]+)", url)
    if not m:
        return ""
    host = m.group(1).lower().split(":")[0]
    parts = host.split(".")
    return ".".join(parts[-2:]) if len(parts) >= 2 else host
