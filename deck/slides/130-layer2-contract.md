layout: default
section: The agent role contract
---
## Every agent gets four fields. Not nine.

<div class="cols">
<div>
<ul>
<li><strong>Scope.</strong> Which decisions it may make, named one by one. Anything
unnamed is out, and running into one is a stop.</li>
<li><strong>Evidence.</strong> What it must show for every decision. If it cannot
produce the evidence, it does not make the decision.</li>
</ul>
</div>
<div>
<ul>
<li><strong>Escalation.</strong> The named conditions where it stops, and the named
human it stops to.</li>
<li><strong>Revocation.</strong> How you turn it off, who can, how fast, and what
happens to work in flight.</li>
</ul>
</div>
</div>

<p class="small">Four is the number somebody can hold in their head at six on a
Friday when the thing is misbehaving and a call has to be made. That is the only
moment the contract has to work.</p>

@notes

Say why the number is four rather than a longer, safer-looking list. A contract
gets read twice: once at approval when everyone is calm, and once during an
incident. Only the second reading matters, and a fifteen-field contract fails it.

Revocation is the one people leave out, and the one to press on. Ask the room:
who here could turn off their AI tooling this afternoon without a meeting. It
usually goes quiet.

If somebody says four is too few, the answer is that rate limits go in scope,
retention goes in evidence, on-call goes in escalation, and the kill switch goes
in revocation. Nothing genuine has needed a fifth.
