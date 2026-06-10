"""Analyze phantom results: phantom + abstention rates by level / model / task /
condition, with Wilson 95% CIs. Includes the E2c_consensus control (phantom should
be LOW there = judge not over-flagging) and the mitigation effect (default vs abstain).
"""
import json
import math
import sys
from collections import defaultdict

LEVEL_ORDER = ["E0_postonly", "E1_neutral", "E2_mixed", "E2c_consensus", "E3_counts"]


def wilson(k, n, z=1.96):
    if n == 0:
        return (float("nan"), 0, 0)
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (100 * p, 100 * max(0, c - half), 100 * min(1, c + half))


def rate(rows, field):
    v = [r[field] for r in rows if r.get(field) is not None]
    k = sum(1 for x in v if x)
    return wilson(k, len(v)) + (k, len(v))


def line(label, rows):
    p, lo, hi, k, n = rate(rows, "phantom")
    a, alo, ahi, ak, an = rate(rows, "abstained")
    ps = f"{p:4.0f}% [{lo:3.0f},{hi:3.0f}]" if n else "   —"
    as_ = f"{a:4.0f}%" if an else "  —"
    print(f"  {label:<22} phantom {ps:<18} (n={n:>3})   abstain {as_:>6}")


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else "results_full.jsonl"
    rows = [json.loads(l) for l in open(path) if l.strip()]
    rows = [r for r in rows if r.get("phantom") is not None]
    print(f"\nSource: {path}   ({len(rows)} judged outputs)\n")

    dft = [r for r in rows if r["condition"] == "default"]

    print("=== 1. Phantom rate by EVIDENCE LEVEL (default condition) ===")
    print("    (E2c_consensus is a control: genuine agreement present -> phantom should be LOW)")
    by = defaultdict(list)
    for r in dft:
        by[r["level"]].append(r)
    for lvl in LEVEL_ORDER:
        if by[lvl]:
            line(lvl, by[lvl])

    print("\n=== 2. Phantom rate by MODEL (default, all levels) — capability trend ===")
    bym = defaultdict(list)
    for r in dft:
        bym[r["model"]].append(r)
    for m in sorted(bym):
        line(m, bym[m])

    print("\n=== 3. Phantom rate at E3_counts by MODEL (the headline cell) ===")
    e3 = defaultdict(list)
    for r in dft:
        if r["level"] == "E3_counts":
            e3[r["model"]].append(r)
    for m in sorted(e3):
        line(m, e3[m])

    print("\n=== 4. Phantom rate by TASK (default) ===")
    byt = defaultdict(list)
    for r in dft:
        byt[r["task"]].append(r)
    for t in sorted(byt):
        line(t, byt[t])

    print("\n=== 5. MITIGATION: default vs abstain-instructed (by level) ===")
    for lvl in LEVEL_ORDER:
        d = [r for r in rows if r["level"] == lvl and r["condition"] == "default"]
        a = [r for r in rows if r["level"] == lvl and r["condition"] == "abstain"]
        if not d:
            continue
        pd, *_ , kd, nd = rate(d, "phantom")
        pa, *_ , ka, na = rate(a, "phantom")
        print(f"  {lvl:<16} default {pd:4.0f}%  ->  abstain {pa:4.0f}%   (Δ {pa-pd:+.0f} pts)")


if __name__ == "__main__":
    main()
