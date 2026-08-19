# Examples

## PMO-40

A synthetic portfolio of 40 projects, 14 reviewers and 8 weeks of decision log.

> **These numbers are synthetic.** PMO-40 is an organisation that does not exist. The bundle demonstrates that the arithmetic works and the tooling reproduces. It is not a measurement of anything and it should never be cited as evidence. See [limitation 8](../README.md#10-known-limitations).

```bash
vb budget --input examples/pmo40
```

```bash
vb metrics --input examples/pmo40
```

```bash
vb drift --input examples/pmo40 --decision-class C
```

```bash
vb gates --input examples/pmo40
```

Regenerate it:

```bash
python examples/generate_pmo40.py
```

The generator is seeded and reproduces byte for byte. CI checks this, because an example that quietly drifts away from the figures quoted in the README is worse than no example.

## What the bundle shows

| | Figure | Why it is in there |
|---|---|---|
| Class C overdraft | **3.31x** | The headline. 49 of 70 weekly decisions have no verification capacity. |
| Class C drift | 0.13 rising to 0.52 | The lag. The overdraft is constant from week 1, but drift takes six weeks to show, because backlog absorbs it first. |
| Class C queue | 310 decisions | What the backlog looks like after 8 weeks against a budget of 21 a week. |
| Class A containment | k = 0.69 | A verifier that passes Gate 3, banked at the lower bound of its interval rather than at the point estimate. |
| Class B containment | k = 0 | A verifier that misses the false-negative bar. Assigned zero and kept running as an advisory annotation. Designed, not drawn. |
| Class C containment | none | Deliberate. Agentic verification supplies budget where a machine-checkable verdict is possible, which is where checking was already cheap. It does nothing for the class that is drowning. |
| Class D | 0 autonomous | Never delegated. Any non-zero figure here is a contract breach, not an overdraft. |

## Files

```
pmo40/
  config.json         class inputs, floors, the period length
  decision_log.jsonl  4,400 decisions over 8 weeks, one per line
  reviewers.csv       14 reviewers and the classes each is qualified for
  projects.csv        the 40 projects
  timing.csv          the calibrated sample that c-hat and the drift floors come from
  gate_data.json      inputs for all four eval gates
generate_pmo40.py     the seeded generator
```

## Making your own bundle

`config.json` is the only required file. Everything else is optional and the tools degrade to whatever is present: with just a config you get budgets, add a decision log and you get metrics and drift, add `gate_data.json` and you get the gates.

Start by copying `pmo40/config.json`, replacing the class inputs with your own measured numbers, and pointing `vb budget` at the directory.
