"""Figures for the phantom study (run locally; pulls results_full.jsonl).
Fig1: phantom rate by evidence level (default) with 95% CI.
Fig2: phantom rate at E3_counts by model (capability trend).
Fig3: mitigation — default vs abstain by level.
"""
import json
import math
import sys
from collections import defaultdict

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

LEVELS = ["E0_postonly", "E1_neutral", "E2_mixed", "E2c_consensus", "E3_counts"]
path = sys.argv[1] if len(sys.argv) > 1 else "results_full.jsonl"
rows = [json.loads(l) for l in open(path) if l.strip()]
rows = [r for r in rows if r.get("phantom") is not None]


def wil(k, n, z=1.96):
    if n == 0:
        return 0, 0, 0
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return 100 * p, 100 * max(0, c - h), 100 * min(1, c + h)


def prate(rs):
    k = sum(1 for r in rs if r["phantom"])
    return wil(k, len(rs))


dft = [r for r in rows if r["condition"] == "default"]

# Fig 1
by = defaultdict(list)
for r in dft:
    by[r["level"]].append(r)
xs = [l for l in LEVELS if by[l]]
ys = [prate(by[l])[0] for l in xs]
err = [[prate(by[l])[0] - prate(by[l])[1] for l in xs], [prate(by[l])[2] - prate(by[l])[0] for l in xs]]
plt.figure(figsize=(8, 5))
bars = plt.bar(xs, ys, yerr=err, capsize=4, color=["#9bb", "#9bb", "#9bb", "#7a9", "#c55"])
plt.ylabel("Phantom Social Evidence Rate (%)")
plt.title("Models fabricate crowd sentiment most when given counts but no text")
plt.xticks(rotation=20)
for b, y in zip(bars, ys):
    plt.text(b.get_x() + b.get_width() / 2, y + 2, f"{y:.0f}%", ha="center", fontsize=9)
plt.tight_layout(); plt.savefig("fig1_by_level.png", dpi=150); plt.close()

# Fig 2: by model at E3
e3 = defaultdict(list)
for r in dft:
    if r["level"] == "E3_counts":
        e3[r["model"]].append(r)
ms = sorted(e3, key=lambda m: prate(e3[m])[0])
ys2 = [prate(e3[m])[0] for m in ms]
plt.figure(figsize=(8, 5))
plt.bar(ms, ys2, color="#c55")
plt.ylabel("Phantom rate at E3_counts (%)")
plt.title("Capability vs fabrication (E3_counts)")
plt.xticks(rotation=20)
plt.tight_layout(); plt.savefig("fig2_by_model.png", dpi=150); plt.close()

# Fig 3: mitigation
plt.figure(figsize=(8, 5))
w = 0.38
xs3 = [l for l in LEVELS if any(r["level"] == l for r in rows)]
d = [prate([r for r in rows if r["level"] == l and r["condition"] == "default"])[0] for l in xs3]
a = [prate([r for r in rows if r["level"] == l and r["condition"] == "abstain"])[0] for l in xs3]
x = range(len(xs3))
plt.bar([i - w / 2 for i in x], d, w, label="default", color="#c55")
plt.bar([i + w / 2 for i in x], a, w, label="abstain-instructed", color="#7a9")
plt.xticks(list(x), xs3, rotation=20)
plt.ylabel("Phantom rate (%)")
plt.title("Mitigation: abstention instruction")
plt.legend()
plt.tight_layout(); plt.savefig("fig3_mitigation.png", dpi=150); plt.close()
print("wrote fig1_by_level.png, fig2_by_model.png, fig3_mitigation.png")
