# model-cards

A static site archiving a year (Oct 2025 – Oct 2026) of model cards, system cards, safety reports and
technical reports from Anthropic, OpenAI, Google Gemini, Zhipu GLM, Moonshot Kimi and Alibaba Qwen. Each
document is available as a PDF and as markdown, with extracted evaluations and a cross-lab safety-evaluation analysis.

- `site/`: the deployable static site (no build step). `site/cards/<provider>/` holds the PDFs and markdown, and `site/data/` holds the JSON.
- `data/manifest/<provider>.json`: document metadata (source URLs, dates, notes).
- `data/md/`: OCR markdown with `<!-- page N -->` markers.
- `data/extracted/`: per-document evaluation extraction (schema: `scripts/extraction_schema.md`).
- `scripts/convert.py`: PDF/HTML → markdown via Mistral OCR. It needs `MISTRAL_API_KEY` in `.env`, which is git-ignored.
- `scripts/build_site.py`: copies documents into `site/` and writes `site/data/cards.json` and `evals.json`.
- `scripts/analyze.py`: writes `site/data/safety_stats.json`.
- `scripts/find.py`: grep a document with page numbers (used to verify citations).

## Rebuild

```bash
uv venv .venv && uv pip install --python .venv/bin/python requests
.venv/bin/python -I scripts/convert.py        # only new docs; cached otherwise
python3 -I scripts/build_site.py && python3 -I scripts/analyze.py
cd site && python3 -m http.server 8000
```

## Deploy

`.github/workflows/pages.yml` publishes `site/` to GitHub Pages on every push to `main`. To serve it at
`https://model-cards.github.io`, push this repo as `model-cards/model-cards.github.io` and set
Settings → Pages → Source to "GitHub Actions".
