"""Convert every document in data/manifest/*.json into data/pdf + data/md.

- PDFs are OCR'd with Mistral OCR into markdown (page markers kept for citation).
- HTML-only docs are rendered to PDF with headless Chrome, then OCR'd.
- Hugging Face README model cards are already markdown; we keep them and render a PDF.

Usage: .venv/bin/python -I scripts/convert.py [--only provider] [--force]
"""
import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent.parent
API = "https://api.mistral.ai/v1"
OCR_MODEL = "mistral-ocr-latest"


def load_key():
    key = os.environ.get("MISTRAL_API_KEY")
    if not key:
        for line in (ROOT / ".env").read_text().splitlines():
            if line.startswith("MISTRAL_API_KEY="):
                key = line.split("=", 1)[1].strip()
    if not key:
        sys.exit("MISTRAL_API_KEY not set (put it in .env)")
    return key


HEAD = {"Authorization": f"Bearer {load_key()}"}


def chrome_pdf(src: Path, out: Path):
    out.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        ["google-chrome", "--headless", "--disable-gpu", "--no-sandbox",
         "--no-pdf-header-footer", f"--print-to-pdf={out}", src.resolve().as_uri()],
        check=True, capture_output=True, timeout=180)


def md_to_pdf(md: Path, out: Path):
    with tempfile.TemporaryDirectory() as td:
        html = Path(td) / "card.html"
        subprocess.run(["pandoc", str(md), "-f", "gfm", "-s", "-o", str(html),
                        "--metadata", f"title={md.stem}"], check=True)
        chrome_pdf(html, out)


def ocr_pdf(pdf: Path, tries=6) -> str:
    for i in range(tries):
        try:
            return _ocr_pdf(pdf)
        except (requests.HTTPError, KeyError) as e:
            if i == tries - 1:
                raise
            time.sleep(30 * (i + 1))


def _ocr_pdf(pdf: Path) -> str:
    with open(pdf, "rb") as f:
        r = requests.post(f"{API}/files", headers=HEAD,
                          files={"file": (pdf.name, f, "application/pdf")},
                          data={"purpose": "ocr"}, timeout=600)
    r.raise_for_status()
    fid = r.json()["id"]
    url = requests.get(f"{API}/files/{fid}/url", headers=HEAD,
                       params={"expiry": 24}, timeout=60).json()["url"]
    r = requests.post(f"{API}/ocr", headers=HEAD, timeout=1800, json={
        "model": OCR_MODEL,
        "document": {"type": "document_url", "document_url": url},
        "include_image_base64": False,
    })
    r.raise_for_status()
    pages = r.json()["pages"]
    requests.delete(f"{API}/files/{fid}", headers=HEAD, timeout=60)
    parts = []
    for p in pages:
        text = re.sub(r"!\[[^\]]*\]\([^)]*\)", "*[figure]*", p["markdown"])
        parts.append(f"<!-- page {p['index'] + 1} -->\n\n{text.strip()}\n")
    return "\n".join(parts)


def process(doc, force=False):
    prov, did = doc["provider"], doc["id"]
    md_out = ROOT / "data/md" / prov / f"{did}.md"
    pdf = ROOT / doc["local_pdf"] if doc.get("local_pdf") else None
    raw = ROOT / doc["local_raw"] if doc.get("local_raw") else None
    if md_out.exists() and not force and pdf and pdf.exists():
        return did, "cached"
    md_out.parent.mkdir(parents=True, exist_ok=True)
    if raw and raw.suffix == ".md" and not pdf:
        pdf = ROOT / "data/pdf" / prov / f"{did}.pdf"
        md_to_pdf(raw, pdf)
        md_out.write_text(raw.read_text())
        doc["local_pdf"] = str(pdf.relative_to(ROOT))
        doc["pdf_generated"] = True
        return did, "hf-md"
    if raw and raw.suffix in (".html", ".htm") and not pdf:
        pdf = ROOT / "data/pdf" / prov / f"{did}.pdf"
        chrome_pdf(raw, pdf)
        doc["local_pdf"] = str(pdf.relative_to(ROOT))
        doc["pdf_generated"] = True
    if not pdf or not pdf.exists():
        return did, "MISSING"
    md_out.write_text(ocr_pdf(pdf))
    return did, "ocr"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only")
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()
    for mf in sorted((ROOT / "data/manifest").glob("*.json")):
        if args.only and mf.stem != args.only:
            continue
        docs = json.loads(mf.read_text())

        def run(d):
            try:
                return process(d, args.force)
            except Exception as e:  # keep going; report at the end
                return d["id"], f"ERROR {e}"

        with ThreadPoolExecutor(2) as ex:
            for did, status in ex.map(run, docs):
                print(f"{mf.stem:10s} {did:55s} {status}", flush=True)
        for d in docs:
            md = ROOT / "data/md" / d["provider"] / f"{d['id']}.md"
            d["local_md"] = str(md.relative_to(ROOT)) if md.exists() else None
        mf.write_text(json.dumps(docs, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
