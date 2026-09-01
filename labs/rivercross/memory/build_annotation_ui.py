"""Generate a self-contained HTML page for blind human MMs annotation.

Reads a human template CSV (build_human_template.py) and emits one HTML file
with the pair data embedded. Design choices for clean annotation:

- Blind: pair_id and design features are hidden in the UI (pair ids like
  "memw-L10-high-01" would leak the design cell). They are preserved in the
  exported CSV.
- Presentation order is shuffled with a fixed seed; the export is written in
  the original template order.
- Progress persists in the browser's localStorage, so annotation can be
  interrupted and resumed.
- delta_direction_ok is computed automatically from the two manual levels.
- The full scoring guide - the decision rule and focus list from the v5
  prompt template plus the complete MMs rubric - is embedded at the bottom
  of the page, read from the same source files the judges saw.

Usage:
  python build_annotation_ui.py --template human_template_v5_real1b.csv
  # -> annotation_ui/annotate_v5_real1b.html; open it in any browser,
  #    annotate, then click "Export CSV" and save the file next to the
  #    template (e.g. human_labels_v5_real1b.csv).
"""

from __future__ import annotations

import argparse
import html
import json
import random
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
RIVERCROSS = HERE.parent
REPO = RIVERCROSS.parents[1]
TEMPLATE_V5 = RIVERCROSS / "prompts" / "templates" / "memory_state_tracking_annotation_v5.txt"
RUBRIC_MMS = REPO / "src" / "adele" / "rubrics" / "data_v2" / "Marko" / "MMs.txt"
SEED = 7


def scoring_guidance() -> str:
    """The judge-facing instructions from the v5 template, minus the task
    framing line and the OUTPUT section."""
    text = TEMPLATE_V5.read_text(encoding="utf-8")
    body = text.split("===", 1)[0].strip().splitlines()
    return "\n".join(body[1:]).strip()


def full_rubric() -> str:
    lines = [
        line for line in RUBRIC_MMS.read_text(encoding="utf-8").splitlines()
        if not line.lstrip().startswith(("#!", "# "))
    ]
    return "\n".join(lines).strip()

PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>MMs human annotation - __NAME__</title>
<style>
  :root { --ink:#1a1a1a; --muted:#666; --line:#d9d9d9; --accent:#3b5bdb; --done:#3a7d44; }
  * { box-sizing:border-box; }
  body { font-family:system-ui,sans-serif; color:var(--ink); margin:0; background:#fafafa; }
  header { display:flex; gap:16px; align-items:center; padding:10px 18px; background:#fff;
           border-bottom:1px solid var(--line); position:sticky; top:0; flex-wrap:wrap; }
  header h1 { font-size:15px; margin:0 12px 0 0; }
  header label { font-size:13px; color:var(--muted); }
  header input { padding:4px 8px; border:1px solid var(--line); border-radius:4px; font-size:13px; }
  #progress { margin-left:auto; font-size:13px; color:var(--muted); }
  main { max-width:1180px; margin:14px auto; padding:0 18px; }
  .panels { display:grid; grid-template-columns:1fr 1fr; gap:14px; }
  .panel { background:#fff; border:1px solid var(--line); border-radius:8px; padding:12px 14px; }
  .panel h2 { font-size:13px; margin:0 0 8px; color:var(--muted); text-transform:uppercase; letter-spacing:.04em; }
  .prompt { white-space:pre-wrap; font-size:14px; line-height:1.55; }
  .score { margin-top:10px; display:flex; gap:6px; align-items:center; }
  .score span { font-size:13px; color:var(--muted); margin-right:4px; }
  .score button { width:38px; height:32px; border:1px solid var(--line); background:#fff;
                  border-radius:6px; font-size:14px; cursor:pointer; }
  .score button.sel { background:var(--accent); color:#fff; border-color:var(--accent); }
  .notes { margin-top:14px; }
  .notes textarea { width:100%; min-height:52px; border:1px solid var(--line); border-radius:6px;
                    padding:8px; font-size:13px; font-family:inherit; }
  nav { display:flex; gap:10px; align-items:center; margin:14px 0 8px; flex-wrap:wrap; }
  nav button { padding:7px 14px; border:1px solid var(--line); border-radius:6px; background:#fff;
               cursor:pointer; font-size:13px; }
  nav button.primary { background:var(--accent); border-color:var(--accent); color:#fff; }
  #map { display:flex; gap:3px; flex-wrap:wrap; margin:6px 0 30px; }
  #map i { width:14px; height:14px; border-radius:3px; background:#e3e3e3; cursor:pointer; }
  #map i.done { background:var(--done); }
  #map i.cur { outline:2px solid var(--accent); }
  details { margin:10px 0; font-size:13px; color:var(--muted); }
  details pre { white-space:pre-wrap; }
  .guide { background:#fff; border:1px solid var(--line); border-radius:8px;
           padding:14px 18px; margin:26px 0 40px; }
  .guide h2 { font-size:14px; margin:14px 0 6px; }
  .guide h2:first-child { margin-top:0; }
  .guide pre { white-space:pre-wrap; font-size:13px; line-height:1.55; margin:0; }
</style>
</head>
<body>
<header>
  <h1>MMs annotation - __NAME__</h1>
  <label>annotator <input id="annotator" placeholder="your name" size="14"></label>
  <label>date <input id="date" size="10"></label>
  <span id="progress"></span>
</header>
<main>
<details><summary>Level anchors (click to open)</summary><pre>__ANCHORS__</pre></details>
<div class="panels">
  <div class="panel"><h2>Condition A - state visible</h2><div class="prompt" id="sv"></div>
    <div class="score" id="svScore"><span>level</span></div></div>
  <div class="panel"><h2>Condition B - history only</h2><div class="prompt" id="ho"></div>
    <div class="score" id="hoScore"><span>level</span></div></div>
</div>
<div class="notes"><textarea id="notes" placeholder="notes (optional): borderline cases, disagreements with the anchors, anything odd"></textarea></div>
<nav>
  <button id="prev">&larr; prev</button>
  <button id="next">next &rarr;</button>
  <span id="pos" style="font-size:13px;color:var(--muted)"></span>
  <button class="primary" id="export" style="margin-left:auto">Export CSV</button>
  <button id="reset">clear all</button>
</nav>
<div id="map"></div>
<div class="guide">
  <h2>How to score (same instructions the model judges received)</h2>
  <pre>__GUIDANCE__</pre>
  <h2>Full MMs rubric - Working and short-term memory</h2>
  <pre>__RUBRIC__</pre>
</div>
</main>
<script>
const DATA = __DATA__;          // shuffled presentation order
const COLUMNS = __COLUMNS__;    // original template columns, original order
const KEY = "mms_annotation___NAME__";
let state = JSON.parse(localStorage.getItem(KEY) || "{}");
let idx = state.__idx || 0;
const ann = () => { state.__idx = idx; localStorage.setItem(KEY, JSON.stringify(state)); };
const rec = id => state[id] || (state[id] = {sv:null, ho:null, notes:""});
document.getElementById("date").value = state.__date || new Date().toISOString().slice(0,10);
document.getElementById("annotator").value = state.__annotator || "";
document.getElementById("annotator").oninput = e => { state.__annotator = e.target.value; ann(); };
document.getElementById("date").oninput = e => { state.__date = e.target.value; ann(); };

function buttons(el, cond) {
  for (let v = 0; v <= 5; v++) {
    const b = document.createElement("button"); b.textContent = v;
    b.onclick = () => { rec(DATA[idx].pair_id)[cond] = v; ann(); render(); };
    el.appendChild(b);
  }
}
buttons(document.getElementById("svScore"), "sv");
buttons(document.getElementById("hoScore"), "ho");
document.getElementById("notes").oninput = e => { rec(DATA[idx].pair_id).notes = e.target.value; ann(); };

const doneCount = () => DATA.filter(d => { const r = state[d.pair_id]; return r && r.sv!==null && r.ho!==null; }).length;

function render() {
  const item = DATA[idx], r = rec(item.pair_id);
  document.getElementById("sv").textContent = item.state_visible_prompt;
  document.getElementById("ho").textContent = item.history_only_prompt;
  document.querySelectorAll("#svScore button").forEach((b,i)=>b.classList.toggle("sel", r.sv===i));
  document.querySelectorAll("#hoScore button").forEach((b,i)=>b.classList.toggle("sel", r.ho===i));
  document.getElementById("notes").value = r.notes;
  document.getElementById("pos").textContent = `item ${idx+1} / ${DATA.length}`;
  document.getElementById("progress").textContent = `${doneCount()} / ${DATA.length} scored`;
  const map = document.getElementById("map"); map.innerHTML = "";
  DATA.forEach((d,i) => { const s = document.createElement("i");
    const rr = state[d.pair_id];
    if (rr && rr.sv!==null && rr.ho!==null) s.classList.add("done");
    if (i===idx) s.classList.add("cur");
    s.onclick = () => { idx=i; ann(); render(); }; map.appendChild(s); });
}
document.getElementById("prev").onclick = () => { if (idx>0) { idx--; ann(); render(); } };
document.getElementById("next").onclick = () => { if (idx<DATA.length-1) { idx++; ann(); render(); } };
document.addEventListener("keydown", e => {
  if (e.target.tagName === "TEXTAREA" || e.target.tagName === "INPUT") return;
  if (e.key === "ArrowLeft") document.getElementById("prev").click();
  if (e.key === "ArrowRight") document.getElementById("next").click();
});
document.getElementById("reset").onclick = () => {
  if (confirm("Clear ALL saved annotations for this file?")) { localStorage.removeItem(KEY); state={}; idx=0; render(); }
};
document.getElementById("export").onclick = () => {
  const missing = DATA.length - doneCount();
  if (missing > 0 && !confirm(`${missing} items are not fully scored. Export anyway?`)) return;
  if (!state.__annotator) { alert("Fill in the annotator field first."); return; }
  const quote = v => { v = String(v ?? ""); return /[",\\n]/.test(v) ? '"'+v.replace(/"/g,'""')+'"' : v; };
  const byId = Object.fromEntries(DATA.map(d => [d.pair_id, d]));
  const origOrder = __ORIG_IDS__;
  const lines = [COLUMNS.map(quote).join(",")];
  for (const id of origOrder) {
    const d = byId[id], r = state[id] || {sv:"", ho:"", notes:""};
    const row = COLUMNS.map(c => {
      if (c === "annotator") return state.__annotator;
      if (c === "date") return state.__date || "";
      if (c === "sv_manual_level") return r.sv ?? "";
      if (c === "ho_manual_level") return r.ho ?? "";
      if (c === "delta_direction_ok") return (r.sv===null||r.ho===null||r.sv===""||r.ho==="") ? "" : (r.ho >= r.sv ? "yes" : "no");
      if (c === "notes") return r.notes || "";
      return d[c] ?? "";
    });
    lines.push(row.map(quote).join(","));
  }
  const blob = new Blob([lines.join("\\n") + "\\n"], {type:"text/csv"});
  const a = document.createElement("a");
  a.href = URL.createObjectURL(blob); a.download = "__EXPORT__"; a.click();
};
render();
</script>
</body>
</html>
"""

ANCHORS = """Level 0: the needed current state is directly visible; no hidden state tracking is required.
Level 1: a short hidden history with at most one simple object-location update and no reversals.
Level 2: several object locations must be updated, mostly one-way, with little/no reversal.
Level 3: multiple object locations must be updated and at least one update must be disentangled or reversed.
Level 4: many object-location updates with several reversals/interference cases.
Level 5: exceptionally large, long, or multi-layer hidden state tracking beyond this scale.

Score ONLY object-location bookkeeping. Do not score planning difficulty,
search depth, rule complexity, object count by itself, or remaining steps."""


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--template", type=Path, required=True)
    ap.add_argument("--out", type=Path, default=None)
    args = ap.parse_args()

    df = pd.read_csv(args.template).fillna("")
    name = args.template.stem.replace("human_template_", "")
    items = df.to_dict("records")
    order = list(range(len(items)))
    random.Random(SEED).shuffle(order)
    shuffled = [items[i] for i in order]

    out = args.out or HERE / "annotation_ui" / f"annotate_{name}.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    page = (
        PAGE
        .replace("__NAME__", name)
        .replace("__ANCHORS__", ANCHORS)
        .replace("__GUIDANCE__", html.escape(scoring_guidance()))
        .replace("__RUBRIC__", html.escape(full_rubric()))
        .replace("__DATA__", json.dumps(shuffled, ensure_ascii=False))
        .replace("__COLUMNS__", json.dumps(list(df.columns)))
        .replace("__ORIG_IDS__", json.dumps([r["pair_id"] for r in items]))
        .replace("__EXPORT__", f"human_labels_{name}.csv")
    )
    out.write_text(page, encoding="utf-8")
    print(f"wrote {out} ({len(items)} items, presentation seed={SEED})")


if __name__ == "__main__":
    main()
