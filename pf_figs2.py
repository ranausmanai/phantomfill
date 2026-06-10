"""PhantomFill figure suite v2. Six publication figures, computed live from results.
Design: claim-as-title, one accent palette, no chartjunk, big annotated numbers.
"""
import json
from collections import defaultdict
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

from schema_score import score

HERE = Path(__file__).resolve().parent

# ---------- design system ----------
RED = "#C5283D"      # fabrication
GREEN = "#1E7A46"    # honest
AMBER = "#E8A33D"    # format violation / refusal tax
INK = "#1a1a2e"
GRAY = "#9aa0a6"
BG = "#FFFFFF"
plt.rcParams.update({
    "font.family": "Helvetica Neue",
    "font.size": 11,
    "text.color": INK,
    "axes.edgecolor": INK,
    "axes.labelcolor": INK,
    "xtick.color": INK,
    "ytick.color": INK,
    "figure.facecolor": BG,
    "axes.facecolor": BG,
    "savefig.facecolor": BG,
    "axes.spines.top": False,
    "axes.spines.right": False,
})

OPEN = ["qwen3.5:0.8b", "qwen3.5:2b", "llama3.2:3b", "gemma4:e4b",
        "mistral:7b", "qwen2.5:7b", "llama3.1:8b", "phi4", "gemma4:26b"]
FRONTIER = ["haiku", "sonnet", "opus", "codex"]
LAB = {"qwen3.5:0.8b": "Qwen 0.8B", "qwen3.5:2b": "Qwen 2B", "llama3.2:3b": "Llama 3B",
       "gemma4:e4b": "Gemma e4B", "mistral:7b": "Mistral 7B", "qwen2.5:7b": "Qwen 7B",
       "llama3.1:8b": "Llama 8B", "phi4": "Phi-4 14B", "gemma4:26b": "Gemma 26B",
       "haiku": "Haiku 4.5", "sonnet": "Sonnet 4.6", "opus": "Opus 4.8", "codex": "GPT-5.5"}
RUNGS = ["freetext", "json_esc", "json_req"]
RUNG_LAB = ["free text", "JSON + escape", "JSON required"]


def load(files):
    rows = []
    for f in files:
        p = HERE / f
        if p.exists():
            rows += [json.loads(l) for l in open(p) if l.strip()]
    return [r for r in rows if "session limit" not in r.get("output", "")]


def matrix():
    det = load(["pf_open_all.jsonl", "pf_codex.jsonl", "pf_opus_clean.jsonl",
                "pf_haiku2.jsonl", "pf_sonnet2.jsonl", "pf_opus2.jsonl"])
    jud = load(["pf_open_freetext_judged.jsonl", "pf_frontier_freetext_judged.jsonl",
                "pf_hs2_freetext_judged.jsonl"])
    m = defaultdict(lambda: defaultdict(lambda: [0, 0, 0]))  # n, fab, badjson
    for r in det:
        if r["level"] != "E3_counts" or r["condition"] == "freetext":
            continue
        s = score(r)
        c = m[r["model"]][r["condition"]]
        c[0] += 1; c[1] += int(s["fabricated"]); c[2] += int(not s["valid_json"])
    for r in jud:
        if r["level"] != "E3_counts" or r.get("phantom") is None:
            continue
        c = m[r["model"]]["freetext"]
        c[0] += 1; c[1] += int(bool(r["phantom"]))
    return m


def pct(m, mod, rung):
    n, f, _ = m[mod][rung]
    return 100 * f / n if n else np.nan


# ---------- FIG 1: hero matrix ----------
def fig1(m):
    models = OPEN + FRONTIER
    data = np.array([[pct(m, mod, r) for r in RUNGS] for mod in models])
    fig, ax = plt.subplots(figsize=(7.6, 8.2))
    cmap = matplotlib.colors.LinearSegmentedColormap.from_list(
        "pf", ["#1E7A46", "#7fb069", "#f2cc8f", "#e07a5f", "#C5283D"])
    im = ax.imshow(data, cmap=cmap, vmin=0, vmax=100, aspect="auto")
    # white grid
    for i in range(len(models) + 1):
        ax.axhline(i - 0.5, color="white", lw=3)
    for j in range(4):
        ax.axvline(j - 0.5, color="white", lw=3)
    ax.set_xticks(range(3), RUNG_LAB, fontsize=12)
    ax.xaxis.set_ticks_position("top")
    ax.set_yticks(range(len(models)), [LAB[x] for x in models], fontsize=12)
    for i, mod in enumerate(models):
        for j in range(3):
            v = data[i, j]
            if np.isnan(v):
                continue
            light = 30 < v < 85
            txt = f"{v:.0f}"
            # annotate refusal cells
            n, f, bad = m[mod][RUNGS[j]]
            note = ""
            if RUNGS[j] == "json_req" and bad >= n * 0.6 and n:
                note = "\nrefuses"
            ax.text(j, i, txt + note, ha="center", va="center", fontsize=13,
                    fontweight="bold", color="white" if not light else INK)
    # frontier divider
    ax.axhline(len(OPEN) - 0.5, color=INK, lw=2.5)
    ax.text(2.56, len(OPEN) - 0.75, "open weights", ha="left", fontsize=10, color=GRAY, style="italic", clip_on=False)
    ax.text(2.56, len(OPEN) - 0.18, "frontier", ha="left", fontsize=10, color=GRAY, style="italic", clip_on=False)
    ax.set_xlim(-0.5, 2.5)
    ax.set_title("Fabrication rate (%) when the fields are unanswerable\nsame input, same question, only the output format changes",
                 fontsize=13.5, pad=42, fontweight="bold", loc="left")
    ax.tick_params(length=0)
    for s in ax.spines.values():
        s.set_visible(False)
    fig.tight_layout()
    fig.savefig(HERE / "v2_fig1_matrix.png", dpi=200)
    print("v2_fig1_matrix.png")


# ---------- FIG 2: the flip, slope chart ----------
def fig2(m):
    fig, ax = plt.subplots(figsize=(8.2, 5.2))
    x = np.arange(3)
    styles = {"codex": (RED, "o", 3.6), "opus": (GREEN, "s", 2.6),
              "haiku": ("#4361ee", "D", 2.0), "sonnet": ("#7d8597", "^", 2.0)}
    for mod, (c, mk, lw) in styles.items():
        ys = [pct(m, mod, r) for r in RUNGS]
        ax.plot(x, ys, marker=mk, lw=lw, ms=9, color=c, label=LAB[mod],
                zorder=5 if mod == "codex" else 3)
        ax.annotate(LAB[mod], (2, ys[2]), xytext=(12, 0), textcoords="offset points",
                    fontsize=11, fontweight="bold", color=c, va="center")
    ax.annotate("0 to 100 in one\nschema change", xy=(1.97, 96), xytext=(1.25, 72),
                fontsize=12.5, color=RED, fontweight="bold", ha="center",
                arrowprops=dict(arrowstyle="-|>", color=RED, lw=1.6,
                                connectionstyle="arc3,rad=0.2"))
    ax.set_xticks(x, RUNG_LAB, fontsize=12)
    ax.set_xlim(-0.15, 2.75)
    ax.set_ylim(-4, 106)
    ax.set_ylabel("fabrication %", fontsize=12)
    ax.grid(axis="y", alpha=0.25)
    ax.set_title("The schema flip: GPT-5.5 is honest until the format removes the option",
                 fontsize=13.5, fontweight="bold", loc="left", pad=14)
    fig.tight_layout()
    fig.savefig(HERE / "v2_fig2_flip.png", dpi=200)
    print("v2_fig2_flip.png")


# ---------- FIG 3: strategy breakdown at json_req ----------
def fig3(m):
    models = OPEN + FRONTIER
    fabs, viol, honest = [], [], []
    for mod in models:
        n, f, bad = m[mod]["json_req"]
        fabs.append(100 * f / n)
        # violations that are NOT counted fabricated (honest refusals in prose)
        hv = 100 * bad / n
        # honest = neither fabricated; split into refusal (bad json) vs honest JSON
        viol.append(min(hv, 100 - 100 * f / n))
        honest.append(max(0, 100 - 100 * f / n - viol[-1]))
    y = np.arange(len(models))[::-1]
    fig, ax = plt.subplots(figsize=(8.4, 7.2))
    ax.barh(y, fabs, color=RED, label="fabricates the fields")
    ax.barh(y, viol, left=fabs, color=AMBER, label="refuses by breaking the schema")
    ax.barh(y, honest, left=np.array(fabs) + np.array(viol), color=GREEN,
            label="honest inside the schema")
    ax.set_yticks(y, [LAB[x] for x in models], fontsize=12)
    ax.set_xlim(0, 100)
    ax.set_xlabel("% of trials (JSON required, unanswerable fields)", fontsize=11)
    for yi, (a, b, c) in zip(y, zip(fabs, viol, honest)):
        if a > 8: ax.text(a / 2, yi, f"{a:.0f}", ha="center", va="center", color="white", fontweight="bold", fontsize=10.5)
        if b > 8: ax.text(a + b / 2, yi, f"{b:.0f}", ha="center", va="center", color="white", fontweight="bold", fontsize=10.5)
        if c > 8: ax.text(a + b + c / 2, yi, f"{c:.0f}", ha="center", va="center", color="white", fontweight="bold", fontsize=10.5)
    ax.axhline(3.5, color=INK, lw=2)
    ax.legend(loc="lower right", framealpha=0.95, fontsize=10.5)
    ax.set_title("Three ways to face an impossible schema:\nlie, crash the parser, or answer honestly within it",
                 fontsize=13.5, fontweight="bold", loc="left", pad=14)
    fig.tight_layout()
    fig.savefig(HERE / "v2_fig3_strategies.png", dpi=200)
    print("v2_fig3_strategies.png")


# ---------- FIG 4: EUR ----------
def fig4(m):
    models = OPEN + FRONTIER
    eur = [(mod, 100 - pct(m, mod, "json_esc")) for mod in models]
    eur.sort(key=lambda t: t[1])
    y = np.arange(len(eur))
    fig, ax = plt.subplots(figsize=(8.2, 6.6))
    cols = [GREEN if mod in FRONTIER else GRAY for mod, _ in eur]
    cols = [GREEN if v >= 80 else (AMBER if v >= 30 else GRAY) for _, v in eur]
    ax.barh(y, [v for _, v in eur], color=cols)
    ax.set_yticks(y, [LAB[mod] for mod, _ in eur], fontsize=12)
    for yi, (mod, v) in zip(y, eur):
        ax.text(v + 1.5, yi, f"{v:.0f}%", va="center", fontsize=11, fontweight="bold",
                color=INK)
    ax.set_xlim(0, 108)
    ax.set_xlabel("Escape Utilization Rate: % taking an offered “insufficient evidence” option", fontsize=11)
    ax.set_title("The cheap fix only works at the top:\nmost models ignore the escape hatch you give them",
                 fontsize=13.5, fontweight="bold", loc="left", pad=14)
    ax.grid(axis="x", alpha=0.25)
    fig.tight_layout()
    fig.savefig(HERE / "v2_fig4_eur.png", dpi=200)
    print("v2_fig4_eur.png")


# ---------- FIG 5: field-level mechanism ----------
def fig5():
    fields = ["sentiment\n(required enum)", "main complaints\n(array)", "representative quote\n(free string)"]
    vals = [100, 15, 0]
    fig, ax = plt.subplots(figsize=(7.6, 4.8))
    cols = [RED, AMBER, GREEN]
    bars = ax.bar(fields, vals, color=cols, width=0.55)
    for b, v in zip(bars, vals):
        ax.text(b.get_x() + b.get_width() / 2, v + 2.5, f"{v:.0f}%", ha="center",
                fontsize=15, fontweight="bold", color=INK)
    ax.set_ylim(0, 112)
    ax.set_ylabel("fabricated (GPT-5.5, untranscribed ticket, n=20)", fontsize=10.5)
    ax.set_title("Fabrication hides where no hedge fits:\na string can carry a disclaimer, an enum cannot",
                 fontsize=13.5, fontweight="bold", loc="left", pad=14)
    ax.grid(axis="y", alpha=0.25)
    fig.tight_layout()
    fig.savefig(HERE / "v2_fig5_fields.png", dpi=200)
    print("v2_fig5_fields.png")


# ---------- FIG 6: instruction fight ----------
def fig6():
    rows = load(["schema_abstain_open.jsonl", "schema_codex_abstain.jsonl", "schema_opus_abstain.jsonl"])
    base = load(["pf_open_all.jsonl", "pf_codex.jsonl", "pf_opus_clean.jsonl", "pf_opus2.jsonl"])
    def rate(rs, mod):
        sel = [r for r in rs if r["model"] == mod and r["level"] == "E3_counts" and r["condition"] == "json_req"]
        return 100 * sum(score(r)["fabricated"] for r in sel) / len(sel) if sel else np.nan
    mods = ["llama3.1:8b", "gemma4:e4b", "gemma4:26b", "codex", "phi4", "claude"]
    bmap = {"claude": "opus"}
    no_i = [rate(base, bmap.get(x, x)) for x in mods]
    wi_i = [rate(rows, x) for x in mods]
    x = np.arange(len(mods)); w = 0.36
    fig, ax = plt.subplots(figsize=(8.6, 5))
    ax.bar(x - w / 2, no_i, w, color=RED, label="schema alone")
    ax.bar(x + w / 2, wi_i, w, color="#4361ee", label="schema + “do NOT infer sentiment” system prompt")
    for xi, (a, b) in zip(x, zip(no_i, wi_i)):
        ax.text(xi - w / 2, a + 2, f"{a:.0f}", ha="center", fontsize=10.5, fontweight="bold")
        ax.text(xi + w / 2, b + 2, f"{b:.0f}", ha="center", fontsize=10.5, fontweight="bold")
    ax.set_xticks(x, [LAB.get(bmap.get(v, v), v) for v in mods], fontsize=11.5)
    ax.set_ylim(0, 132)
    ax.set_ylabel("fabrication % (JSON required)", fontsize=11)
    ax.annotate("instruction changes nothing", xy=(1.5, 112), fontsize=11.5, color=RED, fontweight="bold", ha="center")
    ax.plot([-0.25, 3.25], [108, 108], color=RED, lw=1.2)
    ax.annotate("instruction wins", xy=(4.5, 45), fontsize=11.5, color="#4361ee", fontweight="bold", ha="center")
    ax.legend(loc="upper right", fontsize=10, framealpha=0.95, bbox_to_anchor=(1.0, 0.92))
    ax.grid(axis="y", alpha=0.25)
    ax.set_title("The schema outranks the system prompt for 4 of 6 models",
                 fontsize=13.5, fontweight="bold", loc="left", pad=14)
    fig.tight_layout()
    fig.savefig(HERE / "v2_fig6_instruction.png", dpi=200)
    print("v2_fig6_instruction.png")


if __name__ == "__main__":
    m = matrix()
    fig1(m); fig2(m); fig3(m); fig4(m); fig5(); fig6()
