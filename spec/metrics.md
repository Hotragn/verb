# The six operating metrics

Normative specification. Short form in [README section 7](../README.md#7-the-six-operating-metrics). Reference implementation in [`vb/metrics.py`](../vb/metrics.py) and [`vb/drift.py`](../vb/drift.py).

**All six are reported per decision class, per period.** Portfolio-wide reporting averages a healthy Class A over a drowning Class C and shows nothing. The PMO-40 example has a portfolio-wide overdraft ratio of about 0.2 and a Class C overdraft ratio of 3.31. Only one of those numbers is worth knowing.

| # | Metric | Symbol | Unit | Target |
|---|---|---|---|---|
| 1 | Verification Budget | `VB` | decisions / period | measured, not targeted |
| 2 | Overdraft Ratio | `O` | ratio | ≤ 1.0 |
| 3 | Silent Drift Rate | `SDR` | fraction | ≤ baseline + 0.05 |
| 4 | Containment | `k` | fraction | measured, reported with FNR |
| 5 | Escalation Precision | `EP` | fraction | ≥ 0.7 |
| 6 | Reversal Latency | `RL` | hours | ≤ one review cycle |

---

## 0. The measured input: ĉ

Not one of the six. It is the input all six rest on, and it is the number most organisations do not have.

> **`c` must be measured, not estimated.** An estimated `c` produces a budget that is a restatement of your assumptions in the shape of arithmetic.

### 0.1 Measurement protocol

1. **Sample.** At least 30 decisions per class per measurement round. Randomly, across reviewers and across days of the week. Friday afternoon reviews are not representative of Tuesday morning reviews and both belong in the sample.
2. **Time.** Wall-clock from artifact-open to approval-submit, per reviewer, per decision. Instrument the review tool. Self-reported durations are unusable: people report what a careful review should take.
3. **Trim.** Remove idle gaps over 10 minutes. A reviewer who opened an artifact, went to a meeting, and came back has not spent 90 minutes on it. 10 minutes is a convention, not a finding; use a different threshold if yours is better, but write it down and keep it fixed.
4. **Confirm.** Ask the reviewer afterwards whether they genuinely checked. Discard the ones where the answer is no. **This is the step everybody skips and it is the step that makes the number mean something.** Without it you are measuring approval duration, not verification cost, and under overdraft those are different quantities.
5. **Aggregate.** `ĉ` is the **median** of what survives. Not the mean. The distribution is right-skewed, with a long tail of hard cases, and the mean flatters the budget by pulling toward the tail.
6. **Re-measure.** Quarterly, and after any material change to the evidence plane, the median artifact length, or `k`.

### 0.2 Reporting

Report `ĉ` with its sample size, date, and interquartile range:

```
    Class C   ĉ = 1.25 h   IQR [0.85, 2.10]   n = 34   measured 2026-07-08
```

The IQR is not decoration. A class whose IQR spans an order of magnitude is not one class, and the correct response is to split the decision type, not to average it.

### 0.3 Known bias, stated every time

Reviewers check more carefully when observed. `ĉ` measured under observation is therefore **biased low**, so `VB` is **biased high**, so real overdraft is **worse than reported**. The direction is known. The size is not. Say this out loud whenever you present a budget. It costs you nothing and it is the difference between a model people trust and a model people trust once.

---

## 1. Verification Budget, VB

### Definition

```
                R × H × u
        VB  =  -----------
                    c
```

Per class, per period.

| Symbol | Definition | Unit |
|---|---|---|
| `R` | Reviewers qualified for this class | people |
| `H` | Nominal review hours per qualified reviewer per period | hours |
| `u` | Utilisation, fraction of `H` actually available for verification | 0 to 1 |
| `c` | Measured verification cost per decision, `ĉ` | hours |

Units: `people × (hours/person/period) × 1 / (hours/decision) = decisions/period`.

### Counting R

`R` is the number of people **whose approval on this class of decision would survive scrutiny**. Not headcount, not FTE, not people with the button.

The test: if this decision went wrong and was examined, would the organisation defend this person's approval as a qualified judgement? If not, they are not in `R` for that class. A person can be in `R` for Class B and not for Class C on the same decision type.

Counting people with permissions rather than people with qualification is the most common way `VB` gets overstated, and it overstates it in exactly the direction that hides the overdraft.

### Setting u

`u` is measured, not chosen. Take a fortnight of calendars for the qualified reviewers, subtract everything that is not review time, divide.

| `u` | Reading |
|---|---|
| 0.4 to 0.7 | Realistic range for a working PMO |
| above 0.7 | Almost always fiction. Check what has been left out. |
| below 0.3 | Real, and the cheapest available lever is here, not in `c` |

`u` is the only input in the formula that a manager can move in a week, by protecting review time. It is worth measuring first for that reason.

### Class D

`VB_D` is not defined, and setting it to zero is a modelling convenience, not a statement about capacity. A Class D decision has no finite `c`, so the quotient has no value. In the reference implementation, `evaluate_class` returns `budget = 0.0`, `overdraft_ratio = None`, and status `unbudgeted` when demand is zero, or `policy_violation` when an agent has taken any Class D decisions autonomously. A policy violation is not an overdraft. It is a contract breach and it is handled by revocation, not by the budget.

### With agentic verification

```
        c_eff = c_a + (1 - k) × c
        VB_eff = (R × H × u) / c_eff
```

Rules on `k` in [section 4](#4-containment-k).

---

## 2. Overdraft Ratio, O

### Definition

```
        O = D / VB
```

`D` is demand: decisions of this class produced in the period, by agents and by people.

### Derived quantities

```
        verified_fraction    = min(1, VB / D)
        unverified_decisions = max(0, D - VB)
        headroom             = VB - D                (negative under overdraft)
```

### Status bands

| Range | Status | Meaning |
|---|---|---|
| `O < 0.95` | `in_budget` | Review is real |
| `0.95 ≤ O ≤ 1.0` | `at_limit` | No absorption capacity for a bad week |
| `O > 1.0` | `overdraft` | The excess is approved without being verified |

The `at_limit` band exists because a budget with no slack fails on the first burst, and [limitation 3](../README.md#10-known-limitations) means bursts are guaranteed. Treat `at_limit` as a planning trigger, not a passing grade.

### Interpretation

`unverified_decisions` is not "decisions at risk of being unverified". It is the count of decisions for which no verification capacity exists. The arithmetic does not leave anywhere else for them to go. Under `O = 3.31` with `D = 70`, about 49 decisions per week carry an approval that no qualified reviewer had the capacity to make.

### Counting D

Count decisions, not artifacts, not tasks, not tokens. A decision is an artifact with all six evidence plane fields, per [evidence-plane.md](evidence-plane.md). Outputs are not decisions and are not counted, and they must not be actioned either.

Escalations count as demand at the class cost of the escalated decision. An agent that escalates everything consumes the same budget as an agent that decides everything, which is why [escalation precision](#5-escalation-precision-ep) is one of the six.

---

## 3. Silent Drift Rate, SDR

The headline metric. Everything else measures capacity. This measures whether the approvals are real.

### 3.1 Definition

For decision class `X` with floor `f_X` hours, over approval events `i = 1..N` in the period:

```
        drift_i = 1   if  d_i < f_X
                  0   otherwise

                        N
        SDR_X  =  (1/N) Σ  drift_i
                       i=1
```

where `d_i` is the **idle-trimmed** duration from artifact-open to approval-submit, for the reviewer of record, using the same 10-minute trim as the `ĉ` protocol.

Only approvals are counted. Rejections are excluded: a fast rejection is often a good rejection, because the reviewer spotted something immediately, and including them would penalise exactly the behaviour you want.

### 3.2 Setting the floor

The floor is not a target and not a policy. It is the line below which a genuine review could not have physically happened.

```
        f_X = max( P10(baseline durations for class X),
                   W_X / 240 / 60 )
```

where `W_X` is the word count of the median artifact for that class, and 240 is words per minute.

**Term 1: the calibrated baseline P10.**

- Collect at least 30 reviews per class during a **calibrated period**: reviewers observed, and each confirming afterwards that they genuinely checked. This is the same collection round as the `ĉ` measurement, and doing both at once is the practical way to afford it.
- Take the 10th percentile of those durations, by linear interpolation between order statistics.

**Term 2: the physical reading floor.**

- `W_X / 240 / 60` hours. 240 words per minute is a defensible skim-to-comprehend rate for technical material.
- This term exists to catch the case where the baseline itself was collected under mild time pressure and its P10 is already too low. It is a floor on the floor.

**Take the larger of the two.**

**Re-derive** quarterly, or whenever the median artifact length moves by more than 25 percent. Artifact length moves when the evidence plane changes, so an evidence plane change means a floor change, always.

### 3.3 Why P10 and not the median

You are not trying to catch fast reviewers. Fast reviewers are good. You are trying to catch reviews that **could not have occurred**.

P10 of a calibrated baseline is a conservative "nobody who is genuinely checking goes faster than this" line. The median would flag half of all genuine reviews and the metric would be discarded within a month, correctly.

### 3.4 The 10 percent baseline

By construction, a P10 floor produces `SDR ≈ 0.10` when nothing is wrong, because 10 percent of the calibrated baseline was below its own 10th percentile. So the signal is not `SDR`. The signal is:

```
        excess_drift = max(0, SDR_X - 0.10)
```

Report excess drift. An `SDR` of 0.11 is a healthy system. An `SDR` of 0.34 is a PMO where a third of approvals are decorative.

If you use a percentile other than P10, the baseline changes to match: `baseline = percentile / 100`. The reference implementation takes the percentile as a parameter and derives the baseline from it rather than hard-coding 0.10, so the two cannot drift apart.

### 3.5 Trend

Fit an ordinary least squares slope across per-period `SDR` values, periods indexed `0, 1, 2, ...`:

```
              Σ (t_i - t̄)(SDR_i - SDR̄)
        β  =  --------------------------
                   Σ (t_i - t̄)²
```

| `β` (drift fraction per period) | Label |
|---|---|
| `β > +0.02` | `rising` |
| `-0.02 ≤ β ≤ +0.02` | `flat` |
| `β < -0.02` | `falling` |

Fewer than three periods returns `insufficient_data`. Do not label a trend on two points.

**The diagnostic signature.** Rising drift with `O > 1` is what this framework predicts and it has a characteristic lag: the overdraft first becomes backlog, then becomes late nights, then becomes drift. Backlog absorbs the overdraft for several weeks, which is why drift usually lags overdraft by a month or two, and why people conclude the overdraft was harmless. It was not. It was queued. The PMO-40 example shows the lag explicitly: constant `O = 3.31` from week 1, `SDR` rising from 0.12 to 0.52 across eight weeks, queue depth reaching 140.

### 3.6 Secondary signals

Reported alongside `SDR`, never used as the metric. They are pattern detectors, and patterns have innocent explanations often enough that acting on them directly would be wrong.

**Variance collapse.** Coefficient of variation of review durations within a class and period:

```
        CV = σ(d) / mean(d)
```

`CV < 0.15` means reviews have become uniform. Real reviews are not uniform, because real decisions differ in difficulty. Uniformity means the duration is being set by something other than the decision, usually a habit or a target.

**Batch bursts.** Three or more approvals by the same reviewer within 60 seconds. Occasionally legitimate: a reviewer who queued five artifacts, read them all, and then clicked through. Never legitimate as a sustained pattern. Report as a count of bursts and a share of approvals inside a burst.

### 3.7 The rule that keeps the metric alive

> **`SDR` is never used for individual performance management.**

The moment it is, review duration becomes a thing people manage rather than a thing you measure. Reviewers leave artifacts open. Durations rise. `SDR` falls to zero and stays there, and you have lost the only instrument that sees the failure mode this framework is about.

Report by class, not by person. Store per-person durations if you must, for the CV calculation, and put them behind an access control that makes casual use awkward. This is not a nicety, it is a measurement-validity requirement, and [limitation 4](../README.md#10-known-limitations) says it again: if your organisation cannot resist using it against individuals, do not collect it. A corrupted metric is worse than a missing one, because a missing metric does not tell you everything is fine.

---

## 4. Containment, k

### Definition

```
              decisions closed by the verifier without human involvement
        k  =  ---------------------------------------------------------
                       total decisions offered to the verifier
```

"Closed" means either passed, or rejected with a machine-checkable reason and returned to the originating agent. A decision the verifier could not decide is not contained; it goes to a human and counts in the denominator only.

### The mandatory companion: false-negative rate

```
              bad decisions the verifier passed
        FNR = --------------------------------
                  total bad decisions in the labelled set
```

> **`k` reported without `FNR` is not a metric, it is a claim.**

A verifier that passes everything has `k = 1.0` and `FNR = 1.0`. The first number looks like a triumph. Reporting them together is the only thing that stops it being reported as one.

### Confidence interval and what the budget uses

Report `k` with a 95 percent confidence interval. Use the **Wilson score interval**, which behaves properly at proportions near 0 and 1 where the normal approximation does not:

```
                 p̂ + z²/2n  ±  z √( p̂(1-p̂)/n + z²/4n² )
        CI  =   -------------------------------------------
                              1 + z²/n
```

with `z = 1.96`, `n` the number of decisions offered, `p̂` the observed containment.

> **The budget uses the lower bound.** Never the point estimate.

The gap is the margin between a good quarter of measurement and a permanent assumption. In the PMO-40 verifier contract, the point estimate is 0.71 and the lower bound is 0.652, a difference of about 8 percent of `VB` for the covered classes.

### Uncalibrated verifiers

`k = 0`. Not "assume 0.5". Not "estimate from the logs". Zero. See [Gate 3](eval-gates.md#gate-3-verifier-calibration). A verifier that fails Gate 3 keeps running as an advisory annotation, which still helps a human by pointing at what to look at, but it contributes nothing to the budget until it is calibrated.

### The adverse-selection correction, which does not exist

A verifier closes the easy decisions first. The residual queue reaching the human is therefore harder than the original average, so **`c` rises as `k` rises**.

The framework has no closed-form correction for this and this version does not attempt one. The operating rule is: **re-measure `ĉ` after every material change to `k`**, using the full protocol in section 0.1, and never carry a pre-verifier `ĉ` into a post-verifier budget. A budget that holds `c` constant while `k` climbs over-reports capacity precisely when the overdraft is growing, which is the worst possible time for a metric to be optimistic. This is [limitation 6](../README.md#10-known-limitations) and it is the most consequential known gap in the model.

---

## 5. Escalation Precision, EP

### Definition

```
              escalations a human agreed needed escalating
        EP =  --------------------------------------------
                        total escalations
```

Measured by asking the receiving human, at resolution, one question: did this need to come to you? Record the answer. It costs about five seconds and it is the only source for this metric.

### Target and interpretation

`EP ≥ 0.7`.

Below 0.7, the agent is spending your scarcest resource on decisions that did not need a human. Escalations consume verification budget at the class cost of the escalated decision, so a low `EP` is a direct, quantifiable drain: at `EP = 0.4`, 60 percent of escalation budget is spent on nothing.

An `EP` near 1.0 is not necessarily good. It can mean the thresholds are so conservative that only obvious cases escalate, which is a recall problem hiding as a precision success.

### The recall gap, stated honestly

What you actually want is **escalation recall**: of the decisions that should have been escalated, how many were? You cannot measure it directly, because you do not observe the escalations that should have happened and did not.

Three partial proxies, none sufficient:

1. **Reversal-triggered recall.** Of decisions later reversed, what fraction had been escalated? Low means the agent is missing cases. Undercounts, because it only sees failures that were caught.
2. **Injected probes.** Insert known-bad decisions into the stream at a low rate and measure how many the agent escalates. Closest to a real measurement. Requires care, an audit trail for the injections, and a policy that says clearly what happens if a probe reaches production.
3. **Shadow review.** Have a human review a random sample of non-escalated decisions. Expensive, because it consumes the same verification budget the framework is trying to protect, which is why almost nobody does it.

Probes are the recommended approach where the domain allows it. Where it does not, say that recall is unmeasured rather than implying `EP` covers it. This is a real gap in the framework, not a gap in your implementation.

---

## 6. Reversal Latency, RL

### Definition

```
        RL = median( t_reversed - t_decided )
```

over decisions that were reversed in the period, in hours. Report median and P90; the tail is where the damage is.

### Target

`RL ≤ one review cycle`. If your review cycle is a week, `RL ≤ 168` hours.

### What it actually tells you

`RL` audits the `reversal` field of the [evidence plane](evidence-plane.md#25-reversal). That field states `cheap_until`, and reviewers use it to justify lighter checks on reversible decisions. If reversals routinely land after `cheap_until`, the field is fiction, the lighter checks were unjustified, and any class assignment that relied on reversibility needs revisiting.

Report the crossing rate directly:

```
        reversal_window_breach_rate = fraction of reversals occurring after cheap_until
```

Above about 0.2, treat `reversal.cheap_until` as unreliable across the board and re-run Gate 1 on the affected decision types under tie-breaker T1, the reversibility override.

### The counting problem

`RL` only sees reversals that happened. Decisions that were wrong and never reversed do not appear, and there is no way to count them from the log. `RL` is therefore a lower bound on how bad reversal performance is, and it is best read next to `SDR`: a system with low `RL` and high `SDR` is reversing quickly the small number of errors it happens to notice.

---

## 7. Reporting

A period report is one table per class:

```
  Class C                          period 2026-W33
  ------------------------------------------------
  VB                     21.12  decisions/week
  Demand                 70.00  decisions/week
  Overdraft O             3.31x                 OVERDRAFT
  Unverified             48.88  decisions/week
  SDR                     0.52     excess 0.42   RISING (+0.057/wk)
  Floor f_C               0.30  h                (P10 basis, n=34, 2026-07-08)
  Containment k           0.00                   no verifier on Class C
  Escalation precision    0.74
  Reversal latency       36.0  h  (P90 112.0)    breach rate 0.11
  ĉ                       1.25  h  IQR [0.85, 2.10]  n=34  measured 2026-07-08
  ------------------------------------------------
  Secondary: CV 0.31 (ok)   batch bursts 3 (0.4% of approvals)
```

Generate it:

```bash
vb metrics --input examples/pmo40
```

### Four presentation rules

1. **Always per class.** A portfolio number hides the only class that matters.
2. **Always with the date and sample size of `ĉ`.** A budget computed from a `ĉ` measured fourteen months ago is a historical document.
3. **Always with the observation bias stated.** Section 0.3. One sentence, every time.
4. **Never `SDR` by person.** Section 3.7.
