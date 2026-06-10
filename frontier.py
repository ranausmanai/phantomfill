"""Frontier models via local CLIs (no API key): claude -p and codex exec.
Modes:
  agent  : run claude/codex as the AGENT over threads x tasks (default condition)
  judge  : use claude/codex as a GOLD JUDGE on a sample of existing outputs, compare labels
"""
import argparse
import json
import re
import subprocess
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

HERE = Path(__file__).resolve().parent
from phantom_run import render_thread, TASKS, SYS, extract_json
from rejudge import JUDGE2


def claude_call(prompt, timeout=180):
    import os
    cmd = ["claude", "-p"]
    m = os.environ.get("CLAUDE_MODEL")
    if m:
        cmd += ["--model", m]
    try:
        r = subprocess.run(cmd + [prompt], capture_output=True, text=True, timeout=timeout)
        return r.stdout.strip()
    except Exception as e:
        return f"__ERR__{e}"


def codex_call(prompt, timeout=360):
    try:
        r = subprocess.run(["codex", "exec", "--skip-git-repo-check", prompt],
                           capture_output=True, text=True, timeout=timeout,
                           stdin=subprocess.DEVNULL, cwd=str(HERE))
        parts = re.split(r"\ncodex\n", r.stdout)
        ans = parts[-1] if len(parts) > 1 else r.stdout
        return re.split(r"\ntokens used", ans)[0].strip()
    except Exception as e:
        return f"__ERR__{e}"


CALLERS = {"claude": claude_call, "codex": codex_call}


def load_threads():
    return [json.loads(l) for l in open(HERE / "threads_full.jsonl") if l.strip()]


def agent(name, levels, workers, out):
    caller = CALLERS[name]
    threads = load_threads()
    if levels:
        threads = [t for t in threads if t["level"] in levels]
    jobs = [(th, tk) for th in threads for tk in TASKS]
    print(f"{name} agent: {len(jobs)} calls", flush=True)
    lock = threading.Lock()
    fo = open(HERE / out, "w")
    done = [0]

    def do(job):
        th, tk = job
        prompt = f"{SYS['default']}\n\n{render_thread(th)}\n\nTASK: {TASKS[tk]}"
        return {"model": name, "base": th["base"], "level": th["level"], "task": tk,
                "condition": "default", "output": caller(prompt)}

    with ThreadPoolExecutor(max_workers=workers) as ex:
        futs = [ex.submit(do, j) for j in jobs]
        for f in as_completed(futs):
            r = f.result()
            with lock:
                fo.write(json.dumps(r) + "\n"); fo.flush()
                done[0] += 1
            print(f"  [{done[0]}/{len(jobs)}] {r['base']}/{r['level']}/{r['task']}", flush=True)
    fo.close()
    print(f"wrote -> {out}", flush=True)


def judge(name, results, n, workers):
    caller = CALLERS[name]
    threads = {(t["base"], t["level"]): t for t in load_threads()}
    rows = [json.loads(l) for l in open(HERE / results) if l.strip()]
    rows = [r for r in rows if r.get("phantom") is not None and r.get("condition") == "default"]
    # stratified by level
    import collections
    bylvl = collections.defaultdict(list)
    for r in rows:
        bylvl[r["level"]].append(r)
    per = max(1, n // len(bylvl))
    sample = []
    for lvl, rs in bylvl.items():
        step = max(1, len(rs) // per)
        sample += rs[::step][:per]
    print(f"{name} gold-judge: {len(sample)} outputs", flush=True)
    lock = threading.Lock()
    res = []

    def do(r):
        th = threads[(r["base"], r["level"])]
        raw = caller(JUDGE2.format(thread=render_thread(th), output=r["output"]))
        o = extract_json(raw) or {}
        return (r, o.get("phantom") if "phantom" in o else None)

    with ThreadPoolExecutor(max_workers=workers) as ex:
        for f in as_completed([ex.submit(do, r) for r in sample]):
            r, p = f.result()
            with lock:
                res.append((r, p))

    valid = [(r, p) for r, p in res if p is not None]
    agree = sum(1 for r, p in valid if bool(r["phantom"]) == bool(p))
    n2 = len(valid)
    print(f"\nGOLD judge = {name}  (n={n2})")
    print(f"  agreement with gemma-26b judge: {100*agree/n2:.0f}%")
    print(f"  gemma phantom rate: {100*sum(1 for r,_ in valid if r['phantom'])/n2:.0f}%   "
          f"{name} phantom rate: {100*sum(1 for _,p in valid if p)/n2:.0f}%")
    import collections as C
    by = C.defaultdict(lambda: [0, 0, 0])
    for r, p in valid:
        b = by[r["level"]]
        b[0] += 1; b[1] += int(bool(r["phantom"])); b[2] += int(bool(p))
    print(f"  {'level':<16}{'n':>4}{'gemma':>8}{name:>8}")
    for lvl in ["E0_postonly", "E1_neutral", "E2_mixed", "E2c_consensus", "E3_counts"]:
        if lvl in by:
            c, g, q = by[lvl]
            print(f"  {lvl:<16}{c:>4}{100*g/c:>7.0f}%{100*q/c:>7.0f}%")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["agent", "judge"])
    ap.add_argument("model", choices=["claude", "codex"])
    ap.add_argument("--levels", default="")
    ap.add_argument("--results", default="results_rejudged.jsonl")
    ap.add_argument("--n", type=int, default=100)
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--out", default="frontier_out.jsonl")
    a = ap.parse_args()
    levels = [x for x in a.levels.split(",") if x]
    if a.mode == "agent":
        agent(a.model, levels, a.workers, a.out)
    else:
        judge(a.model, a.results, a.n, a.workers)


if __name__ == "__main__":
    main()
