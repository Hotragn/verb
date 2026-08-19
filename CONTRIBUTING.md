# Contributing to VERB

Three contributions are wanted more than anything else. All three need people who are not the author, and all three are more valuable than a pull request that tidies the code.

---

## 1. Measured verification costs from real organisations

**This is the most useful thing you can send.**

The whole framework rests on `c`, the qualified human hours it takes to genuinely review one decision of a given class. Every number in this repository that touches `c` is either synthetic or an estimate. There is no published field data on this, anywhere, that I have been able to find.

If you have measured it, please report it. One measured `ĉ` with its method is worth more than a page of argument.

**Use the issue template: [Report a measured verification cost](https://github.com/hotragn/verb/issues/new?template=measured-verification-cost.yml).**

What is needed:

- The decision type, described well enough that somebody else could recognise it.
- The class you assigned it, and briefly why.
- Measured `ĉ`, the sample size, and the date.
- The measurement method, especially whether you asked reviewers afterwards if they had genuinely checked and discarded the ones who said no. That step is what separates a verification cost from an approval duration, and it is the step almost everybody skips.
- The interquartile range if you have it.

What is not needed:

- Your organisation's name. Anonymised is completely fine. "A 900-person engineering consultancy, UK" is enough context.
- Anything commercially sensitive. If in doubt, round the numbers.
- A polished write-up. A rough number with an honest method beats a clean number with an unknown one.

**Negative results are wanted too.** If you tried to measure `ĉ` and could not, that is informative and it should be written down. The reasons people cannot measure it are probably more interesting than the values.

---

## 2. Classification disagreements

The A/B/C/D boundaries are not crisp, particularly between B and C. The decision tree in [spec/decision-classes.md](spec/decision-classes.md) resolves most cases and the tie-breakers resolve most of the rest, but genuine disagreement remains and nobody has published a field disagreement rate.

Open an issue labelled `classification` with:

- The decision type.
- What the tree gave you.
- What you think the right answer is, and why.
- If two people in your organisation split on it, both rationales.

Cases where the tree gives an answer that is clearly wrong are the most valuable, because they point at a defect in the tree rather than at a hard case.

If you have run [Gate 1](spec/eval-gates.md#gate-1-classification) and have a kappa, please include it, whatever it was. A low kappa is a finding, not an embarrassment.

---

## 3. The queueing question

This is the largest open problem in the framework and it is stated as [limitation 3](README.md#10-known-limitations).

`VB` is a rate. Decisions do not arrive at a constant rate. An organisation can be comfortably under budget averaged across a quarter and still drop reviews in the week the board pack is due, because arrivals are bursty and review capacity is not storable.

The right treatment is a queueing model with class-based priority and an explicit service discipline. This version of the framework does not have one, and the author is not the right person to build it.

If you know queueing theory, the specific questions are:

- What is the right arrival process for PMO decision demand? Poisson is almost certainly wrong, because demand is driven by governance cycles and clusters around gates and board dates.
- Given a class-based priority discipline, what utilisation should a PMO target so that the probability of a review being dropped in any given week stays below some threshold? The answer is presumably well below `O = 1.0`, and knowing how far below would change the guidance in section 2.
- Does the `at_limit` band at `0.95 ≤ O ≤ 1.0` have any principled basis, or is it a guess? It is currently a guess.
- How does agentic containment interact with the queue? A verifier removes the easy decisions, which changes the service time distribution as well as the arrival rate.

Open an issue labelled `queueing`, or send a draft. Co-authorship on any resulting write-up is offered and expected.

---

## Other contributions

Welcome, in roughly this order of usefulness.

**Worked classifications.** Real decision types from your domain, classified, with the reasoning. Especially from outside project delivery, since limitation 9 says the classes are PMO-shaped and nobody has tested that.

**Reference implementations in other languages.** The Python package is a reference, not a product. A port that makes the definitions unambiguous in another ecosystem is useful. Keep the dependency count at zero if you can.

**Corrections to the specification.** If a definition is ambiguous, that is a defect. Ambiguity in a specification is worse than an error, because an error gets caught and an ambiguity gets implemented two different ways.

**Documentation that makes it easier for a non-technical PMO director to use.** The README is meant to be implementable with no code at all. If you got stuck somewhere, say where.

---

## Ground rules for the prose

If you are editing the README or anything in `spec/`, please match the existing voice.

- Plain, direct, practitioner voice.
- No em dashes, and no stylised substitutes for them. Commas, colons, semicolons and full stops are enough.
- No marketing language. Do not describe the framework as proprietary, and do not add trademark symbols. Adoption is the point.
- Avoid: delve, leverage, robust, seamless, transformative, unlock, crucial, pivotal, landscape, navigate, foster, cutting-edge, revolutionise, game-changing.
- British spelling.
- Numbers are set in mono, sentences in sans. See [brand/README.md](brand/README.md).
- Say what is not known. A limitation stated plainly is worth more than a claim that survives one conversation.

---

## Working on the code

```bash
git clone https://github.com/hotragn/verb.git
```

```bash
pip install -e ".[dev]"
```

```bash
pytest
```

Standards:

- **The `vb` package has no runtime dependencies and will not acquire any.** `jsonschema` and `pytest` are development dependencies only. If you need a third-party package to implement something in `vb`, that is a signal the something belongs elsewhere.
- Full type hints on everything public.
- Tests for every module. Coverage on the calculation logic stays above 85 percent; it is currently 96 percent overall.
- A test that reproduces a figure quoted in the README is worth more than a test that exercises a branch. See `tests/test_examples.py`, which fails if the README goes out of date.
- Docstrings explain why, not what. The formula is four symbols; the reason Class D returns `policy_violation` rather than `overdraft` is the part worth writing down.

If you change a definition, the change touches four places and all four need updating together:

1. The README, which is the specification.
2. The relevant file in `spec/`.
3. The implementation in `vb/`.
4. The tests, including any figure in `tests/test_examples.py`.

If you change the schemas, re-run the fixture builder:

```bash
python schema/fixtures/build_fixtures.py
```

If you change the example generator, regenerate and check the headline figures still hold:

```bash
python examples/generate_pmo40.py
```

---

## Conduct

Be straightforward and assume good faith. Disagree with the ideas as hard as you like; the framework is more likely to be wrong than you are to be rude.

Two things to avoid:

- Do not send verification cost data that identifies individuals. Class-level aggregates only. [Silent drift](spec/metrics.md#3-silent-drift-rate-sdr) must never be reported per person, and that applies here as well as in your own organisation.
- Do not open issues asking whether the framework applies to your situation without saying what your situation is. The answer depends entirely on whether your review capacity is the binding constraint, and only you can see that.

---

## Licence

Contributions are accepted under the Apache License 2.0, the same licence as the rest of the repository. By opening a pull request you confirm you have the right to contribute the work under those terms.
