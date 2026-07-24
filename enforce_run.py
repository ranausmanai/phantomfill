"""Rung 4: DECODER-ENFORCED structured output via Ollama's format parameter.

The decoder is constrained to the JSON schema: format violation (prose refusal)
is physically impossible. Two enforcement conditions:
  enf_req : enforced schema, enums WITHOUT escape values  -> fabricate is the only
            grammatical option besides... nothing. The floor test.
  enf_esc : enforced schema, enums WITH "insufficient_evidence"  -> escape is
            grammatically available; does the model take it under enforcement?

Same threads, same QUESTION as schema_run.py. Deterministic scoring applies.
"""
import argparse
import json
import re
import threading
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

HERE = Path(__file__).resolve().parent
from phantom_run import render_thread, OLLAMA_URL
from schema_run import QUESTION

SCHEMA_REQ = {
    "type": "object",
    "properties": {
        "sentiment": {"type": "string", "enum": ["positive", "negative", "mixed"]},
        "main_themes": {"type": "array", "items": {"type": "string"}, "minItems": 3},
        "representative_reaction": {"type": "string"},
        "controversy_level": {"type": "string", "enum": ["low", "medium", "high"]},
    },
    "required": ["sentiment", "main_themes", "representative_reaction", "controversy_level"],
}

SCHEMA_ESC = {
    "type": "object",
    "properties": {
        "sentiment": {"type": "string",
                      "enum": ["positive", "negative", "mixed", "insufficient_evidence"]},
        "main_themes": {"type": ["array", "null"], "items": {"type": "string"}},
        "representative_reaction": {"type": ["string", "null"]},
        "controversy_level": {"type": "string",
                              "enum": ["low", "medium", "high", "insufficient_evidence"]},
    },
    "required": ["sentiment", "main_themes", "representative_reaction", "controversy_level"],
}

CONDS = {"enf_req": SCHEMA_REQ, "enf_esc": SCHEMA_ESC}


def chat_enforced(model, prompt, schema, max_new=400):
    body = json.dumps({
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "stream": False,
        "format": schema,
        "options": {"num_predict": max_new},
    }).encode()
    req = urllib.request.Request(OLLAMA_URL, data=body,
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=600) as r:
        out = json.loads(r.read())
    t = out.get("message", {}).get("content", "")
    return re.sub(r"<think>.*?</think>", "", t, flags=re.DOTALL | re.IGNORECASE).strip()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("models")                      # comma-separated ollama tags
    ap.add_argument("--levels", default="E3_counts,E2c_consensus")
    ap.add_argument("--conds", default="enf_req,enf_esc")
    ap.add_argument("--workers", type=int, default=3)
    ap.add_argument("--out", default="enforce_out.jsonl")
    a = ap.parse_args()

    levels = a.levels.split(",")
    conds = a.conds.split(",")
    threads = [json.loads(l) for l in open(HERE / "threads_full.jsonl")
               if l.strip() and json.loads(l)["level"] in levels]

    fo = open(HERE / a.out, "a")
    lock = threading.Lock()

    for model in a.models.split(","):
        jobs = [(th, c) for th in threads for c in conds]
        done = [0]
        print(f"{model}: {len(jobs)} enforced calls", flush=True)

        def do(job):
            th, c = job
            prompt = f"{render_thread(th)}\n\n{QUESTION}"
            out = ""
            for attempt in range(3):
                try:
                    out = chat_enforced(model, prompt, CONDS[c])
                except Exception as e:
                    out = f"__ERR__{e}"
                if out.strip() and not out.startswith("__ERR__"):
                    break
            return {"model": model, "base": th["base"], "level": th["level"],
                    "task": "schema", "condition": c, "output": out}

        with ThreadPoolExecutor(max_workers=a.workers) as ex:
            for f in as_completed([ex.submit(do, j) for j in jobs]):
                r = f.result()
                with lock:
                    fo.write(json.dumps(r) + "\n"); fo.flush()
                    done[0] += 1
                    if done[0] % 40 == 0 or done[0] == len(jobs):
                        print(f"  [{done[0]}/{len(jobs)}]", flush=True)
    fo.close()
    print(f"wrote -> {a.out}", flush=True)


if __name__ == "__main__":
    main()
