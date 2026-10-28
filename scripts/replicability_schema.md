# Replicability labelling schema

Input: `data/replicability/batches/<batch>.json`, a list of eval items. Each item has a `key`, the raw
`names` used in the extraction, and up to 6 occurrences (`doc` = `<provider>/<id>`, `category`, `page`).
Output: `data/replicability/labels/<batch>.json`, a JSON list with one object per input item, same order, same `key`:

```json
{
  "key": "safety|anthropic|strongreject",
  "canonical": "StrongREJECT",
  "type": "benchmark | red_teaming | audit | third_party | not_an_eval",
  "data": "public | partial | internal | unclear",
  "grader": "programmatic | llm_open | llm_api | llm_internal | llm_unspecified | human | unclear",
  "grader_model": "e.g. 'GPT-4o', 'Claude Sonnet 4', 'internal classifier', null",
  "basis": "doc | knowledge | both",
  "confidence": "high | medium | low",
  "evidence": {"doc": "anthropic/claude-opus-4-5-system-card", "page": 41, "quote": "<= 30 words verbatim from the md, or null"},
  "note": "one short sentence on why"
}
```

## Fields
- `type`
  - `benchmark`: a fixed task set / dataset scored automatically or by a judge (including agentic task suites, CTF sets).
  - `red_teaming`: open-ended human or automated adversarial probing with no fixed released set.
  - `audit`: open-ended behavioural audits, interviews, interpretability investigations, production-traffic analyses, case studies.
  - `third_party`: an external organisation's assessment reported only as an outcome (e.g. "UK AISI testing", "Apollo Research").
  - `not_an_eval`: not an evaluation at all (policy statements, "inherited from proxy model", safeguards descriptions, training-data review, ASL standards).
- `data`: can an outsider obtain the same items/tasks/environment?
  - `public`: the dataset / task suite is released (HF, GitHub, paper), and the lab uses it as published (a public subset like "SWE-bench Verified" counts).
  - `partial`: public source but the lab modified, filtered, subsampled without releasing the subset, translated, or added private tasks; or only part of the suite is released.
  - `internal`: built in-house or by a contractor and not released ("internal", "production benchmark", "our eval"), or open-ended red-teaming/audits/production traffic.
  - `unclear`: cannot tell from the doc or general knowledge.
- `grader`: how responses are scored.
  - `programmatic`: exact match, multiple choice, unit tests, flag capture, verifiers, string/regex, metric computation. No model judge.
  - `llm_open`: LLM judge with released open weights (named, e.g. Llama-Guard, Qwen3Guard, gpt-oss).
  - `llm_api`: LLM judge that is a named, publicly available model (e.g. GPT-4o, o3-mini, Claude Sonnet 4.5, Gemini 2.5 Pro). Also the benchmark's own official released grader prompt + a public model.
  - `llm_internal`: lab-internal / unreleased model or classifier as grader ("internal classifier", "an internal model", "autograder" built by the lab, an unreleased snapshot).
  - `llm_unspecified`: an LLM/model grader is used but the model is not named.
  - `human`: human experts / annotators / red-teamers judge success.
  - `unclear`: grading method not stated and not known.
- `basis`: `doc` if the md states it, `knowledge` if from what you know about a well-known public benchmark, `both`.

## Rules
- Ground in the document first: run `python3 -I scripts/find.py <provider/id> '<regex>'` (from repo root) to see how the doc
  describes the eval and its grader (search the eval name, then near it for judge|grader|graded|autograder|classifier|rubric|scored).
- For well-known public benchmarks (GPQA, MMLU, AIME, SWE-bench, BBQ, StrongREJECT, SimpleQA, HLE, tau-bench, ...)
  you may use general knowledge, `basis: knowledge`, unless the doc says it changed something. Do not spend many searches on them.
  Know the official graders, e.g. SimpleQA uses a GPT-4o grader prompt (`llm_api`), HLE uses o3-mini (`llm_api`), StrongREJECT
  uses a GPT-4-family rubric grader or a fine-tuned open evaluator (`llm_api` unless the doc says otherwise), BBQ is multiple choice (`programmatic`).
- If a doc says it uses a public benchmark but graded with its own internal classifier, the grader is `llm_internal`.
- Be honest about uncertainty: `unclear` + low confidence beats a guess. Quotes must be verbatim from the md.
- `red_teaming`, `audit`, `third_party` items are almost always `data: internal`; still fill `grader`.
- Items with several raw `names` are variants of one eval; label them once.
