# API Codex

A merged, deduplicated catalog of public APIs, with a focus on which ones
offer a free tier. Five API directories are scraped and normalized into one
dataset so the same API listed in three places appears once, with its
provenance kept.

## Sources

All credit for the underlying listings belongs to the source directories:

- [APIs.guru](https://apis.guru) — the OpenAPI directory (via api.apis.guru)
- [publicapis.io](https://publicapis.io)
- [freepublicapis.com](https://freepublicapis.com)
- [marcelscruz/public-apis](https://github.com/marcelscruz/public-apis)
- [ripienaar/free-for-dev](https://github.com/ripienaar/free-for-dev)

## Artifacts

- `catalog.json` — the merged catalog before deduplication
- `catalog_v2.json` — the deduplicated catalog (the main dataset)
- `quarantined.json` — listings pulled out of the main catalog (for example
  marketplace resellers), with the reason recorded
- `codex.db` — the same data as SQLite, for local querying
- `REPORT.md` — per-source counts and data-quality notes from the last run

## Refresh

A GitHub Actions workflow re-runs the full pipeline twice a month (the 1st
and 15th) and commits the updated artifacts. It can also be run manually
from the Actions tab.

Pipeline order: the five scrapers in `scrapers/` write `raw/*.json`,
`merge.py` merges them, `dedupe.py` deduplicates, `export_sqlite.py`
builds `codex.db`, and `gen_report.py` writes `REPORT.md`. Stdlib Python
only, no API keys, no browser.

## Run it locally

```bash
git clone --depth 1 https://github.com/ripienaar/free-for-dev /tmp/free-for-dev
git clone --depth 1 https://github.com/marcelscruz/public-apis /tmp/public-apis
python3 scrapers/scrape_apisguru.py
python3 scrapers/scrape_publicapisio.py
python3 scrapers/scrape_freepublicapis.py
python3 scrapers/scrape_free_for_dev.py /tmp/free-for-dev
python3 scrapers/scrape_public_apis.py /tmp/public-apis
python3 scrapers/merge.py
python3 scrapers/dedupe.py
python3 scrapers/export_sqlite.py
python3 scrapers/gen_report.py
```

## License

Code is MIT (see `LICENSE`). The catalog data is factual listing data
republished with attribution to the source directories above.
