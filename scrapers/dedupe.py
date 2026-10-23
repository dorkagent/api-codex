"""Dedupe v2.1: rule 2 with guardrails. Pure stdlib, zero tokens."""
import json, os, re, difflib
from urllib.parse import urlparse
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.join(HERE, "..")

cat = json.load(open(os.path.join(BASE, 'catalog.json')))

def dom(u):
    try: return (urlparse(u or '').hostname or '').lower().removeprefix('www.')
    except Exception: return ''
def norm(n):
    n = (n or '').lower()
    n = re.sub(r'\(rapidapi\)', '', n)
    n = re.sub(r'\b(apis?|free|official|public)\b', '', n)
    return re.sub(r'[^a-z0-9]+', '', n).strip()

# docs-aggregator domains: host docs for thousands of unrelated APIs, not providers
JUNK_DOMAINS = {'api.apis.guru', 'github.com', 'documenter.getpostman.com',
                'rapidapi.com', 'stoplight.io', 'readme.io'}

AGG_LISTING = {'rapidapi.com'}
quarantined, kept = [], []
for e in cat:
    ds = {dom(e.get('website') or ''), dom(e.get('docs_url') or '')}
    if ds & AGG_LISTING:
        e['quarantine_reason'] = 'rapidapi-marketplace-listing'
        quarantined.append(e)
    else:
        kept.append(e)

# Rule 1: normalized-name merge (unchanged)
groups = defaultdict(list)
for e in kept: groups[norm(e['name'])].append(e)
merged, merges_log = [], []
for key, es in groups.items():
    if len(es) == 1: merged.append(es[0]); continue
    base = max(es, key=lambda x: len(x.get('description') or ''))
    for other in es:
        if other is base: continue
        base['provenance'] = sorted(set(base.get('provenance', [])) | set(other.get('provenance', [])))
        for f in ('docs_url', 'website', 'pricing_free'):
            if not base.get(f) and other.get(f): base[f] = other[f]
        merges_log.append(('r1', base['name'], other['name']))
    merged.append(base)

# Rule 2 (guardrailed): same provider domain + strong name similarity
by_dom = defaultdict(list)
for e in merged:
    d = dom(e.get('website') or '') or dom(e.get('docs_url') or '')
    if d and d not in JUNK_DOMAINS: by_dom[d].append(e)

DENYLIST = {tuple(sorted(p)) for p in [('activedirectory', 'activedirectoryb2c')]}

def strong_match(na, nb):
    if len(na) < 4 or len(nb) < 4: return False
    if tuple(sorted((na, nb))) in DENYLIST: return False
    if na == nb: return True
    sim = difflib.SequenceMatcher(None, na, nb).ratio()
    if sim > 0.9: return True
    # clean containment: one is the other plus a small suffix/prefix
    if (na.startswith(nb) or nb.startswith(na)) and abs(len(na)-len(nb)) <= 4:
        return True
    return False

final, r2 = [], 0
for d, es in by_dom.items():
    if len(es) < 2: final.extend(es); continue
    used = set()
    for i, a in enumerate(es):
        if i in used: continue
        na = norm(a['name'])
        for j in range(i+1, len(es)):
            if j in used: continue
            if strong_match(na, norm(es[j]['name'])):
                for f in ('docs_url', 'website', 'pricing_free'):
                    if not a.get(f) and es[j].get(f): a[f] = es[j][f]
                a['provenance'] = sorted(set(a.get('provenance', [])) | set(es[j].get('provenance', [])))
                merges_log.append(('r2', a['name'], es[j]['name'], d))
                used.add(j); r2 += 1
        final.append(a); used.add(i)
# entries on junk/no domains pass through untouched
touched = {id(e) for e in final}
for e in merged:
    if id(e) not in touched: final.append(e)

json.dump(final, open(os.path.join(BASE, 'catalog_v2.json'), 'w'), indent=1)
json.dump(quarantined, open(os.path.join(BASE, 'quarantined.json'), 'w'), indent=1)
print(f"input {len(cat)} -> quarantined {len(quarantined)} -> final {len(final)}")
print(f"rule1 merges: {sum(1 for m in merges_log if m[0]=='r1')}, rule2 merges: {r2}")
print("rule2 sample:")
for m in [m for m in merges_log if m[0]=='r2'][:15]: print("  ", m[1:])
