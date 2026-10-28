"""Join eval labels (data/replicability/labels) with every eval occurrence in data/extracted
-> site/data/replicability.json. Tiers are assigned here so the rules live in one place."""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OPEN_GRADERS = {"programmatic", "llm_open", "llm_api"}


def norm(s):
    return re.sub(r"[^a-z0-9]+", " ", s.lower()).strip()


def tier(lb):
    if lb["type"] == "not_an_eval":
        return "excluded"
    if lb["data"] == "public":
        return "replicable" if lb["grader"] in OPEN_GRADERS else "closed_judge"
    if lb["data"] == "partial":
        return "partial_data"
    if lb["data"] == "internal":
        return "closed_data"
    return "unclear"


labels = {}
for f in sorted((ROOT / "data/replicability/labels").glob("*.json")):
    for lb in json.loads(f.read_text()):
        labels[lb["key"]] = lb
# Manual fixes from the cross-batch consistency check (same eval labelled differently by different agents).
for k, v in json.loads((ROOT / "data/replicability/overrides.json").read_text()).items():
    labels[k].update(v)

docs, evals, eidx, occ, missing = [], [], {}, [], set()
for mf in sorted((ROOT / "data/manifest").glob("*.json")):
    for d in json.loads(mf.read_text()):
        p = ROOT / "data/extracted" / d["provider"] / f"{d['id']}.json"
        if not p.exists():
            continue
        ex = json.loads(p.read_text())
        di = len(docs)
        docs.append({k: d[k] for k in ("id", "provider", "model", "doc_type", "release_date")})
        seen = set()
        rows = [(f"safety|{d['provider']}|{norm(e)}", cat, s.get("page"))
                for cat, s in ex["safety"].items() for e in s.get("evals") or []]
        rows += [(f"capability|{norm(b['name'])}", b.get("category"), b.get("page")) for b in ex["capability_benchmarks"]]
        for key, cat, page in rows:
            if key not in labels:
                missing.add(key)
                continue
            if (key, cat) in seen:  # same eval listed twice under one area / benchmark repeated per setting
                continue
            seen.add((key, cat))
            if key not in eidx:
                lb = labels[key]
                eidx[key] = len(evals)
                evals.append({"key": key, "kind": key.split("|")[0], "tier": tier(lb),
                              **{k: lb.get(k) for k in ("canonical", "type", "data", "grader", "grader_model",
                                                       "basis", "confidence", "evidence", "note")}})
            occ.append([di, eidx[key], cat, page])

out = {"docs": docs, "evals": evals, "occ": occ}
(ROOT / "site/data/replicability.json").write_text(json.dumps(out, separators=(",", ":")))
print(f"{len(docs)} docs, {len(evals)} evals, {len(occ)} occurrences, {len(missing)} unlabelled keys")
from collections import Counter
for kind in ("safety", "capability"):
    c = Counter(evals[e]["tier"] for _, e, _, _ in occ if evals[e]["kind"] == kind)
    print(kind, dict(c))
