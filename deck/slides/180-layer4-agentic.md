layout: default
dense: true
section: Agentic verification
---
## Agents can supply review capacity, not just consume it.

```formula
  c_eff = c_a + (1 - k) x c
```

<p>Put a second agent in front of the human. It closes some decisions on its own,
with a machine-checkable reason. <strong>k</strong> is the share it closes. The
budget goes up without hiring anybody.</p>

<h4>Three rules, or this becomes wishful thinking</h4>

<ol>
<li><strong>The verifier's own output has to be machine-checkable.</strong> If a
human has to read its reasoning, you moved the cost, you did not remove it.</li>
<li><strong>Measure how often it misses a bad decision.</strong> Unmeasured means
it counts as zero. Not an estimate. Zero.</li>
<li><strong>Bank the bottom of the confidence range, never the headline.</strong></li>
</ol>

@notes

This is the part that is genuinely new, so give it room. It is also the part
that is easiest to sell badly, so lead with the rules rather than the upside.

Rule two is the one to press on. An agent checking an agent is a lovely diagram
and a risk transfer unless somebody has measured its miss rate against decisions
known to be bad. Until then it is an opinion with a confident tone.

There is a sting worth mentioning if the room is technical: the verifier closes
the easy ones first, so the queue that reaches the human gets harder, so c goes
up as k goes up. Re-measure after every change. The repo says the framework has
no clean correction for this, which is the honest position.
