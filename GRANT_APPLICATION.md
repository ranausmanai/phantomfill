# Long-Term Future Fund — application draft

Apply at: https://funds.effectivealtruism.org/funds/far-future (Long-Term Future Fund).
Also submit the same text to Manifund (https://manifund.org) — it is a separate pool,
applications are public, and running both is normal and expected.

Anything in `[BRACKETS]` is a fact I don't have. Everything else is written.

---

## Project title

```
Measuring coerced fabrication: honesty failures caused by output format, not by missing knowledge
```

## Amount requested

```
$42,000 USD for 6 months
```

## Summary (what LTFF shows reviewers first)

```
Language models that correctly answer "there is no evidence for that" in prose will
invent an answer when the same question is asked through a JSON schema with a required
field. I measured this across thirteen models and found it drives fabrication to 100% in
ten of them. The paper is on arXiv (2607.20492) and under review at TMLR.

I did that work unfunded, on a laptop, using local models, which forced two limitations I
cannot fix without money: frontier models were reached through vendor CLIs rather than
APIs, and I could only build two evaluation domains. This grant funds six months to close
both gaps, extend the benchmark to four domains including high-stakes ones (clinical
notes, incident reports), and land it in the evaluation harnesses labs actually run
(HELM, lm-evaluation-harness) so the number gets reported rather than just published.

The concrete output is a maintained benchmark with two reportable metrics that no model
card currently includes, plus the tooling for others to run it on their own systems.
```

## The problem this addresses

```
Abstention benchmarks measure whether a model will say "I don't know." Every one of them
asks the model in prose. Deployed systems do not use prose: they use JSON mode, function
calling, and extraction schemas. My results show the gap between those two settings is
not a matter of degree. GPT-5.5 answers honestly in 98% of free-text trials and fabricates
in 40 out of 40 when the same answer must go into a required enum.

That means published safety evaluations systematically overstate the honesty of deployed
systems, and the error is invisible because nobody measures the deployed configuration.

The failure also has a specific shape that makes it dangerous. It concentrates in fields
where hedging is impossible — required enums, minimum-count arrays, booleans — and those
are exactly the fields that downstream code branches on. A free-text hallucination gets
read by a human who might notice. A fabricated enum value gets read by a switch statement.

I also found the failure is not a capability limit. Under grammar-constrained decoding,
with "insufficient_evidence" guaranteed reachable in the sampler's grammar, five open
models emitted it zero times out of 200 trials on the three fields that carried the
fabrication — and twelve times on the one field where escaping conceded nothing. The
models can produce the token. They decline to spend it where it costs them an answer.
That is a trained behavior, and it differs across models from the same lab, which means
it is trainable and currently untracked.
```

## What I will do with the funding

```
1. Replace CLI-mediated frontier measurements with direct API runs (month 1).
   The current frontier numbers were collected through vendor CLIs, which inject system
   prompts and agentic scaffolding that no API user has. This is the single most
   attackable methodological weakness in the paper and it is purely a cost problem.
   Estimated 15,000-25,000 API calls across GPT-5.5, Claude Opus/Sonnet/Haiku, and Gemini.

2. Extend from two domains to five (months 2-3).
   Current domains are social threads and support tickets. I will add clinical-note
   summarization, incident/postmortem reports, and code review — chosen because each is a
   real deployment of structured extraction where a fabricated required field propagates
   into a decision. My existing result shows resistance does not transfer across domains,
   so per-domain measurement is necessary rather than redundant.

3. Test mitigations properly (month 4).
   I have shown that adding an escape value fixes frontier models and fails for open
   models. What I have not tested: whether fine-tuning on structured refusals transfers,
   whether the "structured refusal" behavior I observed in one frontier model can be
   elicited by prompt or schema design, and whether constrained-decoding libraries can
   surface a warning at schema-compile time.

4. Ship it where it gets used (months 5-6).
   Integrate PhantomFill as a scenario in HELM and lm-evaluation-harness, maintain the
   linter (already released), and write the CFR/EUR reporting format up as something a
   model card can adopt. A benchmark nobody runs is a paper. A benchmark in the harness
   is a number that shows up in every evaluation report.
```

## Why me

```
I am an independent researcher with no institutional affiliation and no funding to date.
Two arXiv preprints, both done alone:

- PhantomFill: When the Form Demands an Answer, Language Models Invent One
  (arXiv:2607.20492, under review at TMLR). Thirteen models, 4,500+ trials, deterministic
  scoring, all raw outputs released.
- Adversarial Feeds Steer LLM Agent Decisions Against Their Defaults (arXiv:2606.00914).

I also shipped phantomfill-lint, a zero-dependency tool that flags the schema fields that
cause this failure, so the finding is actionable rather than only documented.

The relevant signal is the constraint I worked under. Both papers were produced on a
laptop running local models, with no compute budget, no API credits, and no collaborators.
That forced a design discipline I would not otherwise have learned: because I could not
afford a judge model at scale, I built inputs where the ground truth is absence, which
made the headline metric deterministic and removed the judge-reliability argument that
most hallucination benchmarks get stuck in. The methodological strength of the work came
directly from having no money.

I would rather not keep working this way, which is why I am applying.

[BRACKETS: add 2-3 sentences on your background — degree, prior employment, relevant
engineering experience. Be plain about the gap if there is one; LTFF funds independent
people and does not require a PhD.]
```

## Budget

```
Living stipend, 6 months                                        $30,000
API credits (frontier model runs, ~25k calls with retries)       $4,500
Compute (rented GPU hours for larger open models, ~200 hrs)      $3,500
Annotation (human validation of new domains, ~120 hrs)           $3,000
Miscellaneous (storage, tooling, conference registration)        $1,000
                                                                --------
Total                                                           $42,000

[BRACKETS: adjust the stipend to your actual cost of living in your country. LTFF funds
researchers globally and does not expect a Bay Area number. If $30k is more than you need
for six months, lower it — a realistic, well-justified ask is stronger than a large one.]
```

## Track record of output

```
Both preprints were completed and released within [BRACKETS: N] months of starting, alone,
without funding. Code and complete raw data for both are public under MIT.

Verification for reviewers:
  Paper:     https://arxiv.org/abs/2607.20492
  Code/data: https://github.com/ranausmanai/phantomfill
  Tool:      pip install phantomfill-lint
```

## What happens if you don't fund this

```
The benchmark stays as published: correct, but limited to two domains with frontier
numbers collected through an imperfect access path. I will keep maintaining it in whatever
time I have, but the API reruns and the high-stakes domains do not happen, and neither
does the harness integration, which is the part that determines whether anyone reports
these numbers.
```

---

## Also apply here, same text

- **Manifund** (https://manifund.org) — public applications, faster, smaller amounts.
  Regranters can fund you directly. Low effort given you already have this text.
- **Open Philanthropy** — check current early-career and AI-safety RFPs at
  openphilanthropy.org/research-and-grants. Larger, slower, more competitive.
- **AI Safety Camp / MATS** — programs rather than grants, but they pay a stipend and give
  you a mentor and collaborators, which is the other thing you're missing.

## Two notes on how to write this

Do not undersell the no-funding constraint. Reviewers at these funds are explicitly
looking for people who produce results without institutional support, because that is the
strongest available signal of what they would do with support. It is the best part of your
application. It stays in.

Do not inflate the ask. $42k with a line-item budget reads as competent. $150k with a
vague justification reads as someone who has not thought about it.
