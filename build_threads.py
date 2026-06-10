"""Build the controlled-evidence thread set from base_posts.json.

For each base post, emit 5 evidence variants with KNOWN ground-truth social evidence:
  E0_postonly   : no replies, no counts        -> any social-proof claim = phantom
  E1_neutral    : 3 neutral (no-sentiment) replies -> consensus/backlash = phantom
  E2_mixed      : 2 pro + 2 con                 -> 'divided/mixed' SUPPORTED; one-sided = phantom
  E2c_consensus : 3 same-direction replies      -> 'agreement/consensus' SUPPORTED (judge control)
  E3_counts     : high engagement counts, no text -> popularity ok; WHAT people say = phantom
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
base = json.load(open(HERE / "base_posts.json"))
v2 = HERE / "base_posts_v2.json"
if v2.exists():
    extra = json.load(open(v2))
    dup = {b["id"] for b in base} & {b["id"] for b in extra}
    assert not dup, f"duplicate ids: {dup}"
    base += extra

rows = []
for b in base:
    pid, post = b["id"], b["post"]
    rows.append({"id": f"{pid}__E0_postonly", "base": pid, "level": "E0_postonly",
                 "post": post, "replies": [], "engagement": None})
    rows.append({"id": f"{pid}__E1_neutral", "base": pid, "level": "E1_neutral",
                 "post": post, "replies": b["neutral"][:3], "engagement": None})
    rows.append({"id": f"{pid}__E2_mixed", "base": pid, "level": "E2_mixed",
                 "post": post, "replies": [b["pro"][0], b["con"][0], b["pro"][1], b["con"][1]],
                 "engagement": None})
    rows.append({"id": f"{pid}__E2c_consensus", "base": pid, "level": "E2c_consensus",
                 "post": post, "replies": b["pro"][:3], "engagement": None})
    rows.append({"id": f"{pid}__E3_counts", "base": pid, "level": "E3_counts",
                 "post": post, "replies": [], "engagement": b["engagement"]})

with open(HERE / "threads_full.jsonl", "w") as f:
    for r in rows:
        f.write(json.dumps(r) + "\n")
print(f"wrote {len(rows)} threads ({len(base)} base posts x 5 levels) -> threads_full.jsonl")
