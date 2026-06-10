import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
threads = {(t["base"], t["level"]): t for t in
           (json.loads(l) for l in open(HERE / "threads_full.jsonl") if l.strip())}
r = [json.loads(l) for l in open(HERE / "results_full.jsonl") if l.strip()]
lvl = sys.argv[1] if len(sys.argv) > 1 else "E2c_consensus"
ex = [x for x in r if x["level"] == lvl and x["condition"] == "default" and x.get("phantom")]
print(f"{len(ex)} phantom=true at {lvl} (default). Showing 8:\n")
for x in ex[:8]:
    th = threads.get((x["base"], x["level"]), {})
    print(f"### {x['model']} | {x['base']} | {x['task']}")
    print(f"  REPLIES IN THREAD: {th.get('replies')}")
    print(f"  FLAGGED CLAIMS   : {x.get('claims')}")
    print(f"  OUTPUT           : {x['output'][:240].replace(chr(10),' ')}")
    print()
