"""Assemble the static site: copy PDFs/markdown into site/cards and write site/data/*.json.

Usage: python3 -I scripts/build_site.py
"""
import json
import re
import shutil
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "site"

SAFETY_KEYS = [
    "cbrn_bio_chem", "cyber", "autonomy_ai_rnd", "harmful_content_refusal", "over_refusal",
    "jailbreak_robustness", "prompt_injection", "sycophancy", "deception_scheming",
    "alignment_audit", "reward_hacking", "honesty_hallucination", "bias_fairness",
    "child_safety", "self_harm_wellbeing", "privacy", "election_misinfo", "model_welfare",
    "multilingual_safety", "system_safeguards", "other_safety",
]
DEPTH = {"none": 0, "mention": 1, "light": 2, "substantial": 3}

# Canonical benchmark names: key = normalised form, value = display name.
ALIASES = {
    "swebenchverified": "SWE-bench Verified", "swebverified": "SWE-bench Verified",
    "swebenchpro": "SWE-bench Pro", "swebenchmultilingual": "SWE-bench Multilingual",
    "gpqadiamond": "GPQA Diamond", "gpqa": "GPQA Diamond",
    "humanityslastexam": "Humanity's Last Exam", "hle": "Humanity's Last Exam",
    "terminalbench20": "Terminal-Bench 2.0", "terminalbench2": "Terminal-Bench 2.0",
    "aime2025": "AIME 2025", "aime2026": "AIME 2026", "hmmt2025": "HMMT 2025",
    "hmmtfeb2025": "HMMT 2025", "mmmu": "MMMU", "mmmupro": "MMMU-Pro",
    "browsecomp": "BrowseComp", "osworld": "OSWorld", "osworldverified": "OSWorld-Verified",
    "arcagi2": "ARC-AGI-2", "arcagi1": "ARC-AGI-1", "mmlupro": "MMLU-Pro", "mmlu": "MMLU",
    "livecodebench": "LiveCodeBench", "livecodebenchv6": "LiveCodeBench v6",
    "tau2bench": "τ²-bench", "frontiermath": "FrontierMath",
    "simpleqa": "SimpleQA", "mmmlu": "MMMLU", "ifeval": "IFEval", "videommmu": "Video-MMMU",
    "swelancer": "SWE-Lancer", "mcpatlas": "MCP Atlas", "gdpval": "GDPval",
    "vendingbench2": "Vending-Bench 2", "screenspotpro": "ScreenSpot-Pro",
    "charxivreasoning": "CharXiv Reasoning", "finsearchcomp": "FinSearchComp",
}


def norm(name):
    base = re.sub(r"\(.*?\)", "", name).lower().replace("²", "2").replace("τ", "tau")
    return re.sub(r"[^a-z0-9]", "", base)


def canon(name):
    k = norm(name)
    return ALIASES.get(k, name.strip())


def main():
    cards, extracted = [], {}
    for mf in sorted((ROOT / "data/manifest").glob("*.json")):
        for d in json.loads(mf.read_text()):
            prov, did = d["provider"], d["id"]
            out = SITE / "cards" / prov
            out.mkdir(parents=True, exist_ok=True)
            entry = {k: d.get(k) for k in ("id", "provider", "model", "model_family", "doc_type",
                                          "title", "release_date", "source_url", "pdf_url",
                                          "pages", "open_weights", "notes", "pdf_generated")}
            if d.get("local_pdf") and (ROOT / d["local_pdf"]).exists():
                shutil.copy2(ROOT / d["local_pdf"], out / f"{did}.pdf")
                entry["pdf"] = f"cards/{prov}/{did}.pdf"
            if d.get("local_md") and (ROOT / d["local_md"]).exists():
                shutil.copy2(ROOT / d["local_md"], out / f"{did}.md")
                entry["md"] = f"cards/{prov}/{did}.md"
            ex_path = ROOT / "data/extracted" / prov / f"{did}.json"
            if ex_path.exists():
                ex = json.loads(ex_path.read_text())
                for b in ex.get("capability_benchmarks", []):
                    b["canonical"] = canon(b.get("name", ""))
                extracted[did] = ex
                saf = ex.get("safety", {})
                entry["safety_categories_covered"] = sum(
                    1 for k in SAFETY_KEYS if saf.get(k, {}).get("covered")
                    and DEPTH.get(saf[k].get("depth"), 0) >= 1)
                entry["summary"] = ex.get("summary")
                entry["framework"] = (ex.get("framework") or {}).get("name")
                (SITE / "data/extracted").mkdir(parents=True, exist_ok=True)
                (SITE / "data/extracted" / f"{did}.json").write_text(
                    json.dumps(ex, ensure_ascii=False, indent=1))
            cards.append(entry)

    (SITE / "data").mkdir(exist_ok=True)
    (SITE / "data/cards.json").write_text(json.dumps(cards, ensure_ascii=False, indent=1))

    # Aggregate: safety coverage matrix + benchmark table.
    coverage = []
    bench = defaultdict(dict)
    for c in cards:
        ex = extracted.get(c["id"])
        if not ex:
            continue
        saf = ex.get("safety", {})
        coverage.append({
            "id": c["id"], "provider": c["provider"], "model": c["model"],
            "release_date": c["release_date"], "doc_type": c["doc_type"],
            "cells": {k: {"d": DEPTH.get(saf.get(k, {}).get("depth"), 0) if saf.get(k, {}).get("covered") else 0,
                          "f": saf.get(k, {}).get("finding"), "p": saf.get(k, {}).get("page"),
                          "e": saf.get(k, {}).get("evals", [])[:6]} for k in SAFETY_KEYS},
            "third_party": ex.get("third_party_evaluators", []),
        })
        for b in ex.get("capability_benchmarks", []):
            name = b["canonical"]
            if name not in bench[c["id"]]:
                bench[c["id"]][name] = {"score": b.get("score"), "setting": b.get("setting"),
                                        "page": b.get("page"), "category": b.get("category")}
    (SITE / "data/evals.json").write_text(json.dumps(
        {"safety_keys": SAFETY_KEYS, "coverage": coverage, "benchmarks": bench},
        ensure_ascii=False))
    print(f"{len(cards)} cards, {len(extracted)} extracted")


if __name__ == "__main__":
    main()
