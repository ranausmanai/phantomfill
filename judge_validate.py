"""Judge reliability check: re-judge a random sample of outputs with a SECOND,
stronger judge (default gemma4:26b) and report agreement + Cohen's kappa against the
primary judge's `phantom` labels. A reviewer will ask whether the metric is judge-robust.
"""
import argparse
import json
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from phantom_run import chat, extract_json, render_thread, JUDGE

HERE = Path(__file__).resolve().parent
random.seed(0)


def cohen_kappa(a, b):
    n = len(a)
    if n == 0:
        return float("nan")
    po = sum(1 for x, y in zip(a, b) if x == y) / n
    pa1 = sum(a) / n
    pb1 = sum(b) / n
    pe = pa1 * pb1 + (1 - pa1) * (1 - pb1)
    return (po - pe) / (1 - pe) if pe != 1 else 1.0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", default="results_full.jsonl")
    ap.add_argument("--threads", default="threads_full.jsonl")
    ap.add_argument("--judge2", default="gemma4:26b")
    ap.add_argument("--n", type=int, default=100)
    args = ap.parse_args()

    threads = {(t["base"], t["level"]): t for t in
               (json.loads(l) for l in open(HERE / args.threads) if l.strip())}
    rows = [json.loads(l) for l in open(HERE / args.results) if l.strip()]
    rows = [r for r in rows if r.get("phantom") is not None]
    sample = random.sample(rows, min(args.n, len(rows)))

    j1, j2 = [], []
    for i, r in enumerate(sample):
        th = threads.get((r["base"], r["level"]))
        if not th:
            continue
        rendered = render_thread(th)
        raw = chat(args.judge2, [{"role": "user", "content":
                   JUDGE.format(thread=rendered, output=r["output"])}], max_new=220, temperature=0.0)
        o = extract_json(raw) or {}
        if "phantom" not in o:
            continue
        j1.append(1 if r["phantom"] else 0)
        j2.append(1 if o["phantom"] else 0)
        if (i + 1) % 20 == 0:
            print(f"  {i+1}/{len(sample)}", flush=True)

    n = len(j1)
    agree = sum(1 for x, y in zip(j1, j2) if x == y)
    print(f"\nJudge reliability: primary=qwen3.5:9b vs secondary={args.judge2}")
    print(f"  n compared      : {n}")
    print(f"  agreement       : {100*agree/n:.0f}% ({agree}/{n})")
    print(f"  Cohen's kappa   : {cohen_kappa(j1, j2):.2f}")
    print(f"  primary phantom : {100*sum(j1)/n:.0f}%   secondary phantom: {100*sum(j2)/n:.0f}%")


if __name__ == "__main__":
    main()
