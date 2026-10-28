"""Collect every eval named in data/extracted into labelling batches -> data/replicability/batches/*.json

Safety evals are keyed per (provider, name) because labs grade the same benchmark differently;
capability benchmarks are keyed by name across labs."""
import json
import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data/replicability/batches"
SIZE = 250


def norm(s):
    return re.sub(r"[^a-z0-9]+", " ", s.lower()).strip()


items = {}
for f in sorted((ROOT / "data/extracted").glob("*/*.json")):
    ex = json.loads(f.read_text())
    p = ex["provider"]
    for cat, s in ex["safety"].items():
        for e in s.get("evals") or []:
            k = f"safety|{p}|{norm(e)}"
            it = items.setdefault(k, {"key": k, "kind": "safety", "provider": p, "names": set(), "occ": []})
            it["names"].add(e)
            it["occ"].append({"doc": f"{p}/{ex['id']}", "category": cat, "page": s.get("page"), "finding": s.get("finding")})
    for b in ex["capability_benchmarks"]:
        k = f"capability|{norm(b['name'])}"
        it = items.setdefault(k, {"key": k, "kind": "capability", "names": set(), "occ": []})
        it["names"].add(b["name"])
        it["occ"].append({"doc": f"{p}/{ex['id']}", "category": b.get("category"), "page": b.get("page"), "setting": b.get("setting")})

groups = defaultdict(list)
for it in items.values():
    it["names"] = sorted(it["names"])
    it["occ"] = it["occ"][:6]  # enough context to locate it
    g = it["provider"] if it["kind"] == "safety" and it["provider"] in ("anthropic", "openai", "gemini") else "other"
    groups[g].append(it)
for f in OUT.glob("*.json"):
    f.unlink()
for g, its in groups.items():
    its.sort(key=lambda x: x["key"])
    n = -(-len(its) // SIZE)
    for i in range(n):
        chunk = its[i * len(its) // n:(i + 1) * len(its) // n]
        (OUT / f"{g}-{i + 1}.json").write_text(json.dumps(chunk, indent=1))
        print(g, i + 1, len(chunk))
