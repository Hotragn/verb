# Deadlines, class priority and selective containment

This contribution addresses the queueing question in `CONTRIBUTING.md`.
All inputs below are synthetic. The examples identify information that a
capacity ratio cannot supply. They do not estimate a safe utilisation target
for a real organisation.

## A finite-calendar model

There is one reviewer qualified for both B and C decisions. The reviewer has
2,400 available minutes in a week. Time counts available review minutes, so
the model does not represent lunch, overnight gaps or other calendar effects.
Each review has an arrival time, a service requirement and a deadline.
Service is non-preemptive. FIFO orders by arrival and then identifier.
Class priority selects C before B among waiting reviews, with FIFO ties.
Priority never interrupts a review already in service.

Every review stays in the queue until completed, including after its deadline.
The outcome is a missed deadline. It is not an abandoned review or an approval
without verification. No behavioural model of rubber-stamping is assumed.
The queue starts empty. Results describe this finite workload, not a stationary
queue or a sequence of independent weeks.

## Equal offered load, different completion outcomes

Twenty C reviews require 96 minutes each. Their combined requirement is
1,920 minutes, giving offered load `O = 0.8`. All are due at minute 2,400.

| Arrivals | Reviews completed by deadline | Late reviews | Work remaining at deadline |
|---|---:|---:|---:|
| One every 120 minutes, starting at zero | 20 | 0 | 0 minutes |
| All at minute 1,920 | 5 | 15 | 1,440 minutes |

The second row has only 480 available minutes after the batch arrives.
Exactly `floor(480 / 96) = 5` reviews can finish. The other 15 eventually
finish, with the last completion at minute 3,840.

More generally, no positive threshold on average offered load alone can
guarantee a common deadline. Fix any `0 < rho < 1`, available time `H`, and
`N` identical reviews of duration `s = rho * H / N`. Release all of them at
`H - epsilon`, where `0 < epsilon < s`, and give all of them deadline `H`.
Then their offered load is `rho`, but none finishes by the deadline. This
construction assumes that late releases are permitted. A useful guarantee
therefore needs restrictions on arrivals, service durations and deadlines.

`burst_sensitivity.csv` reports 20 deterministic cases spanning offered loads
0.25, 0.50, 0.75 and 0.95, and five common release times. These are sensitivity
cases, not a probability distribution. Their average is not an estimated
weekly failure probability.

## Priority changes which class misses its deadline

A second batch arrives at minute 1,920: 32 B reviews of 30 minutes and eight
C reviews of 120 minutes. B identifiers precede C identifiers. Total work is
again 1,920 minutes and all deadlines are minute 2,400.

| Discipline | B completed on time | C completed on time | Total late |
|---|---:|---:|---:|
| FIFO | 16 | 0 | 24 |
| C before B | 0 | 4 | 36 |

The priority rule improves timely C completion while increasing the number
of late reviews overall. Both schedules leave 1,440 minutes of work at the
deadline. Counting late reviews and counting unfinished work answer different
questions. A proposed priority policy needs explicit class-specific costs or
service requirements before one can call it preferable.

## Containment changes the conditional service distribution

Let `S` be human service time and `Z = 1` mean a review remains for a human.
The exact residual human workload per original arrival is
`E[S * Z] = P(Z = 1) * E[S | Z = 1]`. Reusing `E[S]` in the second factor
assumes that selection leaves the mean unchanged.

For 80 easy reviews of 15 minutes and 20 hard reviews of 120 minutes, the
original mean is 36 minutes and total work is 3,600 minutes. Containing all
80 easy cases leaves a 120-minute mean and 2,400 minutes of human work.
The constant-mean calculation predicts only 720 minutes. It understates the
residual work by a factor of `10 / 3`.

Selection alone still reduces total human work from 3,600 to 2,400 minutes.
An increased residual mean does not imply an increased total workload when
the original arrivals are fixed and containment adds no human work. Any
additional oversight cost or induced demand needs to be modelled separately.

## Reproduction and verification

From the repository root:

```bash
python examples/queueing.py examples/queueing_results
PYTHONPATH=. python -m pytest tests/test_queueing_example.py -q
```

The generator has no third-party dependencies. It writes the summaries,
individual scheduling traces and sensitivity table. Tests compare the event
scheduler with an independent minute-by-minute simulator on 200 fixed-seed
workloads, check the analytic counts above, and check deadline equality and
non-preemptive service.

The next empirical step would require arrival timestamps, review durations,
deadlines, reviewer availability and class labels from participating teams.
Those observations are not supplied here. No Poisson arrival assumption,
calibrated weekly risk estimate, or replacement for the current status bands
is proposed by these examples.
