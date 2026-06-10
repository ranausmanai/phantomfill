"""Compare two judges (gemma4:26b vs qwen3.5:9b, same tight prompt) on identical
outputs: overall agreement + Cohen's kappa, and per-model phantom rates under each
judge — to test whether gemma's near-0% is real or same-family leniency.
"""
import json
import sys
from collections import defaultdict


def load(p):
    d = {}
    for l in open(p):
        if not l.strip():
            continue
        r = json.loads(l)
        if r.get("phantom") is None:
            continue
        d[(r["model"], r["base"], r["level"], r["task"], r["condition"])] = 1 if r["phantom"] else 0
    return d


def kappa(pairs):
    n = len(pairs)
    if not n:
        return float("nan"), 0
    po = sum(1 for a, b in pairs if a == b) / n
    pa = sum(a for a, _ in pairs) / n
    pb = sum(b for _, b in pairs) / n
    pe = pa * pb + (1 - pa) * (1 - pb)
    return ((po - pe) / (1 - pe) if pe != 1 else 1.0), po


g = load(sys.argv[1] if len(sys.argv) > 1 else "results_rejudged.jsonl")        # gemma judge
q = load(sys.argv[2] if len(sys.argv) > 2 else "results_rejudged_qwen.jsonl")    # qwen judge
keys = [k for k in g if k in q]
pairs = [(g[k], q[k]) for k in keys]
k_all, agree = kappa(pairs)
print(f"\nJudge agreement (gemma4:26b vs qwen3.5:9b), n={len(keys)}")
print(f"  overall agreement: {100*agree:.0f}%   Cohen's kappa: {k_all:.2f}\n")

print("Per-model phantom rate under each judge (default condition only):")
print(f"  {'model':<16}{'gemma26b':>10}{'qwen9b':>10}{'agree':>9}")
bym = defaultdict(list)
for k in keys:
    if k[4] == "default":
        bym[k[0]].append(k)
for m in sorted(bym):
    ks = bym[m]
    gp = 100 * sum(g[k] for k in ks) / len(ks)
    qp = 100 * sum(q[k] for k in ks) / len(ks)
    ag = 100 * sum(1 for k in ks if g[k] == q[k]) / len(ks)
    print(f"  {m:<16}{gp:>9.0f}%{qp:>9.0f}%{ag:>8.0f}%")
