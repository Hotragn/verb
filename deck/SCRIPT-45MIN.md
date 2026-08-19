# Speaker script, 45 minutes

28 slides. 45 minutes talking, 15 minutes questions.

`[HOST]` marks the two places to name the event and the organiser. Everything else is host-neutral and reusable.

**How to use this.** Each slide gets a block. The bold line at the top of a block is the one sentence that has to land; everything under it is support you can cut live. Nothing here reads the slide out loud. The slide holds the numbers and the tables, you hold the argument.

**Paste this straight into Notion.** Headings become toggles you can collapse, so you can keep the whole talk on one page and open only the slide you are on.

**Two markers to watch for:**

- `[ASK]` is an audience prompt. Every one has a `[ROLLBACK]` immediately after it. If nobody types in chat within about five seconds, say the rollback line and move on. Do not wait. A silent Zoom audience is normal and the rollback is written so the silence costs you nothing.
- `[DEMO, OPTIONAL]` is a live demo you are not planning to run. Skipped by default. The script is there in case you decide to, and the block tells you what to say instead when you skip it, which is the default.

**The through-line.** Part 1 says your limit is not the model. Part 2 says how to build the thing anyway. Part 3 says what it buys you and what to do first. If you only get one idea across, it is that this is a permission structure: it tells you where you can go faster.

---

## Running order

| # | Slide | Minutes | Running |
|---|---|---|---|
| 1 | Title | 1:30 | 1:30 |
| 2 | Part 1 divider | 0:25 | 1:55 |
| 3 | Thirty years | 1:40 | 3:35 |
| 4 | What did not move | 1:40 | 5:15 |
| 5 | Nobody decides to | 2:00 | 7:15 |
| 6 | The formula | 2:10 | 9:25 |
| 7 | Six people, twenty-one | 2:00 | 11:25 |
| 8 | Four classes | 2:10 | 13:35 |
| 9 | The quadrant | 1:55 | 15:30 |
| 10 | Part 2 divider | 0:25 | 15:55 |
| 11 | Five layers | 1:10 | 17:05 |
| 12 | Deployment order | 1:55 | 19:00 |
| 13 | The contract | 1:55 | 20:55 |
| 14 | The people | 1:40 | 22:35 |
| 15 | Blast radius | 1:55 | 24:30 |
| 16 | The evidence plane | 1:55 | 26:25 |
| 17 | Reference shape | 1:40 | 28:05 |
| 18 | Agentic verification | 2:10 | 30:15 |
| 19 | Six numbers | 1:10 | 31:25 |
| 20 | Measuring drift | 1:40 | 33:05 |
| 21 | The dashboard | 1:55 | 35:00 |
| 22 | Four gates | 1:55 | 36:55 |
| 23 | Part 3 divider | 0:20 | 37:15 |
| 24 | S0 to S4 | 1:30 | 38:45 |
| 25 | What I do not know | 1:25 | 40:10 |
| 26 | What this buys you | 1:45 | 41:55 |
| 27 | Monday | 1:25 | 43:20 |
| 28 | Take it and use it | 1:00 | 44:20 |

**44:20 talking.** Leaves about forty seconds of slack per ten minutes, which is roughly what you lose to breathing and to one person unmuting by accident.

**If you are running long at slide 22**, cut 14 and 17. You lose the roles table and the architecture picture, and the argument still holds.

**If you are running short at slide 22**, the reserve blocks at the bottom add up to about six minutes.

---

## 1. Title

**Set the promise: they leave knowing how to build this and what it costs to check it.**

`[HOST]` Thank the organiser by name and the host for the invitation.

One line about you: CTO at Future Median, a non-profit, and you spend your time on how autonomous systems get supervised rather than on how they get built.

Then the promise, and make it specific because a vague promise makes people open their email:

> In forty-five minutes I want to give you one number, four categories, and a way to decide which of your work an agent should touch first. All of it is on GitHub under Apache 2.0. The formula, the schemas, a calculator, and the code that produces every figure I am about to show you.

Point at the QR code on the last slide now, not at the end. It stops people photographing slides for the next forty minutes.

Say what this is not: not a tool demo, not a vendor pitch, nothing to buy. You will mention one repository, it is yours, and it is free.

---

## 2. Part 1 divider

**Three parts. Say the shape so people know when to pay attention.**

Part one is why your constraint moved and most roadmaps have not noticed. Part two is the operating model, five layers, and it is the longest part because it is the part you can act on. Part three is where you are today and the smallest useful thing to do about it.

About fifteen minutes on part one.

---

## 3. Thirty years

**For thirty years the scarce thing was producing the work. That is over.**

Tell it as a memory, not a claim. Anyone who has run a PMO recognises the Thursday: chasing seven risk owners for updates, rebuilding a forecast because a change request landed on Tuesday, writing the same status narrative forty times with different names in it.

Capacity planning meant counting the people who could produce those artifacts. Every tool we bought for twenty years was aimed at that bottleneck.

Land the change plainly:

> A competent agent now produces a defensible status pack for forty projects in about the time it takes you to open the file.

Then the point, which is not that this is impressive:

Production is no longer the scarce thing. And if you are still planning capacity around production, you are planning around a number that stopped mattering.

---

## 4. What did not move

**Review capacity did not improve when the models improved. Two parts of it got worse.**

Three things set how much you can review: how many people are genuinely qualified to judge this kind of decision, how many hours they actually have, and how long one honest judgement takes.

Go through why none of the three moved.

Qualified people: the model getting better does not qualify anybody new. Hours: still a working week. Time per judgement: unchanged at best.

Then the part people have not thought about, and slow down here:

> Two of the three got worse. Agents generate decisions faster than the queue drains. And the artifacts arrive fluent, which makes them harder to check, not easier.

Give them the fluency point with a concrete image. A junior analyst's draft with an obvious hole in it takes four minutes to reject. A well-written artifact with the same hole takes forty, because you have to work out whether it is wrong before you can say why.

---

## 5. Nobody decides to

**Rubber-stamping is not a discipline problem. It is arithmetic.**

This is the emotional centre of part one. Do not rush it.

Set the scene concretely. It is quarter past five. Nineteen items in the queue. Eleven minutes before the next call. Every one needs about forty minutes of honest checking.

Then:

> Nineteen approvals go in. Every one is recorded as a review.

Pause after that.

Now make sure nobody in the audience feels accused, because half of them are doing this and they will stop listening if they think you are blaming them:

Nobody chose this. That reviewer is behaving rationally under the constraint they were handed. There is no error message. The dashboard turns green. The governance record is complete. And it looks exactly like a working PMO right up to the day something goes wrong and nobody can reconstruct who checked what.

`[ASK]` Drop a number in the chat: how many agent-generated items land in your review queue in a week? Rough is fine.

`[ROLLBACK]` If nothing comes in within five seconds: "Nobody wants to say it out loud, which is fair, and it is usually higher than people expect. Hold your own number in your head for the next slide, because you are going to need it."

If numbers do come in, read two or three out and say you will come back to them at slide 7. Then actually do it.

---

## 6. The formula

**One number. Qualified people, times their hours, times the share that survives the calendar, divided by what one honest check costs.**

Walk the four inputs, and spend your time on the two that people get wrong.

R is not headcount and not people with the approve button. It is people whose approval would survive being examined if the decision went wrong. That is a much smaller number and everybody in the room knows which of their colleagues are in it.

u is the share of nominal review hours that survives meetings, holidays and escalations. Measured, not chosen. Between 0.4 and 0.7 in real organisations. Above 0.7 somebody is not counting something.

Then the one that matters:

> c is what it costs one qualified person to genuinely check one decision. It is the only input with orders of magnitude in it, and it is the one almost nobody has measured.

Say the units out loud, because it makes the whole thing concrete: decisions per week. It is a rate, and you compare it against another rate, which is how many decisions your agents produce.

If the ratio is over one, the difference is not at risk of being unverified. It is unverified. The arithmetic does not leave anywhere else for it to go.

---

## 7. Six people, twenty-one

**Six qualified reviewers produce twenty-one genuine reviews a week. Not two hundred.**

Do the arithmetic slowly and out loud. Six people, eight nominal hours each, fifty-five percent survives the calendar, one honest re-baseline check takes an hour and a quarter.

Let the number sit:

> Twenty-one a week. That is the whole capacity.

Now bring back the chat numbers from slide 5 if you got them. If you did not, use the example: the agents in this scenario produce seventy.

Seventy against twenty-one. Three point three times over.

Then the sentence to land:

> Roughly forty-nine decisions a week carry an approval that nobody had the capacity to make.

Add the credibility line before anyone else raises it, because volunteering it buys you the rest of the talk:

These numbers are synthetic. There is a seeded script in the repository that generates the whole example, and I would rather show you arithmetic that reproduces than a case study you cannot check. What I do not have is measured data from real organisations, and that is the main thing I am asking this audience for.

`[DEMO, OPTIONAL]` Open the calculator, type your own four numbers, show the ratio change live. Two minutes.

`[DEMO SCRIPT]` "This is a single HTML file, no server, no network calls. Four inputs. I put six, eight, point five five, one and a quarter. Twenty-one. Now watch what happens if checking gets cheaper: I halve c, the budget doubles. That is the only lever in the formula with that behaviour."

`[SKIP BY DEFAULT]` Say instead: "There is a calculator in the repository, one HTML file, no install, no network. Put your own four numbers in it tonight and you will have your own version of this slide in about two minutes."

---

## 8. Four classes

**Sort work by what checking costs, not by risk and not by how hard it is for the model.**

This is the move the rest of the talk depends on. Make sure it lands.

Everybody in the room already classifies by risk. Risk tells you whether you must check something. It says nothing about what checking costs. You need both and most operating models only have one.

Go through the four quickly, one example each, and give the tell rather than the definition:

Class A, machine-checkable. A deterministic check decides it. Schedule arithmetic, dependency cycles, budget rollups. The tell: you could write it as a test, and the test passing means the decision is right.

Class B, sample-checkable. Check twenty, draw a conclusion about two hundred. Status narratives, action extraction. The tell: if that sentence makes you uncomfortable, it is not Class B.

Class C, expert-checkable. Somebody qualified has to reconstruct the reasoning against context that is not in the artifact. Re-baselining, change impact. The tell: two qualified people could reasonably disagree, and settling it needs something neither of them wrote down.

Class D, not checkable in advance. Cancelling a workstream. Terminating a contract. Going to a regulator.

Then the rule, and say it as a rule:

> Class D never goes to an agent. Not because it is dangerous. Because it has no finite checking cost, so it has no budget, so there is no amount of it you can afford.

And immediately the thing that saves it from sounding restrictive, because this is where you get most of the value back:

You still get the throughput. The agent prepares the decision. Options, impacts, precedent, what it costs to reverse, a named recommendation. That pack is Class C, a human can check it in bounded time, and the decision itself stays with a person. You get most of the speed without delegating the call.

---

## 9. The quadrant

**Deploy where checking is cheap, not where the task is easy.**

Two axes. How hard the work is for the model, and what it costs you to check.

The four boxes are labelled as actions rather than descriptions, because a quadrant nobody acts on is just a diagram.

Spend your time on the top right. That is where nearly every impressive AI-in-PMO demo lives. Portfolio prioritisation. Vendor dispute strategy. The model is genuinely good at these, and they are all Class C or D, so your capacity is a couple of dozen a week no matter how good the model gets.

Then the line that usually gets a reaction:

> Risk analysis is the easier AI problem. It should go live later than status reporting.

Let that sit for a second, because it sounds wrong. Then resolve it: risk analysis is easier for the model and far more expensive for you to check. Status reporting is duller and checkable against the source systems in minutes. Difficulty and checking cost are different axes and only one of them is your constraint.

You do not fix the top right box by deploying harder. You fix it by making the work cheaper to check, and then deploying. Reclassify, then deploy. That order.

---

## 10. Part 2 divider

**Twenty minutes on how to actually build it. Five layers.**

This is the part you can act on. Five layers, each answering a different question, and four of the five are things you already have and are running without the verification piece.

---

## 11. Five layers

**Processes, roles, governance, technology, metrics. One question each.**

Do not explain all five now. Name them and the question each answers, then move.

The reassuring point, which is worth making because the previous nine slides have been quite heavy:

> Nothing here is a new department. Four of the five are things you already do. What is missing is the checking layer, and that is the whole of the change.

---

## 12. Deployment order

**Most roadmaps sequence by difficulty. The constraint is on the other axis.**

Everybody draws the roadmap the same way: easiest first, hardest last. It feels rational and it is how every roadmap you have ever seen is drawn.

The problem is that difficulty and checking cost are not correlated, and only one of them limits you.

Give the concrete pair. Status reporting: dull for the model, checkable against the source systems in minutes. Risk analysis: interesting for the model, needs an experienced person and half an hour of context they have to go and get.

If you sequence by difficulty you will do risk analysis in month two and hit your ceiling immediately, on the thing that generates the most impressive demo.

The practical instruction:

> Take your roadmap. Add a column. What does it cost us to check one of these. Re-sort on that column. That is a one-hour exercise and it will change the order.

---

## 13. The contract

**An agent is a role, not a tool. Roles have contracts. Four fields.**

Start with why four rather than what the four are, because the number is the interesting design decision.

A contract gets read twice. Once at approval, when everyone is calm and has time and a fifteen-field document looks thorough. And once at six on a Friday when the thing is misbehaving and somebody has to decide in five minutes whether to pull it.

> The second reading is the one that matters, and a fifteen-field contract fails it.

Then the four, one line each. Scope: what it may decide, named individually, and anything not named is out. Evidence: what it must produce every time. Escalation: the named conditions where it stops, and the named role it stops to. Revocation: how you turn it off.

Two rules to say out loud because they do the real work:

If the agent cannot produce the required evidence, it does not make the decision. It escalates. There is no configuration where that becomes acceptable.

Revocation has to be one named person, no meeting, and you have to have tested it. Untested revocation is not revocation. Everything else in the contract is decoration if you cannot turn it off.

---

## 14. The people

**Two new roles. Neither is a data scientist.**

Walk the before and after quickly. Project manager goes from coordinator to verifier. Analyst goes from producing reports to owning the evidence layer. Lead goes from owning process to owning decision rights.

Then the two new ones, and this is the part worth dwelling on.

Agent steward: owns the contracts, tracks reversals, retires agents that stop earning their place.

Verification lead: owns the budget and allocates review capacity.

Then the observation:

> Both are accountability roles rather than technical ones, which is exactly why they get skipped. It is easier to fund a tool than to name a person who is answerable.

If you take one staffing decision away from this talk, it is naming a verification lead. It does not need to be a new hire. It needs to be somebody's actual job.

---

## 15. Blast radius

**Class tells you what checking costs. Blast radius tells you who is allowed to decide. You need both.**

Class alone is not enough, and here is the case that proves it: a schedule arithmetic correction is Class A whether it moves an internal date or triggers a contractual milestone payment. Same checking cost. Very different decision.

So authority runs on a second axis, five levels, from the agent acting and logging it, up to a human deciding with the agent only supporting.

Walk the ladder briefly. The test in each row is about reversibility and who is affected, not about the work.

Then the point of the slide, and this usually gets people writing:

> Look at what is absent from that table. Model confidence appears nowhere, at any level.

Explain why, because it is counterintuitive. A confidence score is a useful thing to show a reviewer, because it tells them where to look. It is a terrible thing to gate authority on, because confident and wrong on an irreversible decision is still a disaster. Confidence belongs in the evidence, not in the permission.

---

## 16. The evidence plane

**Six fields, and they exist to make the next review fast, not to reconstruct the past.**

Open with the distinction, because it is the whole design:

> An audit log is written so somebody can reconstruct what happened six months later. This is written so somebody can judge it in ninety seconds. Different jobs. Most teams only build the first one.

Then the six, fast, and for each one say what it saves rather than what it is.

The claim, one sentence, so the reviewer knows what they are approving before they start.

The sources, with links, not descriptions. And stop on this one:

Ask them where the time actually goes in a review. It is not the judging. It is the reviewer going and finding the same four things the agent already had open. That is forty to sixty percent of the cost, and this one field deletes it.

The counter-case: the strongest reason this could be wrong, written by the agent. This changes what the reviewer does. Without it they read the whole thing evenly looking for anything. With it they go looking for one named thing.

Blast radius and the reversal path, together, because they answer the same question twice: what breaks if this is wrong, and how do I get out of it. That pair is what lets a reviewer honestly decide to look less hard at something cheap and reversible.

The owner, resolved to a person, not a role. An escalation to "the PMO" is an escalation to nobody.

Then the enforcement line:

> An artifact missing any of the six is not a decision. It is an output. Outputs do not get actioned.

That is a schema check in your pipeline, not a paragraph in a policy document.

---

## 17. Reference shape

**Sources, agents, evidence, verification. The direction matters more than the boxes.**

Do not narrate the diagram. Point at the one property that matters.

> Nothing writes back to the source systems until it has cleared verification. The write path is the governance boundary.

That single constraint does more than any policy you can write, because it is structural. An agent that cannot write until something has checked it cannot quietly accumulate unverified changes in your systems of record.

If people take a photo of one architecture slide, this is a reasonable one to take.

---

## 18. Agentic verification

**Agents can supply verification capacity, not just consume it. This is how you get autonomous.**

This is the slide that answers "so how do I actually scale this", and it is the most forward-looking thing in the talk. Give it room.

Put a second agent in front of the human. It closes some decisions on its own, either passing them or rejecting them with a machine-checkable reason, and only the rest reach a person. The share it closes is containment. As containment goes up, your budget goes up, with no new hires.

Then the three rules, and be firm, because this is where it goes wrong in practice:

One. The verifier's own output has to be machine-checkable. If a human has to read a paragraph of reasoning to decide whether to trust the verifier, you moved the cost, you did not remove it.

Two. It only counts if you have measured how often it passes bad decisions. An unmeasured verifier is a cost reduction on paper and a risk transfer in fact. Uncalibrated means it counts as zero.

Three. Use the bottom of the confidence interval in your budget, not the average. You are sizing a safety margin.

Then the honest bit, which is the thing nobody tells you:

> A verifier closes the easy decisions first. So the queue that reaches your humans is harder than the average was, and your cost per check goes up as containment goes up.

Which means you have to re-measure. A budget that assumes checking cost stayed flat while containment climbed will overstate your capacity at exactly the wrong moment.

---

## 19. Six numbers

**Six metrics. Per class, per week. Never averaged across classes.**

Name them, do not explain them. Budget, overdraft, silent drift, containment, escalation precision, reversal latency.

The one instruction that matters:

> Report them per class. In the worked example the portfolio average is about 0.2 and looks healthy. The number that matters is 3.3 and it is in one class. Average them and you see nothing.

---

## 20. Measuring drift

**The share of decisions approved faster than an honest review could have happened.**

Explain how to build the floor, because this is the only metric here that people cannot look up.

Watch a set of reviews where you know people genuinely checked. Take the tenth percentile of those times. Also work out the physical reading time for a typical artifact. Take whichever is larger. That is your floor, per class, from your own data.

Anything approved faster than that did not get reviewed. Count it, and put it on the same page as the good news.

Two things to say before somebody objects, because both objections are correct:

The floor is built to flag about one in ten even when everything is fine, so the signal is the amount above ten percent, not the raw number.

And the rule that keeps this alive:

> Never use it on an individual. The moment you do, people leave artifacts open, the number goes to zero, and you have destroyed the only instrument that sees this failure.

Report it by class. Not by person. If your organisation cannot resist using it against individuals, do not collect it, because a corrupted metric is worse than a missing one.

---

## 21. The dashboard

**Every headline number improved while supervision quietly stopped existing.**

This is the sharpest slide in the deck. Let it do the work.

Read the four numbers on the left as if they were good news, because in any other quarter they would be. Approval rate up. Reversals low. Cycle time down forty-one percent. Escalations steady.

Then:

> Approval rate went up because approving got easier. Cycle time went down because checking stopped. Every one of these is measuring throughput and calling it health.

`[ASK]` In the chat: which of these four does your current AI reporting include?

`[ROLLBACK]` If the chat stays quiet: "I will answer it for you. Most reporting has three of the four, and none of them has the fifth one on the right. That is not a criticism, it is just what happens when the metrics were designed before the agents arrived."

Close the slide on the lag, because it is the practically useful part:

The overdraft was there from week one. The drift took six weeks to become visible, because the backlog absorbed it first. So the period where this is cheap to fix is the period where nothing looks wrong.

---

## 22. Four gates

**Four gates before an agent goes live. Each has a number, or it is a meeting.**

Go through them fast, one line each, and land on the third.

Gate one, classification and cost. Two qualified people classify fifty decisions separately, and you measure what checking actually costs with a stopwatch. If they disagree, you do not know what class it is, so you do not know your capacity.

Gate two, evidence. Every artifact carries all six fields, and a human spot-checks twenty for whether the fields are real rather than filled in.

Gate three, adversarial. Feed it the cases from your own lessons-learned register. The ones that already went wrong. Then inject conditions that must trigger a handoff and check that every one of them fires.

> Confident and wrong on a case you already know is hard is disqualifying. Not a low score. Disqualifying.

Gate four, replay. Run it against closed decisions where you know the outcome, with the agent blind to anything after the decision date.

Then the note on which one gets skipped:

The cost measurement in gate one is the one that gets dropped, because it is the least interesting and it needs three people with a stopwatch. It is also the only one that tells you how far you can scale. Without that number every other figure in this talk is unavailable to you.

---

## 23. Part 3 divider

**Five minutes. Where you are, what I do not know, and what to do on Monday.**

---

## 24. S0 to S4

**Five stages, and one question tells you which one you are on.**

Name the stages quickly. Unmeasured, measured, bounded, contained, self-budgeting.

Then the question, and ask it directly of the audience rather than describing it:

> What does it cost you to check one expert decision, and when did you last measure it?

No number and no date means you are at stage zero, whatever your governance documentation says. That is most organisations and it is not a criticism, because until recently there was no reason to have measured it.

Then handle the obvious question before it comes:

There is no stage five. Stage five would be a system that also sets its own risk appetite and audits its own drift, which means no human in the loop. That is not more mature. A system with no human verifier does not have an infinite verification budget, it has none, because there is nobody whose approval means anything from outside the system making the claim.

Stage four is the ceiling by construction. And at stage four the human job is small: set the thresholds, set the risk appetite, approve the reclassifications. That job does not shrink further, because it is the job that makes every other number mean something.

---

## 25. What I do not know

**Four holes, said out loud.**

Go quickly. This slide buys you more credibility than anything else in the deck, so do not undersell it by rushing past it apologetically.

The measurement is biased, because people check more carefully when they are watched, so the budget always looks better than it is.

Bursts are not modelled. The budget is a rate and work does not arrive evenly. You can be fine on average and still drop reviews in board week. This is the biggest hole and it is the one I would most like help with.

Timing is a proxy for checking, not checking itself. Somebody who already knows the answer can approve correctly in twenty seconds.

And there is no empirical validation. The numbers are synthetic and they are labelled as synthetic everywhere they appear.

> If you have measured any of this in a real organisation, that is the contribution I want. There is an issue template for exactly it.

---

## 26. What this buys you

**This is a permission structure, not a brake. It tells you where you can go faster.**

Reframe here, deliberately, because the previous twenty-five slides have been about a constraint and people will have heard it as caution.

Four things you get.

More autonomy, not less. In the worked example, machine-checkable work runs at three thousand decisions a week and expert-checkable work runs at twenty-one. Same people, same models, same budget. If you pick the first kind of work you are not throttled at all. The framework does not slow you down, it tells you which lane is open.

A number you can defend. When your board asks how much AI you can safely run, you have arithmetic and you can show exactly what would have to change to raise it. That conversation goes very differently when you have a number.

Capacity that grows without hiring. A calibrated verifier cuts the cost of checking, and the budget rises on the same headcount.

Failures you find early. Drift shows up as a rising number weeks before it shows up as an incident, while every other dashboard is still green.

Then the close of the argument:

> The teams that scale autonomy fastest are not the ones with the best models. They are the ones who made checking cheap.

---

## 27. Monday

**Four things, all doable this week, none needing a budget.**

Say them as instructions, not options.

One. Pick one decision type your agents already make. Time three people checking twenty of them. You now have your first real number and you are out of stage zero.

Two. Work out your budget for that one class. Four inputs, two minutes in the calculator.

Three. Compare it against how many of those decisions you actually produce. Under one and you have headroom, so deploy more, and that is a genuinely good week. Over one and you now know something you did not know on Friday.

Four. Add the ratio to whatever you already report on AI. One row. Next to the approval rate.

`[ASK]` If you are going to do the first one this week, put a plus one in the chat.

`[ROLLBACK]` If the chat is quiet: "Do not put it in the chat then, put it in your calendar. It is a two-hour job and it is the only one of the four that makes the other three possible."

---

## 28. Take it and use it

**Everything is public and free. Take it, rename it, put it in your own framework.**

Three QR codes. Repository, calculator, and the ways to reach you.

Apache 2.0, which means you can take it into your own governance framework and rename it if that helps it get adopted. Adoption is the point, not attribution.

What you want back: measured verification costs from real organisations, classification disagreements where the decision tree gives the wrong answer, and anything at all on the queueing problem.

`[HOST]` Thank the audience and the host. Hand back to the moderator for questions.

Leave the slide up for the whole Q&A. It is the only slide with the links on it.

---

# Reserve blocks

About six minutes total. Use if you reach slide 22 early.

## R1. Why fluent output is harder to check, 90 seconds

Insert after slide 4.

The old failure mode was obviously bad work. A draft with a hole in it, and you spot the hole in four minutes because the writing signals the quality.

Fluent output breaks that signal. The artifact reads like something a competent senior person wrote, so your prior is that it is fine, and you have to do actual work to establish otherwise. The cost of the check went up and nothing about the underlying decision changed.

This is why "the model got better" does not help your review capacity. In this specific way it hurts.

## R2. The Class B trap, 90 seconds

Insert after slide 8.

The most common classification mistake is calling something Class B when it is not.

A batch of two hundred status narratives. Homogeneous, one rubric, high volume. Textbook Class B. Check twenty, conclude about the rest.

Except three of the two hundred go to the board, and a sample of twenty will miss all three.

Class B needs one more condition than people remember: no member of the population can be much more consequential than the others. When that fails you do not average over it, you split it. Thirty-seven projects are Class B and three are Class C, and the three get checked properly.

That failure is invisible until the board sees the wrong number.

## R3. What to do when you are already over budget, 2 minutes

Insert after slide 21.

Somebody will be sitting there having worked out they are at three times capacity, wondering what they are supposed to do on Monday other than panic.

Four options and only two of them work.

Hire more qualified reviewers. Slow, and qualification is the bottleneck rather than recruitment.

Protect review hours. Real, and it is the cheapest gain most people have available, but it is bounded. You cannot get above about 0.7.

Make checking cheaper. This is the one with orders of magnitude in it. Evidence plane, better inputs, a calibrated verifier.

Ask for fewer decisions. Batch them, set standing policy, or stop asking. Underrated, and usually the fastest thing available this week.

> No single lever closes a gap of three times. In the worked example it takes cutting the cost of checking by half and reclassifying about forty-five percent of the work. Both at once.

The two that do the work are making checking cheaper and asking for less. Neither of them is hiring.

## R4. Why the classes are not a risk register, 60 seconds

Insert after slide 15.

The objection to expect: this is just a risk framework with different labels.

It is not, and the difference is testable. Reconciling a forty million budget rollup against the ledger is high risk and machine-checkable in nine seconds. Deciding whether to renegotiate a minor dependency with a partner team is low risk and needs somebody who remembers what happened in March.

Risk and checking cost are not correlated. A pure risk framework tells you to be careful with the first one and relaxed about the second, which is exactly backwards for deciding where to deploy an agent.

You need both axes. Most operating models have one.

---

# Questions to expect

**"How do we measure c without instrumenting everything?"**
Three people, twenty decisions, a stopwatch, one afternoon. The instrumentation is better for the long run and it is not needed to start. The step people skip is the last one: ask each reviewer afterwards whether they genuinely checked and throw away the ones who say no. Without that you measured approval time, not verification cost, and under overdraft those are different quantities.

**"Isn't this just a reason to slow down?"**
The opposite, and slide 26 is the answer. It tells you where you can go faster. Machine-checkable work at three thousand a week against expert work at twenty-one is not a brake, it is a map. Most organisations are being cautious uniformly, which means being too slow on the cheap work and too fast on the expensive work.

**"What if the AI gets good enough that it does not need checking?"**
Then you are trusting it without evidence, which is a decision you can make but should make explicitly. The framework does not say agents are unreliable. It says an approval that nobody had capacity to make is not an approval. If you want to run without verification, run without it deliberately and write down that you did.

**"We already have AI governance. How is this different?"**
Most governance says who may approve what. This says how many approvals you can actually produce. Those are different questions and the second one is usually missing. You can have complete governance documentation and be structurally unable to execute it, and that is the normal case rather than the exception.

**"Where did the 3.3 come from?"**
A synthetic example, generated by a seeded script in the repository, and it is labelled synthetic everywhere it appears. It demonstrates that the arithmetic reproduces. It is not evidence about any real organisation and I would not defend it as such.

**"Does this work outside project delivery?"**
The arithmetic does. Anywhere agents produce decisions and humans approve them. What does not transfer is the calibration: the cost ranges are project-delivery numbers and you should throw them away and measure your own.

**"Who owns this in the org chart?"**
The verification lead from slide 14. It does not have to be a new hire and it usually should not be. It has to be somebody's actual, named job, because a budget nobody owns is a number in a slide deck.
