"""PhantomFill paper figures, computed live from result files.
fig1: 13-model x 3-rung fabrication matrix at E3 (heatmap)
fig2: the schema flip (GPT/Opus free->req) + escape-hatch utilization
fig3: instruction-vs-format fight
"""
import json
from collections import defaultdict
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from schema_score import score

HERE = Path(__file__).resolve().parent

OPEN_ORDER = ["qwen3.5:0.8b", "qwen3.5:2b", "llama3.2:3b", "gemma4:e4b",
              "mistral:7b", "qwen2.5:7b", "llama3.1:8b", "phi4", "gemma4:26b"]
FRONTIER_ORDER = ["haiku", "sonnet", "opus", "codex"]
LABELS = {"qwen3.5:0.8b": "qwen 0.8B", "qwen3.5:2b": "qwen 2B", "llama3.2:3b": "llama 3B",
          "gemma4:e4b": "gemma e4B", "mistral:7b": "mistral 7B", "qwen2.5:7b": "qwen 7B",
          "llama3.1:8b": "llama 8B", "phi4": "phi-4 14B", "gemma4:26b": "gemma 26B",
          "haiku": "Haiku 4.5", "sonnet": "Sonnet 4.6", "opus": "Opus 4.8", "codex": "GPT-5.5"}
RUNGS = ["freetext", "json_esc", "json_req"]


def load_rows(files):
    rows = []
    for f in files:
        p = HERE / f
        if not p.exists():
            continue
        rows += [json.loads(l) for l in open(p) if l.strip()]
    return [r for r in rows if "session limit" not in r.get("output", "")]


def fab_matrix():
    """model -> rung -> (fab_rate, n). JSON rungs deterministic; freetext from judged files."""
    det = load_rows(["pf_open_all.jsonl", "pf_codex.jsonl", "pf_opus_clean.jsonl",
                     "pf_haiku2.jsonl", "pf_sonnet2.jsonl", "pf_opus2.jsonl"])
    judged = load_rows(["pf_open_freetext_judged.jsonl", "pf_frontier_freetext_judged.jsonl",
                        "pf_hs2_freetext_judged.jsonl"])
    m = defaultdict(lambda: defaultdict(lambda: [0, 0]))
    for r in det:
        if r["level"] != "E3_counts" or r["condition"] == "freetext":
            continue
        c = m[r["model"]][r["condition"]]
        c[0] += 1; c[1] += int(score(r)["fabricated"])
    for r in judged:
        if r["level"] != "E3_counts" or r.get("phantom") is None:
            continue
        c = m[r["model"]]["freetext"]
        c[0] += 1; c[1] += int(bool(r["phantom"]))
    return m


def fig1(m):
    models = [x for x in OPEN_ORDER + FRONTIER_ORDER if x in m]
    data = np.full((len(models), 3), np.nan)
    for i, mod in enumerate(models):
        for j, rung in enumerate(RUNGS):
            n, f = m[mod][rung]
            if n:
                data[i, j] = 100 * f / n
    fig, ax = plt.subplots(figsize=(6.4, 7))
    im = ax.imshow(data, cmap="RdYlGn_r", vmin=0, vmax=100, aspect="auto")
    ax.set_xticks(range(3), ["free text", "JSON +\nescape hatch", "JSON\nrequired"])
    ax.set_yticks(range(len(models)), [LABELS[x] for x in models])
    for i in range(len(models)):
        for j in range(3):
            if not np.isnan(data[i, j]):
                v = data[i, j]
                ax.text(j, i, f"{v:.0f}", ha="center", va="center",
                        color="white" if 25 < v < 90 else "black", fontsize=10, fontweight="bold")
    ax.axhline(len([x for x in OPEN_ORDER if x in m]) - 0.5, color="black", lw=2)
    ax.set_title("PhantomFill: fabrication rate (%) at E3 (counts only, no replies)\nby output-format rung")
    fig.colorbar(im, label="% outputs fabricating crowd opinion")
    fig.tight_layout()
    fig.savefig(HERE / "pf_fig1_matrix.png", dpi=160)
    print("pf_fig1_matrix.png")


def fig2(m):
    fig, ax = plt.subplots(figsize=(7, 4))
    x = np.arange(3)
    for mod, c in [("codex", "#d62728"), ("opus", "#1f77b4"),
                   ("sonnet", "#ff7f0e"), ("haiku", "#2ca02c")]:
        if mod not in m:
            continue
        ys = [100 * m[mod][r][1] / m[mod][r][0] if m[mod][r][0] else np.nan for r in RUNGS]
        ax.plot(x, ys, "o-", lw=2.5, ms=8, label=LABELS[mod], color=c)
    ax.set_xticks(x, ["free text", "JSON + escape", "JSON required"])
    ax.set_ylabel("fabrication %")
    ax.set_title("The schema flip: same thread, same question, format only")
    ax.legend(); ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(HERE / "pf_fig2_flip.png", dpi=160)
    print("pf_fig2_flip.png")


def fig3():
    rows = load_rows(["schema_abstain_open.jsonl", "schema_codex_abstain.jsonl",
                      "schema_opus_abstain.jsonl"])
    base = load_rows(["pf_open_all.jsonl", "pf_codex.jsonl", "pf_opus_clean.jsonl"])
    def rate(rs, mod):
        sel = [r for r in rs if r["model"] == mod and r["level"] == "E3_counts"
               and r["condition"] == "json_req"]
        return 100 * sum(score(r)["fabricated"] for r in sel) / len(sel) if sel else np.nan
    mods = ["llama3.1:8b", "gemma4:e4b", "gemma4:26b", "phi4", "codex", "claude"]
    base_map = {"claude": "opus"}
    no_i = [rate(base, base_map.get(x, x)) for x in mods]
    with_i = [rate(rows, x) for x in mods]
    x = np.arange(len(mods)); w = 0.38
    fig, ax = plt.subplots(figsize=(7.5, 4))
    ax.bar(x - w/2, no_i, w, label="schema only", color="#d62728")
    ax.bar(x + w/2, with_i, w, label='schema + "do NOT infer sentiment" instruction', color="#1f77b4")
    ax.set_xticks(x, [LABELS.get(base_map.get(v, v), v) for v in mods])
    ax.set_ylabel("fabrication % (JSON required, E3)")
    ax.set_title("Required-field schemas override explicit instructions\n(except phi-4 and Opus)")
    ax.legend(); ax.grid(alpha=0.3, axis="y")
    fig.tight_layout()
    fig.savefig(HERE / "pf_fig3_instruction.png", dpi=160)
    print("pf_fig3_instruction.png")


if __name__ == "__main__":
    m = fab_matrix()
    fig1(m); fig2(m); fig3()
