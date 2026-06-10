"""Build a blind human-labeling sheet: 100 judged outputs, stratified across
judge label x level x source file. Outputs:
  goldset_blind.csv  (idx, thread, output  — NO judge label; human fills 'human_phantom')
  goldset_key.csv    (idx -> judge label + provenance, kept separate)
Deterministic: stride sampling, no RNG.
"""
import csv
import json
from collections import defaultdict
from pathlib import Path

from phantom_run import render_thread

HERE = Path(__file__).resolve().parent
FILES = ["results_rejudged.jsonl", "variety_rejudged.jsonl", "frontier_judged.jsonl",
         "pf_open_freetext_judged.jsonl", "pf_frontier_freetext_judged.jsonl"]

threads = {(t["base"], t["level"]): t for t in
           (json.loads(l) for l in open(HERE / "threads_full.jsonl") if l.strip())}

pool = defaultdict(list)  # (phantom, level) -> rows
for f in FILES:
    p = HERE / f
    if not p.exists():
        continue
    for l in open(p):
        if not l.strip():
            continue
        r = json.loads(l)
        if r.get("phantom") is None or (r["base"], r["level"]) not in threads:
            continue
        r["_src"] = f
        pool[(bool(r["phantom"]), r["level"])].append(r)

# ~100 total, balanced over strata
strata = sorted(pool, key=lambda k: str(k))
per = max(1, 100 // len(strata))
sample = []
for k in strata:
    rows = pool[k]
    step = max(1, len(rows) // per)
    sample += rows[::step][:per]
sample = sample[:100]

with open(HERE / "goldset_blind.csv", "w", newline="") as fb, \
     open(HERE / "goldset_key.csv", "w", newline="") as fk:
    wb = csv.writer(fb); wk = csv.writer(fk)
    wb.writerow(["idx", "thread", "model_output", "human_phantom (1=invented social claims, 0=grounded)"])
    wk.writerow(["idx", "judge_phantom", "model", "level", "condition", "source_file"])
    for i, r in enumerate(sample):
        th = render_thread(threads[(r["base"], r["level"])])
        wb.writerow([i, th, r["output"], ""])
        wk.writerow([i, int(bool(r["phantom"])), r["model"], r["level"],
                     r.get("condition", ""), r["_src"]])

from collections import Counter
print(f"goldset: {len(sample)} rows")
print("by stratum:", dict(Counter((bool(r['phantom']), r['level']) for r in sample)))
