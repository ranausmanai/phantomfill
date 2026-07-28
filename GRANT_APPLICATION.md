# LTFF application — field by field

Form: https://funds.effectivealtruism.org (Long-Term Future Fund)

Their guidance: total 2,000–5,000 characters, 1–2 hours. This is written to that.
**Leave fields blank rather than writing "N/A"** — they say it creates manual work.

`[FILL]` marks the few things only you know.

---

## Select funds

**Fund:** Long-Term Future Fund
**Secondary fund (EAIF transfer):** Yes
**Funding from Open Philanthropy:** select whichever is true — almost certainly "I have not received funding from Open Philanthropy"

## Basic information

**Name:** `Rana Muhammad Usman`
**Organization name:** *leave empty*
**Grant Program:** **Long-Term Risk Research Grants**
**Main collaborators:** *leave empty* (form says to leave blank if working independently)
**Email address:** `usmanashrafrana@gmail.com`
**Additional email addresses:** *leave empty*
**Employed by Effective Ventures:** `I have not previously held any paid position at Effective Ventures or any of its projects.`

---

## Short description — 100/120 characters

```
6-month stipend to extend PhantomFill, a benchmark measuring LLM fabrication caused by output format
```

## Summary — 998/1000 characters

```
LLMs that honestly answer "there is no evidence for that" in prose invent one when the same question arrives as a JSON schema with a required field. Across 13 models, required fields drive fabrication to 100% in ten. Under grammar-constrained decoding, with the escape token guaranteed reachable by the sampler, five open models used it 0 times out of 200 on the fields carrying the fabrication, and 12 times on the one field where escaping conceded nothing. Paper: arXiv:2607.20492, under review at TMLR.

Honesty evaluations elicit prose; deployed systems and agents emit structured output. If honesty is format-dependent, published evaluations overstate deployed honesty, and no one measures the deployed case.

I did this unfunded on a laptop with local models, forcing two limitations money fixes: frontier models reached via vendor CLIs not APIs, and only two domains. I request 6 months to close both, add three high-stakes domains, and get these metrics into HELM and lm-evaluation-harness.
```

## Project goals

```
Concrete steps, in order:

1. Replace CLI-mediated frontier measurements with direct API runs (month 1). The current
frontier numbers came through vendor CLIs, which inject system prompts and scaffolding no
API user has. This is the most attackable weakness in the work and it is purely a cost
problem: roughly 25,000 API calls.

2. Extend from two domains to five (months 2-3): clinical-note summarization, incident
reports, and code review. Each is a real deployment of structured extraction where a
fabricated required field propagates into a decision. My existing result shows resistance
does not transfer across domains, so per-domain measurement is necessary, not redundant.

3. Test mitigations (month 4): whether the "structured refusal" behavior I observed in one
frontier model can be elicited by schema design, and whether constrained-decoding libraries
can warn at schema-compile time.

4. Ship it where it gets used (months 5-6): integrate as a scenario in HELM and
lm-evaluation-harness, and maintain the linter I already released.

Success criteria, checkable by you: five domains published with API-based frontier numbers;
at least one of HELM or lm-evaluation-harness merges the scenario; the linter has external
users.

Path to impact and fit with the fund: as LLMs are deployed as agents acting through
structured interfaces, a model's ability to report "I don't know" inside its output format
becomes a load-bearing safety property. Honesty evaluations today measure the prose case
only. If the format gates the honesty, the field is measuring the wrong configuration and
reporting numbers that are too optimistic. My contribution is a deterministic, cheap
measurement of the deployed case, plus the plumbing to make it routinely reported.

I want to be honest about scope: this is evaluation infrastructure, not alignment theory.
It reduces risk by making a specific honesty failure visible and measurable before agentic
deployments scale, not by solving anything fundamental.
```

## Track record

```
Two arXiv preprints, both done alone and unfunded:

- PhantomFill: When the Form Demands an Answer, Language Models Invent One
  (arXiv:2607.20492). 13 models, 4,500+ trials, deterministic scoring, all raw outputs
  released. Under review at TMLR.
- Adversarial Feeds Steer LLM Agent Decisions Against Their Defaults (arXiv:2606.00914).

I also released phantomfill-lint, a zero-dependency tool that flags the schema fields
causing this failure, so the result is actionable rather than only documented.

Expenditure and staffing to date: $0 funding, 1 FTE (myself, unpaid), all compute local.

The relevant signal is the constraint. Both papers were produced on a laptop running local
models with no compute budget and no collaborators. That forced a design discipline I would
not otherwise have found: unable to afford a judge model at scale, I built inputs where the
ground truth is absence, which made the headline metric deterministic and removed the
judge-reliability dispute that most hallucination benchmarks get stuck in. The
methodological strength came directly from having no money.

Honest weaknesses: I have no institutional affiliation, no formal research training [FILL:
adjust if you have a relevant degree], and no prior funded projects. My work has not yet
been peer-reviewed — TMLR is my first submission. I have not previously managed a budget or
a multi-month funded project.

[FILL: 2-3 sentences on your education and any prior professional/engineering work. Be
plain about gaps. LTFF funds independent people without PhDs regularly.]
```

## Public Portfolio

```
Paper:  https://arxiv.org/abs/2607.20492
Prior:  https://arxiv.org/abs/2606.00914
Code, data, and benchmark:  https://github.com/ranausmanai/phantomfill
Tool:   pip install phantomfill-lint
```

## Funding amount and breakdown

Copy their template: https://docs.google.com/spreadsheets/d/1lhzs0iqxq3Ik1ocab5cOOMXjN6S2R7zauHKWY8vF7iE/copy
Fill the lines below, set sharing to **"Anyone with the link can view"**, paste the link.

| line item | USD |
|---|---|
| Stipend, 6 months (gross, inclusive of income and self-employment tax) | 27,000 |
| API credits (~25,000 frontier calls incl. retries) | 4,500 |
| Rented GPU compute (~200 hrs, larger open models) | 3,000 |
| Annotation contractor (~120 hrs, validating new domains) | 2,500 |
| Software, storage, miscellaneous | 800 |
| **Subtotal** | **37,800** |
| Buffer (10%, stated explicitly per your guidance) | 3,780 |
| **Total** | **41,580** |

Text box:

```
Total requested: $41,580 over 6 months. Breakdown: 65% stipend (gross, tax included), 11%
API credits, 7% rented GPU compute, 6% annotation contractor, 2% software and storage, 9%
buffer.

Minimum viable scenario: $24,000. This covers the API reruns and three domains rather than
five, at a reduced stipend. The frontier API runs are the single highest-value item and
would be done first under any scenario.

Note: my stipend figure reflects cost of living in [FILL: your city/country], not a US or
UK rate.
```

> **[FILL] — set the stipend to your real six-month cost of living.** LTFF funds people
> globally and does not expect a Bay Area number. A lower, honestly justified figure is more
> likely to be funded than a padded one, and their own guidance asks for the minimum
> necessary. Adjust the buffer and total to match.

**Requested amount (USD):** `41580` (or your adjusted total)
**Organizational budget:** *leave empty*

## Alternatives to funding

```
If not funded, the project continues but shrinks. I would keep maintaining the benchmark
and the linter in whatever time I have while looking for employment, but the API reruns,
the three additional domains, and the harness integration would not happen. The frontier
numbers would stay CLI-mediated, which is the limitation most likely to keep the work from
being taken seriously.

Other applications: I am also applying to Manifund for the same project [FILL: adjust or
remove if you have not]. No funding applications in the last 12 months, none successful,
none pending elsewhere. No conditional offers.

I am currently unemployed and this grant would be my primary source of income.
```

## Use for additional funding

```
Extend the runway rather than the scope. A 12-month rather than 6-month grant would let me
add non-English domains, test whether fine-tuning on structured refusals transfers across
schema types, and run the benchmark against agentic tool-calling loops rather than single
extraction calls, which is where the failure actually bites in deployment.

Beyond that, funding a second person part-time for annotation and replication would let me
validate the new domains against human labels rather than my own.
```

## Remaining fields

| field | answer |
|---|---|
| Confidential information | Put anything about your financial situation here if you'd rather it not be shared with informal advisors. Otherwise leave empty. |
| LinkedIn/CV | `https://github.com/ranausmanai` + your arXiv author page. [FILL: add LinkedIn if you have one] |
| File upload | skip |
| Start date | today's date |
| End date | today + 6 months |
| Requested currency | USD |
| Location | `[FILL: your city, country]. Project implemented remotely; outputs are public.` |
| Activities in China or India? | `[FILL: No, unless you are in India]` |
| Award for past achievement? | No |
| Anyone under 18 contributing? | No |
| Safeguarding measures | *leave empty* |
| Lobbying or political activity? | No |
| References | *leave empty unless you have someone* — see note below |
| Organisational leadership | *leave empty* |
| Referral to other funders | **Yes** |
| How did you hear about EA Funds | `[FILL: honestly — e.g. "searching for funding for independent AI safety research"]` |
| Time-sensitive (decision under 8 weeks)? | **Yes** — reason: `I am currently unemployed with no income; this grant would be my primary source of support.` |
| Public reporting | **Public** |
| Network sharing | **Yes** |
| Anything else | *leave empty* |

---

## Three decisions I made for you, and why

**Long-Term Risk Research Grants, not Applied GCR.** Your primary output is new knowledge
— a measurement nobody has. The tool and harness integration are delivery mechanisms, not
the point.

**Network sharing: Yes.** That field explicitly offers job opportunities, career advice, and
mentorship. You want a job. It costs nothing and does not affect your grant odds. This is
the single highest-value checkbox on the form for your situation.

**Public reporting: Public.** It slightly improves funding odds, and a public LTFF payout
report is a credential and a visibility channel — exactly what you've been trying to build.

## On references

You have none in this community, and that's fine — leave it empty rather than padding it.
If the AbstentionBench or Outlines emails from LAUNCH.md get a substantive reply before you
submit, that person becomes a legitimate reference. Worth sending those first if you can
stand to wait a few days.

## Then do Manifund

Same text, much shorter form, separate money, public applications:
https://manifund.org. Mention in "Alternatives to funding" that you applied to both,
which their guidance explicitly asks for.
