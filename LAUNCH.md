# Launch: exact steps, in order

Paper is live: **arXiv:2607.20492** — https://arxiv.org/abs/2607.20492

Do these in order. Steps 1–3 are today. Steps 4–8 are the distribution, spread over
a week. Nothing below has been sent or posted.

Where you see `[paste]`, the text under it is ready to copy verbatim.

---

# TODAY

## Step 1 — Replace the arXiv version (10 min) ⚠️ do this before promoting anything

The live v1 is the uncorrected draft. It says the enforced-decoding escape was
"taken in 0 of 200 trials." It was 12 of 200, and `enforce_main.jsonl` is public in
your repo, so this is checkable by anyone in five minutes. Fix it before you send
people to it.

Replacing a preprint the same week you post it is routine. Nobody is notified,
nobody reads v1 once v2 exists, and the abstract page just shows "v2".

1. Go to https://arxiv.org/login and log in.
2. Go to your user page — the "My Articles" list at https://arxiv.org/user
3. Find **2607.20492** and click the **replace** link (a pencil icon) next to it.
4. Upload this file: **`phantomfill_arxiv_v2.tar.gz`** (in your repo root)
5. On the metadata screen, replace the **abstract** field with the text below —
   it now includes the enforced-decoding result, which is your strongest finding
   and was missing from v1's abstract.
6. In the **comments** field, put the repo link (this is what makes people click).
7. Submit. It goes live at the next announcement (weekday evenings, US Eastern).

**[paste] — abstract field:**

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
models spend it zero times out of 203 trials on the three fields that carry the
fabrication, and twelve times on the one field where escaping concedes nothing.
They can emit the word. They decline to spend it where it costs them an answer. A
direct instruction, do not infer sentiment, is overridden by the schema in four of
six models. Resistance does not come with scale: within a single model family, the
smallest model refuses, the mid-sized model fabricates, the largest refuses again.
Honesty under format pressure is a training outcome that no one is measuring.

The fabrication hides exactly where hedging is impossible: in required enums and
minimum-count arrays, fields where no disclaimer fits. We release PhantomFill, a
benchmark with deterministic scoring and two reportable numbers: the Coerced
Fabrication Rate and the Escape Utilization Rate. The fix we test is one line of
schema. The failure we measure is everywhere.
```

**[paste] — comments field:**

```
Benchmark, 4,500+ raw model outputs, and a schema linter: https://github.com/ranausmanai/phantomfill
```

## Step 2 — Push the repo (2 min)

```bash
git push -u origin linter-and-scorer-fix
```

Then merge to `main` on GitHub. The README now points at the arXiv link and the
linter, and the corrected data needs to be what people find.

## Step 3 — Put the linter on PyPI (15 min)

This is the part that keeps working after every post has scrolled away. A tool in
someone's CI is a durable reason for them to know your name.

Make a free account at https://pypi.org/account/register, then create an API token
under Account Settings → API tokens.

```bash
python3 -m pip install --upgrade build twine
python3 -m build
python3 -m twine upload dist/*
```

Username is `__token__`, password is the token (starts with `pypi-`).

Verify:

```bash
pip install phantomfill-lint && phantomfill-lint --help
```

---

# THIS WEEK — distribution

You have no audience. That's fine: none of these depend on one. They work by
borrowing an audience that already exists, or by ranking on content alone.

Ordered by what I'd actually do first.

## Step 4 — Hugging Face Daily Papers (5 min) ← best single channel for you

Curated, high-traffic, and open to anyone submitting their own arXiv paper. No
followers required.

1. Log in at https://huggingface.co (free account).
2. Go to https://huggingface.co/papers and click **Submit a paper**.
3. Paste: `https://arxiv.org/abs/2607.20492`
4. Add the summary below as the submission comment.

Do this the morning after v2 announces, not before — you want the corrected
version to be what people land on.

**[paste]:**

```
Same input, same question, only the output format changes. The inputs are built so
the queried field cannot be answered, so scoring is done by code rather than by a
judge.

GPT-5.5 says "there is no reply data" in 98% of free-text trials, and fabricates in
40 of 40 when the answer must go in a required JSON enum. Ten of thirteen models
hit 100%.

The result I did not expect: under grammar-constrained decoding, with
"insufficient_evidence" a legal token in the sampler's grammar, five open models
used it 0 times out of 203 trials on the three fields that constitute the
fabrication — and 12 times on the one field where escaping still let them keep a
full answer everywhere else. The escape is reachable and they use it. Just never
where it costs them.

Benchmark, all 4,500+ raw outputs, and a linter that flags the dangerous fields in
your own schemas: https://github.com/ranausmanai/phantomfill
```

## Step 5 — Email the authors you cite (30 min) ← most underrated

Researchers amplify work that extends theirs, because it makes their paper more
important. These four all have real audiences and a direct interest in your result
existing. This is the cheapest borrowed distribution available to you.

Get each address from the first page of their paper PDF or their GitHub profile —
don't guess.

| who | paper | your hook |
|---|---|---|
| Kirichenko et al. (Meta AI) | AbstentionBench | Your rung 1 replicates them; your rung 3 shows their conclusion is format-dependent |
| Tam et al. | Let Me Speak Freely | You measured a format effect an order of magnitude bigger than theirs, on a different outcome variable |
| Willard & Louf (dottxt) | Outlines | The enforced-decoding result is about their technique |
| Wen et al. | Know Your Limits survey | A new abstention axis their taxonomy doesn't cover |

**[paste] — adapt the first paragraph per recipient:**

```
Subject: Your AbstentionBench result appears to be format-dependent

Hi [name],

I read AbstentionBench closely while building on it, and I wanted to send you a
result that I think sits directly on top of yours.

I ran a controlled version of your question where the input and the question are
held fixed and only the output format varies. Inputs are constructed so the queried
field is unanswerable, so the headline scoring is deterministic rather than
judge-based.

At the free-text rung I reproduce your finding. At the required-JSON-field rung it
inverts: GPT-5.5 goes from 2% fabrication in prose to 100% (40/40) on identical
input. Ten of thirteen models reach 100%. The abstention behavior your benchmark
measures appears to be gated by the output format, and every abstention benchmark
I know of — including yours — elicits prose.

I'm not claiming this undercuts your result. I think it extends it: it suggests the
numbers in AbstentionBench are an upper bound on what a deployed system does, since
deployment speaks JSON.

Paper: https://arxiv.org/abs/2607.20492
Data and benchmark: https://github.com/ranausmanai/phantomfill

If you think the design is wrong somewhere I'd genuinely like to know — you've
thought about this longer than I have.

Rana Muhammad Usman
```

## Step 6 — Reddit (10 min, day after HF)

Pure content ranking. Account age and karma barely matter; the table does.

**r/LocalLLaMA** — the open-model result is about the models they run and the
grammar-constrained result is about the stack they use daily.

Title:
```
I tested 13 models: every open model fabricates ~100% of the time when the JSON schema has no "insufficient_evidence" option — including under grammar-constrained decoding
```

**[paste] — body:**

```
Setup: same input, same question, only the output format changes. Inputs are built
so the answer cannot exist (a post with engagement counts but no reply text), so
any concrete value is a fabrication by construction and scoring is deterministic —
no LLM judge in the headline numbers.

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

The part I think matters most here: I re-ran it with Ollama's `format` parameter, so
the decoder grammar was constrained to the schema and a prose refusal was physically
unreachable. In the condition where "insufficient_evidence" was a legal enum token,
five open models emitted it 0 times out of 203 trials on sentiment, main_themes and
representative_reaction — and 12 times on controversy_level, the one field where
escaping still left them a full answer everywhere else. A typical output declares
sentiment "positive", lists three themes, quotes a reaction nobody wrote, then
reports controversy as "insufficient_evidence".

So it isn't that the escape is hard to reach or easy to miss. It's reachable, they
use it, and only where it doesn't cost them.

Practical upshot for anyone running local models behind a schema: adding a null or
an "unknown" enum value is necessary and nowhere near sufficient. Measure it for
your own model.

Everything is MIT and runs locally against Ollama — generators, scorer, all 4,500+
raw outputs. There's also a linter (`pip install phantomfill-lint`) that flags the
coercive fields in your own schemas.

https://github.com/ranausmanai/phantomfill
https://arxiv.org/abs/2607.20492
```

Keep links at the bottom, lead with the table, and answer technical questions fast.

**r/MachineLearning** — same day or next, use the `[R]` flair. Title:
```
[R] The output format causes the hallucination: 13 models, 2% fabrication in prose vs 100% under a required JSON field, same input
```
Reuse the HF summary from Step 4 as the body.

## Step 7 — GitHub issues (20 min) ← highest job value

Small teams, maintainers read every issue, and a good one from someone who
obviously did the work functions as an application.

Open one each on: `dottxt-ai/outlines`, `567-labs/instructor`, `BoundaryML/baml`,
`guidance-ai/guidance`, `pydantic/pydantic-ai`.

Title:
```
Required enum fields with no "unknown" value coerce fabrication — measurement + linter
```

**[paste]:**

```
Hi — I've been measuring a failure mode that sits right at the boundary of what this
library does, and I think the data might be useful to you. Not a bug report; more
"here is a number for the thing everyone suspects."

When a schema has a required field and the input contains no evidence for it, models
that answer honestly in prose invent a value instead. I ran 13 models on inputs
constructed so the field is unanswerable, so scoring is deterministic rather than
judge-based. Ten of thirteen fabricate in 100% of trials. GPT-5.5 goes from 2% in
prose to 100% under a required-field schema on identical input.

The part specifically relevant to constrained generation: I re-ran it with
decoder-level grammar constraints, in a condition where "insufficient_evidence" was
a legal token in the enum. Across 203 trials, five open models emitted that token 0
times on the three fields that carry the fabrication — and 12 times on the one field
where escaping didn't cost them an answer. The escape being reachable in the grammar
is not sufficient.

I'm not suggesting the library does anything wrong here; the constraint does exactly
what it's asked. But it does mean a user who writes

    {"sentiment": {"enum": ["positive", "negative", "mixed"]}, "required": [...]}

has written a schema that cannot represent "I don't know", and most users don't
realize that was a decision.

Two things that might be worth considering:

1. A docs note: if a field may be unanswerable for some inputs, give it a null or an
   explicit unknown value.
2. Optionally, a warning when a required enum has no abstention value. I wrote a
   standalone zero-dependency linter for exactly this check
   (`pip install phantomfill-lint`) — happy to contribute it as an integration, or
   leave it separate, whichever you prefer.

Paper: https://arxiv.org/abs/2607.20492
Data (4,500+ raw outputs) and benchmark: https://github.com/ranausmanai/phantomfill

Happy to run the benchmark against [project] specifically if that's useful — it runs
locally against Ollama, no API cost.
```

That last line is what opens the door. Be ready to actually do it.

## Step 8 — Newsletters (20 min)

These people need material every single week. A cold email with a real result is
supply meeting demand, not spam. Use the contact or reply address listed on each
newsletter — don't guess an address.

Targets: Import AI, TLDR AI, AlphaSignal, Ben's Bites, Last Week in AI, The Neuron.

**[paste]:**

```
Subject: 13-model measurement: JSON schemas cause hallucination, 2% -> 100%

Hi [name],

Short pitch, one result.

I measured what a language model does when your output schema has a required field
and the input has no evidence for it. Same input, same question, only the format
changes; inputs constructed unanswerable so scoring is by code, not by a judge.

GPT-5.5 answers honestly in prose 98% of the time and fabricates in 40 of 40 trials
when the answer has to go in a required JSON enum. Ten of thirteen models hit 100%.
Adding an "insufficient_evidence" option fixes the frontier models and does nothing
for the open ones — under grammar-constrained decoding, with the escape token
guaranteed reachable, five open models used it 0 times out of 203 on the fields that
mattered, and 12 times on the one field where escaping cost them nothing.

Relevant to your readers because almost every production LLM feature now runs
through JSON mode or function calling, and the mitigation is one line of schema.

https://arxiv.org/abs/2607.20492

Free tool that flags the dangerous fields: pip install phantomfill-lint

Happy to write it up short if that's easier for you.

Rana Muhammad Usman
```

---

# THE JOB PART

Nothing above says you're looking for work. Nobody will guess.

## Step 9 — HN "Who wants to be hired?"

Posted by user `whoishiring` on the first working day of each month. Zero followers
needed; people read the whole thread.

**[paste]:**

```
Location: [your city]
Remote: Yes
Willing to relocate: [Yes/No]
Technologies: Python, LLM evaluation, benchmark design, red-teaming, local
inference (Ollama/llama.cpp), constrained decoding
Résumé/CV: [link]
Email: usmanashrafrana@gmail.com

I build evaluations that find failure modes nobody has a number for yet. Most
recent: PhantomFill (arXiv:2607.20492), which measures how often a model fabricates
when a JSON schema leaves it no way to say "I don't know" — 13 models, 4,500+
trials, deterministic scoring, plus a linter that catches the dangerous schemas
(pip install phantomfill-lint).

Previously: adversarial feeds steering LLM agent decisions (arXiv:2606.00914).

Looking for evaluation, safety, or applied research work. Independent so far — both
papers were done on a laptop with local models and no compute budget, which I
mention because it's the constraint I'm used to designing around.
```

Keep that last sentence. It turns your biggest limitation into the most interesting
thing about you.

## Step 10 — Direct emails, after Step 7 gets replies

dottxt (Outlines), Boundary (BAML), and the Instructor maintainer all work on
exactly this problem and all are small enough to answer email. Reply to your GitHub
issue first, then email referencing it.

Also worth one email each to evaluation contacts at Anthropic, OpenAI, Google
DeepMind, and the UK AI Security Institute (AISI publishes evaluation work and takes
external submissions):

**[paste]:**

```
Subject: Coerced fabrication under required JSON fields — 13-model benchmark

Hi,

I've released a benchmark measuring fabrication caused by output format rather than
by missing knowledge. Same input, same question, only the schema changes; inputs
constructed unanswerable, so scoring is deterministic.

The finding most relevant to model evaluation: within the Claude family, Haiku 4.5
refuses the impossible schema in 40 of 40 trials and fabricates in none, Sonnet 4.6
fabricates in 90%, and Opus 4.8 refuses in 39 of 53 — and Opus does something none
of the others do, returning a machine-readable refusal object of its own design
rather than prose or a guess. Parameter count and recency predict nothing. It looks
like a training outcome, and as far as I can tell no public number tracks it.

Paper: https://arxiv.org/abs/2607.20492
Benchmark and linter: https://github.com/ranausmanai/phantomfill

It runs locally and takes minutes. If a CFR/EUR number would be useful for model
cards, I'd be glad to help set it up.

Rana Muhammad Usman
```

One email each. No follow-up before two weeks.

---

# Skip these

- **Twitter/LinkedIn as a primary channel.** Follower-gated; you'd be shouting into
  a void. Post there once for the record, expect nothing, move on.
- **Paying for API credits.** Your strongest result is the enforced-decoding one and
  it's entirely local and free.
- **Waiting on a conference.** If you want a venue later, TMLR takes rolling
  submissions with no deadline and suits a measurement paper. It'll still be there.
- **Hacker News as your opening move.** Median Show HN gets under 10 points. Do it
  after HF and Reddit, when you have something to point at.
