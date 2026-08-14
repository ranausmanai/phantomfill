"""Survey: how common are coercive fields in real-world schemas?

The benchmark items in PhantomFill are synthetic, because establishing that a
field is unanswerable requires constructing the absence of evidence. That is a
real limitation of the measurement. It is not, however, a limitation of the
schema pattern: this script checks how often the pattern occurs in schemas that
practitioners actually publish.

Corpus: APIs.guru, a public directory of ~2,500 OpenAPI descriptions of real
services. Object schemas from these documents are what tool-calling layers
convert into LLM function definitions, so the required-field structure they
carry is inherited directly by the model's output format.

A schema counts as coercive if it has at least one required field that cannot
express missing evidence: a closed-vocabulary enum or a boolean with no null
option. Only HIGH-severity findings are counted.

Run:  python3 survey_schemas.py --limit 400
"""

from __future__ import annotations

import argparse
import json
import random
import ssl
import sys
import urllib.request
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from phantomfill_lint import lint  # noqa: E402

DIRECTORY = "https://api.apis.guru/v2/list.json"
UA = {"User-Agent": "Mozilla/5.0 (compatible; phantomfill-survey/1.0)"}
CTX = ssl.create_default_context()
OUT = Path(__file__).resolve().parent / "survey_results.json"


def get_json(url: str, timeout: int = 45):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout, context=CTX) as r:
        return json.loads(r.read())


def spec_urls(limit: int, seed: int):
    """Pick APIs at random from the directory and return one spec URL each."""
    directory = get_json(DIRECTORY)
    names = sorted(directory)
    random.Random(seed).shuffle(names)
    picked = []
    for name in names:
        versions = directory[name].get("versions") or {}
        if not versions:
            continue
        newest = sorted(versions)[-1]
        url = versions[newest].get("swaggerUrl")
        if url and url.endswith(".json"):
            picked.append((name, url))
        if len(picked) >= limit:
            break
    return picked


def object_schemas(spec: dict):
    """Named object schemas, from either OpenAPI 3 or Swagger 2."""
    comps = (spec.get("components") or {}).get("schemas") or spec.get("definitions") or {}
    return {k: v for k, v in comps.items() if isinstance(v, dict)}


def survey(limit: int, seed: int) -> dict:
    apis_ok = apis_fail = 0
    n_schemas = n_required = n_coercive = 0
    rules = Counter()
    per_api = []

    for name, url in spec_urls(limit, seed):
        try:
            spec = get_json(url)
        except Exception:
            apis_fail += 1
            continue
        apis_ok += 1

        schemas = object_schemas(spec)
        req_here = coercive_here = 0
        for sname, sch in schemas.items():
            n_schemas += 1
            if not sch.get("required"):
                continue
            n_required += 1
            req_here += 1
            findings = lint(sch, name=sname, min_severity="high")
            if findings:
                n_coercive += 1
                coercive_here += 1
                rules.update(f.rule for f in findings)
        if req_here:
            per_api.append({
                "api": name,
                "schemas_with_required": req_here,
                "coercive": coercive_here,
                "pct": round(100 * coercive_here / req_here, 1),
            })
        print(f"  {name:<44} {coercive_here:>4}/{req_here:<4} coercive", flush=True)

    per_api.sort(key=lambda r: -r["schemas_with_required"])
    return {
        "corpus": "APIs.guru OpenAPI directory",
        "apis_fetched": apis_ok,
        "apis_failed": apis_fail,
        "schemas_total": n_schemas,
        "schemas_with_required_fields": n_required,
        "schemas_coercive": n_coercive,
        "pct_coercive": round(100 * n_coercive / n_required, 1) if n_required else 0.0,
        "findings_by_rule": dict(rules),
        "per_api": per_api,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=300, help="number of APIs to sample")
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()

    result = survey(args.limit, args.seed)
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")

    print("\n" + "=" * 62)
    print(f"APIs sampled          {result['apis_fetched']} (failed: {result['apis_failed']})")
    print(f"Object schemas        {result['schemas_total']:,}")
    print(f"  with required       {result['schemas_with_required_fields']:,}")
    print(f"  coercive            {result['schemas_coercive']:,}  "
          f"({result['pct_coercive']}%)")
    print("Findings by rule:")
    for rule, count in sorted(result["findings_by_rule"].items(), key=lambda kv: -kv[1]):
        print(f"  {rule:<32}{count:>7,}")
    print(f"\nwrote {OUT.name}")


if __name__ == "__main__":
    main()
