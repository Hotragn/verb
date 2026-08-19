layout: default
dense: true
section: Layer 1, processes
---
## The deployment order most PMOs use is backwards.

<div class="quad">
  <div class="go"><div class="qt">go first</div>
    <div class="qd">Easy to build, cheap to check. Start here today. Less
    glamorous than the box to its right, and the only box that scales.</div></div>
  <div class="hot"><div class="qt">hold</div>
    <div class="qd">Easy to build, expensive to check. This is the trap, and it
    is where every impressive demo lives.</div></div>
  <div><div class="qt">go second</div>
    <div class="qd">Hard to build but cheap to check. Worth the engineering.</div></div>
  <div><div class="qt">never yet</div>
    <div class="qd">Hard and expensive to check. Keep it human for now.</div></div>
</div>

<div class="margin"><b>Horizontal</b><br>task difficulty for the model, easier on
the left.<br><br><b>Vertical</b><br>verification cost, cheaper at the top.</div>

<hr>

<div class="cols">
<div><h4>What most teams do</h4>
<p class="small">Deploy along the difficulty axis. Easiest first, hardest last.
It feels rational and it is how every roadmap gets drawn.</p></div>
<div><h4>What actually governs you</h4>
<p class="small">Deploy along the verification axis. You can only run as much
autonomy as you can check, so cheap-to-check work is the only work that
scales.</p></div>
</div>

@notes

This is the same idea as the quadrant in Part 1, turned into a sequencing rule
rather than a warning. If you are short on time, say that and move faster here.

The sentence that makes it concrete, and it is worth memorising:

Risk analysis is the easier AI problem. It should go live later than status
reporting.

That inverts what everybody in the room has on their roadmap, and it inverts it
for a reason they can check. Status reporting is checkable against the source
systems in minutes. A risk analysis needs somebody who knows the programme.

Expect pushback on the grounds that risk analysis is more valuable. Agree. Value
is not the axis. Value tells you what you want; verification cost tells you what
you can run.
