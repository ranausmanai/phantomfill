# phantomfill-lint

**Find the fields in your JSON Schema that force a model to make something up.**

```bash
pip install phantomfill-lint
phantomfill-lint schemas/*.json
```

Zero dependencies. Python 3.8+.

---

## The one-minute version

A language model asked "what are people saying about this post?" — where the post has engagement counts but no reply text — will tell you honestly that there is no reply data. It does this reliably in prose.

Give it this schema instead:

```json
{
  "type": "object",
  "properties": {
    "sentiment": { "type": "string", "enum": ["positive", "negative", "mixed"] },
    "main_themes": { "type": "array", "items": {"type": "string"}, "minItems": 3 }
  },
  "required": ["sentiment", "main_themes"]
}
```

and it invents an answer. Every time. There is no legal value that means "I don't know," so the model picks one that is a lie, because the schema left it no other move.

This was measured across thirteen models. Ten of them fabricate in **100%** of trials under a schema like the one above. GPT-5.5 goes from 2% fabrication in prose to 100% under required fields, on identical input. ([paper](https://github.com/ranausmanai/phantomfill/blob/main/paper/main.pdf))

`phantomfill-lint` finds those fields before you ship them.

## What it flags

| rule | severity | why |
|---|---|---|
| `required-enum-no-escape` | high | Closed vocabulary, every value is a claim. Measured 20/20 fabrication. |
| `required-array-min-items` | high | `minItems: 3` means "invent three things" when there are none. |
| `required-boolean-no-escape` | high | `true`/`false` is a two-value vocabulary; a coin flip is recorded as a finding. |
| `required-number-no-escape` | medium | A number carries no disclaimer; a guess is indistinguishable from a measurement. |
| `required-string-no-escape` | low | Models hedge in free strings (measured 0/20), but the hedge lands where a consumer reads a value. |
| `required-array-not-nullable` | low | `[]` can express absence — flagged only if you must distinguish "none found" from "not determined". |

A field is cleared if it is optional, nullable, or its enum contains a recognized abstention value (`insufficient_evidence`, `unknown`, `not_available`, `n/a`, and similar — see `ESCAPE_VOCAB`).

`neutral` and `other` are **not** escape values. They are answers.

## Usage

```bash
phantomfill-lint schema.json                    # human-readable
phantomfill-lint 'schemas/**/*.json'            # globs
phantomfill-lint tools.json --format json       # machine-readable
phantomfill-lint tools.json --format github     # GitHub Actions annotations
phantomfill-lint tools.json --min-severity high # only the serious ones
phantomfill-lint tools.json --fail-on never     # report, never fail the build
```

Exit codes: `0` clean, `1` findings at or above `--fail-on` (default `high`), `2` file/parse error.

Understands bare JSON Schema, OpenAI function/tool definitions, OpenAI structured-output `json_schema` blocks, and Anthropic `input_schema` tool definitions — including lists of them, `$defs`/`$ref`, nested objects, and objects inside arrays.

### As a library

```python
from phantomfill_lint import lint

findings = lint(my_schema)
for f in findings:
    print(f.severity, f.path, f.message, f.fix)
```

### In CI

```yaml
- name: Lint LLM output schemas
  run: |
    pip install phantomfill-lint
    phantomfill-lint 'src/**/schemas/*.json' --format github
```

## The fix is usually one line

```diff
- "enum": ["positive", "negative", "mixed"]
+ "enum": ["positive", "negative", "mixed", "insufficient_evidence"]
```

Two caveats the measurements insist on:

**An escape value is necessary, not sufficient.** Frontier models take the exit when you give them one. Every open-weight model tested fabricated anyway, at 60–100%, even with `insufficient_evidence` sitting in the enum. Under grammar-constrained decoding, where the escape token was guaranteed reachable by the sampler, five open models used it **0 times out of 203** on the fields that mattered — while happily using it on the one field where escaping conceded nothing. Adding the value fixes your schema; it does not fix your model.

**Measure it for the model you actually deploy.** Resistance to this failure does not track parameter count and does not transfer across domains. Within one model family, the smallest model refused, the mid-sized one fabricated 90% of the time, and the largest refused again.

## License

MIT.

## Citation

```bibtex
@article{rana2026phantomfill,
  title  = {PhantomFill: When the Form Demands an Answer, Language Models Invent One},
  author = {Rana Muhammad Usman},
  year   = {2026}
}
```
