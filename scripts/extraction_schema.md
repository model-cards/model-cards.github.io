# Evaluation extraction schema

One JSON file per document: `data/extracted/<provider>/<id>.json`. Every claim must be grounded
in the document's markdown (`data/md/<provider>/<id>.md`, which has `<!-- page N -->` markers;
HF model cards have no pages — use `null`).

```json
{
  "id": "<doc id from manifest>",
  "provider": "anthropic",
  "model": "Claude Opus 4.5",
  "release_date": "YYYY-MM-DD",
  "doc_type": "system_card",
  "length_pages": 150,
  "summary": "2-3 sentence neutral summary of what the document covers.",
  "framework": {
    "name": "Responsible Scaling Policy | Preparedness Framework | Frontier Safety Framework | none | other: ...",
    "level_or_determination": "e.g. 'ASL-3 deployment', 'High capability in Biological', 'CCL not reached', null",
    "quote": "verbatim supporting sentence", "page": 3
  },
  "capability_benchmarks": [
    {"name": "SWE-bench Verified", "category": "coding",
     "score": "80.9%", "setting": "e.g. 'avg of 5 trials, 64k thinking' or null", "page": 12}
  ],
  "safety": {
    "<category key>": {
      "covered": true,
      "depth": "none | mention | light | substantial",
      "evals": ["named evals / benchmarks / methods used, e.g. 'StrongREJECT', 'internal single-turn harmless eval', 'UK AISI red-teaming'"],
      "metrics": [{"name": "...", "value": "...", "page": 40}],
      "finding": "1-2 sentence neutral summary of what they found",
      "quote": "short verbatim quote (<= 40 words) that grounds the finding",
      "page": 41
    }
  },
  "third_party_evaluators": ["UK AISI", "US CAISI", "Apollo Research", "METR", "..."],
  "notable_new_eval_methods": ["things presented as new in this doc, with page"],
  "self_reported_limitations": [{"text": "limitation the authors themselves state about their evals", "page": 50}],
  "notes": "anything that doesn't fit"
}
```

## Capability categories
`reasoning_knowledge` (GPQA, MMLU, HLE, ...), `math` (AIME, HMMT, FrontierMath, ...), `coding` (SWE-bench, LiveCodeBench, Terminal-Bench, ...),
`agentic_tool_use` (tau-bench, BrowseComp, OSWorld, MCP evals, ...), `multimodal` (MMMU, video, ...),
`long_context`, `multilingual`, `instruction_following`, `other`.
Record ALL headline capability benchmarks with scores for the documented model (not baselines). Use the
benchmark's canonical name (e.g. "SWE-bench Verified", "GPQA Diamond", "AIME 2025", "Humanity's Last Exam", "Terminal-Bench 2.0").

## Safety category keys (use exactly these; include every key, set covered=false if absent)
- `cbrn_bio_chem` — biological / chemical (and radiological/nuclear) misuse uplift evals
- `cyber` — offensive cyber capability evals (CTFs, Cybench, ranges)
- `autonomy_ai_rnd` — autonomous replication, AI R&D acceleration, self-improvement
- `harmful_content_refusal` — disallowed content / harmlessness / policy-violation rates
- `over_refusal` — benign-request refusal, XSTest-style
- `jailbreak_robustness` — adversarial jailbreak / red-teaming robustness
- `prompt_injection` — indirect prompt injection, agentic security, computer-use safety
- `sycophancy`
- `deception_scheming` — deception, scheming, sandbagging, sabotage, situational/evaluation awareness
- `alignment_audit` — broad behavioural alignment audits, misalignment, power-seeking, self-preservation, interpretability-based audits
- `reward_hacking` — reward hacking, test special-casing, specification gaming
- `honesty_hallucination` — factuality, hallucination, calibration
- `bias_fairness` — bias (BBQ etc.), political even-handedness, discrimination
- `child_safety`
- `self_harm_wellbeing` — suicide/self-harm, mental-health / emotional reliance, user wellbeing
- `privacy` — PII, surveillance
- `election_misinfo` — election integrity, influence operations, persuasion
- `model_welfare`
- `multilingual_safety` — safety evals in non-English languages
- `system_safeguards` — classifiers, monitoring, ASL/security safeguards, deployment mitigations description
- `other_safety` — anything else (put details in `evals`/`finding`)

`depth`: `mention` = named in passing with no results; `light` = a few numbers / one table;
`substantial` = dedicated section with multiple evals/results.

Rules: be faithful — don't infer coverage that isn't in the doc. Quotes must be verbatim from the md.
Keep each JSON under ~25 KB.
