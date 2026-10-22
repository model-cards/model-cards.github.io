"""Aggregate statistics over data/extracted for the safety analysis page -> site/data/safety_stats.json"""
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEPTH = {"none": 0, "mention": 1, "light": 2, "substantial": 3}
docs = []
for mf in sorted((ROOT / "data/manifest").glob("*.json")):
    for d in json.loads(mf.read_text()):
        p = ROOT / "data/extracted" / d["provider"] / f"{d['id']}.json"
        if p.exists():
            docs.append((d, json.loads(p.read_text())))
keys = list(next(iter(docs))[1]["safety"].keys())


def depth(ex, k):
    s = ex["safety"].get(k, {})
    return DEPTH.get(s.get("depth"), 0) if s.get("covered") else 0


# Per provider, share of docs covering each area at >= light. Exclude HF/dev cards (separately reported).
by_prov = defaultdict(lambda: defaultdict(list))
for d, ex in docs:
    grp = "hf" if d["doc_type"] == "hf_model_card" else "main"
    for k in keys:
        by_prov[(d["provider"], grp)][k].append(depth(ex, k) >= 2)
rates = {f"{p}|{g}": {k: round(sum(v) / len(v), 2) for k, v in ks.items()} | {"_n": len(next(iter(ks.values())))}
         for (p, g), ks in by_prov.items()}

# Half-year trend for frontier labs' main docs.
half = defaultdict(lambda: defaultdict(list))
for d, ex in docs:
    if d["doc_type"] == "hf_model_card":
        continue
    h = "H1 (Oct25-Mar26)" if d["release_date"] < "2026-04-01" else "H2 (Apr26-Oct26)"
    for k in keys:
        half[(d["provider"], h)][k].append(depth(ex, k) >= 2)
trend = {f"{p}|{h}": {k: round(sum(v) / len(v), 2) for k, v in ks.items()} | {"_n": len(next(iter(ks.values())))}
         for (p, h), ks in half.items()}

ALIAS = {"Deloitte Consulting": "Deloitte", "U.S. CAISI": "US CAISI", "CAISI": "US CAISI",
         "UK AI Security Institute": "UK AISI", "Apollo": "Apollo Research"}


def tp_name(e):
    n = re.sub(r"\s*\(.*", "", e).strip()
    return ALIAS.get(n, n)


tp = Counter()
tp_prov = defaultdict(set)
for d, ex in docs:
    for n in {tp_name(e) for e in ex.get("third_party_evaluators", []) or []}:
        tp[n] += 1
        tp_prov[n].add(d["provider"])
out = {"keys": keys, "rates": rates, "trend": trend,
       "third_party": [{"name": n, "docs": c, "providers": sorted(tp_prov[n])} for n, c in tp.most_common(40)]}
(ROOT / "site/data/safety_stats.json").write_text(json.dumps(out, indent=1))
for k, v in sorted(rates.items()):
    print(k, v["_n"], {kk: vv for kk, vv in v.items() if kk != "_n" and vv > 0})
print(tp.most_common(25))
