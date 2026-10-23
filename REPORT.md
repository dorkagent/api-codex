# API Codex — Scrape Report

**Generated:** 2026-10-12 04:17 UTC

## Per-source counts (raw)

| Source | Records | Notes |
|---|---|---|
| freepublicapis | 727 | sitemap + detail pages, embedded devalue JSON; richest free-tier data |
| publicapis.io | 1449 | 44 category pages, embedded __NEXT_DATA__ JSON |
| apis.guru | 2529 | single list.json, OpenAPI-described providers |
| public-apis | 1844 | marcelscruz/public-apis README tables (shallow clone) |
| free-for-dev | 1316 | ripienaar/free-for-dev README entries (shallow clone) |

## Merged catalog

- **Total unique APIs:** 6567
- With free-tier info (`free_tier_known`): 1983 (30.2%)
- With docs URL: 5873 (89.4%)
- Listed in 2+ sources: 856 (13.0%)

### Top categories

- uncategorized: 2621
- Development: 277
- Geocoding: 142
- Games & Comics: 137
- Transportation: 128
- Finance: 126
- Government: 114
- Cryptocurrency: 112
- Email: 101
- APIs, Data, and ML: 99
- Open Data: 91
- Video: 84
- Tools for Teams and Collaboration: 80
- Social: 80
- Documents & Productivity: 73

### Auth breakdown (top 10)

- unknown: 4160
- none: 1173
- apiKey: 947
- OAuth: 148
- api_key: 95
- bearer: 32
- X-Mashape-Key: 5
- other: 4
- basic: 2
- User-Agent: 1

## Sample entries (full JSON)

```json
{
 "name": "0x",
 "description": "API for querying token and pool stats across various liquidity pools",
 "docs_url": "https://0x.org/api",
 "website": "https://0x.org/api",
 "category": "Cryptocurrency",
 "auth": null,
 "pricing_free": null,
 "free_tier_known": false,
 "health": null,
 "provenance": [
  "publicapis.io"
 ],
 "source_ids": {
  "publicapis.io": "0x-api"
 },
 "extra": {
  "hostname": "0x.org"
 }
}
```

```json
{
 "name": "0xArchive",
 "description": "Real-time and historical Hyperliquid and Lighter market data",
 "docs_url": "https://0xarchive.io",
 "website": "https://0xarchive.io",
 "category": "Cryptocurrency",
 "auth": "apiKey",
 "pricing_free": null,
 "free_tier_known": false,
 "health": null,
 "provenance": [
  "public-apis"
 ],
 "source_ids": {},
 "extra": {
  "cors": "No"
 }
}
```

```json
{
 "name": "1,000,000+ Recipe and Grocery List API (v2)",
 "description": "#Documentation\r\n\r\nThis is the documentation for the partner endpoint of the BigOven Recipe and Grocery List API.\r\n\r\nThe update brings with it Swagger-based documentation. [Swagger](http://swagger.io) is an emerging standard for describing REST-based APIs, and with this Swagger-compliant endpoint (above), you can make ready-to-go interface libraries for your code via [swagger-codegen](https://github.com/swagger-api/swagger-codegen). For instance, it's easy to generate libraries for Node.js, Java, Ruby, ASP.NET MVC, jQuery, php and more!\r\n\r\nYou can also try out the endpoint calls with your own api_key right here on this page. Be sure to enter your api_key above to use the \"Try it out!\" buttons on this page.\r\n\r\n##Start Here\r\n\r\nDevelopers new to the BigOven API should start with this version, not with the legacy API. We'll be making improvements to this API over time, and doing only bug fixes on the v1 API.\r\n\r\n\r\n\r\nTo pretend you're a BigOven user (for instance, to get your recently viewed recipes or your grocery list), you need to pass in Basic Authentication information in the header, just as with the v1 API. We do now require that you make all calls via https. You need to pass your api_key in with every call, though this can now be done on the header (send a request header \"X-BigOven-API-Key\" set to your api_key value, e.g., Request[\"X-BigOven-API-Key\"]=\"your-key-here\"
```

```json
{
 "name": "1.1.1.1",
 "description": "Free public DNS Resolver, which is fast and secure (encrypt your DNS query), provided by Cloudflare. Useful to bypass your internet provider's DNS blocking, prevent DNS query spying, and [to block adult & malware content](https://developers.cloudflare.com/1.1.1.1/1.1.1.1-for-families). It can also be used [via API](https://developers.cloudflare.com/1.1.1.1/encrypted-dns/dns-over-https/make-api-requests). Note: Just a DNS resolver, not a DNS hoster.",
 "docs_url": "https://developers.cloudflare.com/1.1.1.1/",
 "website": "https://developers.cloudflare.com/1.1.1.1/",
 "category": "DNS",
 "auth": null,
 "pricing_free": "Free public DNS Resolver, which is fast and secure (encrypt your DNS query), provided by Cloudflare. Useful to bypass your internet provider's DNS blocking, prevent DNS query spying, and [to block adult & malware content](https://developers.cloudflare.com/1.1.1.1/1.1.1.1-for-families). It can also be used [via API](https://developers.cloudflare.com/1.1.1.1/encrypted-dns/dns-over-https/make-api-requests). Note: Just a DNS resolver, not a DNS hoster.",
 "free_tier_known": true,
 "health": null,
 "provenance": [
  "free-for-dev"
 ],
 "source_ids": {},
 "extra": {}
}
```

```json
{
 "name": "10minutemail",
 "description": "Free, temporary email for testing.",
 "docs_url": "https://10minutemail.com",
 "website": "https://10minutemail.com",
 "category": "Email",
 "auth": null,
 "pricing_free": "Free, temporary email for testing.",
 "free_tier_known": true,
 "health": null,
 "provenance": [
  "free-for-dev"
 ],
 "source_ids": {},
 "extra": {}
}
```

## Data-quality notes and gaps

- **Free-tier coverage is uneven.** Only freepublicapis ships structured pricing/quota data per API; free-for-dev entries describe free tiers in prose. publicapis.io, apis.guru, and the public-apis list carry no per-entry free-limit data — those entries are tagged `free_tier_known: false`, not dropped.
- **Dedupe is name-based.** Same service under different names across directories (e.g. 'Alpha Vantage' vs 'AlphaVantage API') may appear twice; domain tie-breaking reduces but does not eliminate this.
- **Descriptions vary in quality.** Directory blurbs are marketing copy; treat them as leads, not verified claims. Free-tier verification rule still applies before adding anything to the toolkit.
- **apis.guru skews enterprise.** Its ~2.5k OpenAPI-described providers include many paid-only APIs; they are kept for the docs/spec links, with `free_tier_known: false`.
- **Scraper rot risk.** freepublicapis and publicapis.io embed data in page structure (`__NUXT_DATA__` / `__NEXT_DATA__`); a redesign breaks the parsers. The merge step fails loudly if any source drops below 50% of its record floor.

## Runtime

- freepublicapis: ~750 detail pages at 0.5s politeness delay.
- publicapis.io: 44 category pages. apis.guru: 1 JSON file. GitHub lists: 2 shallow clones.
- Recommended refresh cadence: twice a month.
