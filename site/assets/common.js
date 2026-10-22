// Shared helpers for every page: header/nav, theme toggle, data loading, tooltips.
const PROVIDERS = {
  anthropic: "Anthropic",
  openai: "OpenAI",
  gemini: "Google Gemini",
  glm: "Zhipu GLM",
  kimi: "Moonshot Kimi",
  qwen: "Alibaba Qwen",
};
const PROVIDER_ORDER = Object.keys(PROVIDERS);
const DOC_TYPES = {
  system_card: "System card",
  model_card: "Model card",
  addendum: "Addendum",
  tech_report: "Tech report",
  safety_report: "Safety report",
  hf_model_card: "HF / dev model card",
};

function pcolor(p) { return `var(--p-${p})`; }

function esc(s) {
  return String(s ?? "").replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
}

function fmtDate(d) {
  if (!d) return "";
  const dt = new Date(d + "T00:00:00Z");
  return dt.toLocaleDateString("en-US", { year: "numeric", month: "short", day: "numeric", timeZone: "UTC" });
}

async function getJSON(path) {
  const r = await fetch(path);
  if (!r.ok) throw new Error(`${path}: ${r.status}`);
  return r.json();
}

function cardLink(id, page) {
  return `card.html?id=${encodeURIComponent(id)}${page ? `#page-${page}` : ""}`;
}

function header(active) {
  const links = [
    ["index.html", "Catalog"],
    ["compare.html", "Compare evals"],
    ["safety.html", "Safety evals"],
    ["about.html", "About"],
  ];
  const el = document.createElement("header");
  el.className = "top";
  el.innerHTML = `<div class="wrap">
    <a class="brand" href="index.html">model-cards <span>· frontier model documentation archive</span></a>
    <nav class="main">${links.map(([h, t]) => `<a href="${h}" class="${h === active ? "on" : ""}">${t}</a>`).join("")}</nav>
    <button class="theme-btn" type="button" aria-label="Toggle theme">◐</button></div>`;
  document.body.prepend(el);
  el.querySelector(".theme-btn").onclick = () => {
    const cur = document.documentElement.dataset.theme
      || (matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light");
    const next = cur === "dark" ? "light" : "dark";
    document.documentElement.dataset.theme = next;
    try { localStorage.setItem("theme", next); } catch (e) {}
  };
  const f = document.createElement("footer");
  f.innerHTML = `<div class="wrap">Documents are © their publishers and archived here for research and comparison; follow the source links for canonical versions.
    Markdown was produced by OCR (Mistral OCR) and may contain conversion errors. Extracted evaluation data is machine-assisted. Check figures against the PDF.</div>`;
  document.body.append(f);
}
try { const t = localStorage.getItem("theme"); if (t) document.documentElement.dataset.theme = t; } catch (e) {}

// One floating tooltip shared by all charts.
const tip = (() => {
  let el;
  return {
    show(html, ev) {
      if (!el) { el = document.createElement("div"); el.className = "tip"; document.body.append(el); }
      el.innerHTML = html; el.style.display = "block";
      const x = Math.min(ev.clientX + 14, innerWidth - el.offsetWidth - 8);
      const y = ev.clientY + 14 + el.offsetHeight > innerHeight ? ev.clientY - el.offsetHeight - 10 : ev.clientY + 14;
      el.style.left = x + "px"; el.style.top = y + "px";
    },
    hide() { if (el) el.style.display = "none"; },
  };
})();
