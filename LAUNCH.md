# Launch checklist

Everything here is copy-paste ready. Nothing has been sent or posted.
Do them in this order — each one feeds the next.

Total active time: about 90 minutes, spread over a week.

---

## 0. Push the branch (2 min)

```bash
git push -u origin linter-and-scorer-fix
```

Then merge it to `main` — the arXiv package and the README both reference files
that are on this branch.

---

## 1. arXiv (20 min, do this first)

Everything else links here, so it has to exist first. You are already endorsed
for cs.CL via arXiv:2606.00914, so there is no gate.

Go to https://arxiv.org/submit

**Primary category:** `cs.CL`
**Cross-list:** `cs.AI`, `cs.LG`

**Title:**
```
PhantomFill: When the Form Demands an Answer, Language Models Invent One
```

**Abstract** (plain text, no LaTeX — paste exactly):
```
Language models in production do not write prose. They fill forms: JSON fields,
function arguments, extraction templates. We show that the form itself causes
hallucination.

We ask thirteen models the same question about the same input and change only the
answer format. The inputs are built so the question cannot be answered: a viral
post showing 12,400 likes but no visible replies, a support ticket whose call was
never transcribed. In free text, GPT-5.5 answers honestly. It says there is no
reply data, 98% of the time. Given a required JSON field for sentiment, the same
model invents an answer 40 times out of 40. It fabricates the mood of crowds it
never saw and quotes customers it never heard.

The pattern holds with force. Required fields drive fabrication to 100% in ten of
thirteen models. An explicit "insufficient evidence" option rescues only the
frontier: all nine open-weight models ignore it. Under grammar-constrained
decoding, where the escape token is guaranteed reachable by the sampler, five open
models use it zero times out of 203 trials on the fields that carry the
fabrication, while spending it freely on the one field where escaping concedes
nothing. A direct instruction, do not infer sentiment, is overridden by the schema
in four of six models. Resistance does not come with scale: within a single model
family, the smallest model refuses, the mid-sized model fabricates, the largest
refuses again. Honesty under format pressure is a training outcome that no one is
measuring.

The fabrication hides exactly where hedging is impossible: in required enums and
minimum-count arrays, fields where no disclaimer fits. We release PhantomFill, a
benchmark with deterministic scoring and two reportable numbers: the Coerced
Fabrication Rate and the Escape Utilization Rate. The fix we test is one line of
schema. The failure we measure is everywhere.
```

**Comments field** (this is what makes people click):
```
Benchmark, data, and a schema linter: https://github.com/ranausmanai/phantomfill
```

**Timing:** submissions before 14:00 ET on a weekday announce the next weekday
evening. Submit Monday or Tuesday so the announcement lands mid-week — that gives
you a live arXiv link for the Wednesday/Thursday posts below.

---

## 2. Ship the linter to PyPI (15 min)

This is the piece that keeps working after the posts scroll away. A tool in
someone's CI is a durable reason for them to know your name.

```bash
python3 -m pip install --upgrade build twine
python3 -m build
python3 -m twine upload dist/*
```

You need a PyPI account and an API token (free, 2 minutes, pypi.org/account/register).
Verify it worked:

```bash
pip install phantomfill-lint && phantomfill-lint --help
```

Then add a line at the top of the repo README:

```markdown
**Lint your own schemas:** `pip install phantomfill-lint`
```

---

## 3. Hacker News (5 min)

Post Tuesday–Thursday, 8–10am ET. That is when HN traffic peaks.

**Title** (keep it plain — HN punishes hype):
```
Show HN: A linter for LLM schemas that force the model to hallucinate
```

**URL:** the GitHub repo (not the arXiv link — repos do better on Show HN).

**First comment**, post this yourself immediately after submitting:

```
I spent a few weeks measuring something I kept hitting in production and couldn't
find a number for: what a model does when your JSON schema has a required field
and the input has no evidence for it.

The setup is a controlled one. Same input, same question, only the output format
changes. The inputs are built so the field cannot be answered — a post with
engagement counts but zero reply text, a support ticket whose call was never
transcribed. So any concrete value is a fabrication by construction, and scoring
is done by code rather than by a judge.

The result that made me keep going: GPT-5.5 asked in prose says "there is no reply
data" in 98% of trials. Asked through a schema with a required sentiment enum, it
fabricates in 40 of 40. Ten of the thirteen models I tested hit 100%.

Two things I did not expect:

- Adding "insufficient_evidence" to the enum fixes the frontier models and does
  nothing for the open ones. All nine open-weight models fabricated anyway, at
  60-100%.
- I re-ran it under grammar-constrained decoding so the escape token was
  guaranteed reachable by the sampler. Five open models used it zero times out of
  203 trials on the three fields that constitute the fabrication — and twelve
  times on the one field where escaping cost them nothing. They can emit the
  token. They just won't spend it where it means conceding an answer.

The linter is the practical half: it flags required enums, min-count arrays and
booleans that have no way to express "not in the evidence". Zero dependencies,
runs in CI, understands OpenAI and Anthropic tool definitions.

    pip install phantomfill-lint
    phantomfill-lint 'schemas/**/*.json'

Paper, data (4,500+ trials) and generators are in the repo. Happy to be told the
design is wrong somewhere — that would be useful to me.
```

**If it gets traction, answer every comment for the first three hours.** That is
the whole game on HN. The comments are where people decide whether you know what
you're talking about, and that is what turns into interview requests.

---

## 4. r/LocalLLaMA (5 min, day after HN)

This subreddit is your best audience — the open-model result is directly about
the models they run, and the grammar-constrained finding is about the stack they
use daily (llama.cpp / Ollama / outlines grammars).

**Title:**
```
I tested 13 models: every open model I tried fabricates ~100% of the time when the
JSON schema has no "insufficient_evidence" option — including under grammar-
constrained decoding
```

**Body:**

```
Setup: same input, same question, only the output format changes. Inputs are built
so the answer cannot exist (a post with engagement counts but no reply text). Any
concrete value is a fabrication by construction, so scoring is deterministic — no
LLM judge in the headline numbers.

Fabrication rate at the unanswerable level:

    model            free text   JSON+escape   JSON required
    qwen3.5 0.8B        98           100           100
    qwen3.5 2B         100           100           100
    llama3.2 3B        100           100           100
    gemma4 e4B          65            92           100
    mistral 7B          82           100           100
    qwen2.5 7B         100           100           100
    llama3.1 8B         95           100           100
    phi-4 14B           92            98           100
    gemma4 26B          88            60           100

Frontier for comparison: GPT-5.5 goes 2% -> 0% -> 100%. Claude Opus 4.8 stays at
0/9/13 but gets there by refusing to emit JSON at all in 39 of 53 trials.

The part I think matters most here: I re-ran it with Ollama's `format` parameter,
so the decoder grammar was constrained to the schema and a prose refusal was
physically unreachable. In the condition where "insufficient_evidence" was a legal
token in the enum, five open models emitted it 0 times out of 203 trials on
sentiment, main_themes and representative_reaction — and 12 times on
controversy_level, the one field where escaping still let them keep a full answer
everywhere else. A typical output declares sentiment "positive", lists three
themes, quotes a reaction nobody wrote, and then reports controversy as
"insufficient_evidence".

So it isn't that the escape is hard to reach or easy to miss. It's reachable, they
use it, and they only use it where it doesn't cost them.

Practical upshot if you run local models behind a JSON schema: adding a null or an
"unknown" enum value is necessary but is not going to save you. Measure it for
your own model.

Everything is MIT and runs locally against Ollama — generators, scorer, all 4,500+
raw outputs. There's also a linter (`pip install phantomfill-lint`) that flags the
dangerous fields in your own schemas.

[repo link]
[arXiv link]
```

**Note:** r/LocalLLaMA dislikes anything that reads like promotion. Lead with the
table, keep the links at the bottom, and answer technical questions fast.

---

## 5. GitHub issues on the libraries this is about (20 min, highest job-value)

This is the highest-leverage thing in this document and the one most likely to
turn into a job. These are small teams, the maintainers read every issue, and a
well-made issue from someone who clearly did the work is functionally a job
application in that world.

Open one issue per project. Tailor the first line; the body is reusable.

**Targets, in priority order:**

| project | why them |
|---|---|
| `dottxt-ai/outlines` | You cite them. The grammar-constrained result is *about* their technique. |
| `567-labs/instructor` | Biggest structured-output user base in Python. |
| `BoundaryML/baml` | Whole product is schema-driven LLM output; very responsive team. |
| `guidance-ai/guidance` | Constrained generation, same core concern. |
| `pydantic/pydantic-ai` | Newer, growing, schema-first. |

**Issue title:**
```
Required enum fields with no "unknown" value coerce fabrication — measurement + linter
```

**Issue body:**
```
Hi — I've been measuring a failure mode that sits right at the boundary of what
this library does, and I think the data might be useful to you. Not a bug report;
more a "here is a number for the thing everyone suspects."

The short version: when a schema has a required field and the input contains no
evidence for it, models that answer honestly in prose invent a value instead. I
ran 13 models on inputs constructed so the field is unanswerable (so scoring is
deterministic, not judge-based). Ten of thirteen fabricate in 100% of trials.
GPT-5.5 goes from 2% fabrication in prose to 100% under a required-field schema on
identical input.

The part that's specifically relevant to constrained generation: I re-ran it with
decoder-level grammar constraints, in a condition where "insufficient_evidence"
was a legal token in the enum. Across 203 trials, five open models emitted that
token 0 times on the three fields that carry the fabrication — and 12 times on the
one field where escaping didn't cost them an answer. The escape being reachable in
the grammar is not sufficient.

I'm not suggesting this is something the library does wrong — the constraint is
doing exactly what it's asked. But it does mean a user who writes

    {"sentiment": {"enum": ["positive", "negative", "mixed"]}, "required": [...]}

has written a schema that cannot represent "I don't know", and most users don't
realize that's a decision they made.

Two things that might be worth considering:

1. A docs note in the structured-output section: if a field may be unanswerable
   for some inputs, give it a null or an explicit unknown value.
2. Optionally, a warning when a required enum has no abstention value. I wrote a
   standalone zero-dependency linter for exactly this check
   (`pip install phantomfill-lint`) — happy to contribute it as an integration, or
   just leave it as a separate tool, whichever you prefer.

Paper, data (4,500+ raw outputs) and generators: [repo link]

Happy to run the benchmark against [project] specifically if that's interesting to
you — it runs locally against Ollama, no API costs.
```

That last line is the one that opens doors. Make it true and be ready to do it.

---

## 6. The job part — be direct about it (10 min)

You want work. Nothing above says so, and nobody will guess.

**a) HN "Who wants to be hired?"** — posted on the first working day of each
month by `whoishiring`. Post in that thread the same month your Show HN runs, so
anyone who saw the project can connect the two.

```
Location: [your city]
Remote: Yes
Willing to relocate: [Yes/No]
Technologies: Python, LLM evaluation, benchmark design, red-teaming, local
inference (Ollama/llama.cpp), constrained decoding
Résumé/CV: [link]
Email: usmanashrafrana@gmail.com

I build evaluations that find failure modes nobody has a number for yet. Most
recent: PhantomFill, which measures how often a model fabricates when a JSON
schema leaves it no way to say "I don't know" — 13 models, 4,500+ trials,
deterministic scoring, and a linter that catches the dangerous schemas.
[arXiv link] / [repo link]

Previously: adversarial feeds steering LLM agent decisions [arXiv:2606.00914].

Looking for: evaluation, safety, or applied research work. Independent so far —
both papers were done on a laptop with local models and no compute budget, which
I mention because it's the constraint I'm used to designing around.
```

That last sentence turns your biggest limitation into the thing that makes you
interesting. Keep it.

**b) Email the teams whose product this is about.** Small companies, real people,
they answer. dottxt (Outlines), Boundary (BAML), and the Instructor maintainer are
all reachable, and all three work on precisely this. Send after your GitHub issue
gets a reply — reply first, email second, referencing the issue.

**c) Lab evaluation teams.** Short, no attachment, one link:

```
Subject: Coerced fabrication under required JSON fields — 13-model benchmark

Hi,

I've released a benchmark measuring something I couldn't find a number for:
fabrication caused by output format rather than by missing knowledge. Same input,
same question, only the schema changes. Inputs are constructed unanswerable, so
scoring is deterministic.

The finding most relevant to model evaluation: within the Claude family, Haiku 4.5
refuses the impossible schema in 40 of 40 trials, Sonnet 4.6 fabricates in 90%,
and Opus 4.8 refuses in 39 of 53 — and Opus does something none of the others do,
returning a machine-readable refusal object of its own design rather than prose or
a guess. Parameter count and recency predict nothing. It looks like a training
outcome, and as far as I can tell no public number tracks it.

Paper and data: [arXiv link]
Benchmark and linter: [repo link]

It runs locally and takes minutes. If a CFR/EUR number would be useful for model
cards I'd be glad to help set it up.

Rana Muhammad Usman
```

Send to evaluation/alignment contacts at Anthropic, OpenAI and Google DeepMind,
and to the UK AI Security Institute — AISI publishes evaluation work and takes
external submissions. One email each, no follow-up before two weeks.

**d) HELM and lm-evaluation-harness.** Getting PhantomFill added as a scenario to
either is the single biggest multiplier available to you, and it costs a PR rather
than money. Do this after the linter is on PyPI.

---

## What to skip

- **Don't pay for API credits to redo the frontier runs.** It's a reviewer-comfort
  fix, not a correctness fix, and your strongest result (enforced decoding) is
  entirely local and free.
- **Don't wait for a conference decision before doing any of the above.** The
  practitioner channels are where this becomes useful to people, and they don't
  care about acceptance.
- **Don't submit to a main conference this month.** If you want a venue later,
  TMLR takes rolling submissions with no deadline and suits a measurement paper.
  It'll still be there when you have energy.
