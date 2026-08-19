# Speaking script

For the 27-slide deck. Roughly 35 minutes at a normal pace. Shorter cuts are listed below the running order.

> **For the GSDC session, use [`SCRIPT-45MIN.md`](SCRIPT-45MIN.md) as the running order.**
> 45 minutes of talk plus 15 of questions, inside the 60 to 70 minute slot. It holds
> the timing table, two polls, two live demos, the questions to expect, and seventeen
> minutes of reserve material if you finish early. This file is the spine: what you
> say on each slide. That file is the plan.

**How to use this.** The script does not read out the slides. The audience can read, and a speaker who narrates their own bullet points is competing with the room instead of leading it. Every line below is something that is *not* on the screen: the reason behind a claim, the sentence that lands it, the thing to say while people are still reading.

Slide content is referred to by a short cue in **bold**, so you can find your place at a glance.

Lines in *[brackets and italics]* are stage directions, not words to say.

---

## Running order and timing

| # | Cue | Minutes | Running |
|---|---|---|---|
| 1 | Title | 1:00 | 1:00 |
| 2 | Part 1 divider | 0:20 | 1:20 |
| 3 | Thirty years | 1:15 | 2:35 |
| 4 | What did not move | 1:30 | 4:05 |
| 5 | Nobody decides to | 2:00 | 6:05 |
| 6 | The formula | 1:45 | 7:50 |
| 7 | Six people, twenty-one | 2:00 | 9:50 |
| 8 | Four classes | 2:00 | 11:50 |
| 9 | The quadrant | 1:30 | 13:20 |
| 10 | Part 2 divider | 0:30 | 13:50 |
| 11 | Five layers | 1:00 | 14:50 |
| 12 | Layer 1, deployment order | 1:30 | 16:20 |
| 13 | Layer 2, four fields | 1:15 | 17:35 |
| 14 | Layer 2, the people | 1:30 | 19:05 |
| 15 | Layer 3, blast radius | 2:00 | 21:05 |
| 16 | Layer 4, six fields | 1:15 | 22:20 |
| 17 | Layer 4, reference shape | 1:30 | 23:50 |
| 18 | Layer 4, agents supplying capacity | 2:00 | 25:50 |
| 19 | Layer 5, six numbers | 0:45 | 26:35 |
| 20 | Layer 5, measuring drift | 1:30 | 28:05 |
| 21 | Layer 5, the dashboard | 1:45 | 29:50 |
| 22 | Four gates | 1:00 | 30:50 |
| 23 | Part 3 divider | 0:20 | 31:10 |
| 24 | S0 to S4 | 1:30 | 32:40 |
| 25 | What I do not know | 1:00 | 33:40 |
| 26 | Monday | 1:00 | 34:40 |
| 27 | Take it and use it | until questions end | |

**Thirty-five minutes at a normal pace.** That fits a 45-minute slot with time for
questions. Two shorter cuts, both tested against the argument rather than against
the clock:

**25 minutes.** Drop 12, 17 and 22. You lose the sequencing rule, the
architecture and the gates. The argument survives because Part 1 carries it and
Part 2 still has roles, authority and metrics.

**15 minutes.** Keep 1, 3, 5, 6, 7, 8, 15, 21, 26, 27. That is the constraint,
the number, the classes, the authority ladder, the dashboard contrast and the
ask. It is a different talk, a sharper one, and it works.

If you are running long mid-talk, cut 22 first. It is the most reference-like
part and the least dependent on you being in the room.

---

## 1. Title
*[Get the closing slide URL up on a second screen if you have one. Otherwise mention early that everything is free and online, so people stop photographing and start listening.]*

Good morning. My name is Hotragn.

Before I start, three things this talk is not, so nobody is waiting for them. It is not a prediction about what AI will do next. It is not a product, and there is nothing to buy at the end. And it is not a maturity model you have to adopt whole.

It is one number, and what follows from it once you have it.

Everything is on GitHub under Apache 2.0. The formula, the schemas, a calculator, and the code that produces every figure I am about to show you. The last slide has a QR code, so please do not spend the next twenty minutes photographing my slides.

One more thing. I am going to be quite blunt in the middle of this talk about a failure mode that is probably happening in your organisation right now. It is not anyone's fault, and I will explain why.

---

---

## 2. Part 1 divider
*[Two beats, no more. This is a signpost, not a slide.]*

Three parts. Why the constraint moved. What the operating model looks like once
you accept it. And what you can do about it on Monday.

The first part is an argument, so push back on it while I am making it. The
second part is a design, and it is the half most of you came for.

---

---

## 3. Thirty years
Quick show of hands. Who has an AI tool in their delivery organisation right now that writes something a person used to spend an afternoon on?

*[Wait. Let the hands stay up for a beat.]*

Keep them up for a second and look around.

Right. Now here is my question, and I genuinely want you to think about your own answer rather than mine.

Every one of you measured that. You measured hours saved, or throughput, or cycle time on the thing being produced. That is the natural thing to measure and it is the right thing to measure.

**Thirty years** was the reason it was the right thing to measure. For as long as any of us have been doing this, the bottleneck was getting the work made. So capacity planning meant counting the people who could make it.

Nobody measured what happened on the other side.

---

---

## 4. What did not move
*[Point at the right-hand column and stay there. This is the whole slide.]*

Three things on the right. Not one of them improved when the models improved.

The number of people qualified to judge a schedule re-baseline is the same as it was. The hours those people have is the same. And the time it takes to properly check one is the same.

Actually, two of them got worse.

The first is obvious once you say it: the queue drains at the same speed and now more arrives.

The second is not obvious and it is the more interesting one. The output got fluent. When a junior wrote you a rough impact assessment, you knew where to look, because the rough bits were where the thinking was thin. A confident, well-structured, well-written, wrong document gives you nothing to snag on. Fluency is a real cost and nobody put it on the balance sheet.

---

---

## 5. Nobody decides to
*[Slow down here. This is the centre of the talk. Do not rush and do not fill the pauses.]*

So what actually happens when more arrives than can be checked?

The work does not stop. There is no queue that fills up and turns red. The work carries on, and somebody approves it.

**Eleven minutes.** Nineteen items. Nineteen approvals.

I want to be very precise about who is at fault here, because this is where these talks usually go wrong.

Nobody in that story did anything wrong. The reviewer is behaving completely rationally. They have been handed a queue and a calendar that cannot both be true, and they are doing the only thing available to them. If you swapped that person for a better person, you would get the same nineteen approvals.

*[Pause.]*

And here is the part that keeps me up. Every one of those nineteen is recorded as a review. The audit trail is perfect. The names are on it, the timestamps are on it, the workflow shows green.

**Silent drift** is the name for the gap. Silent because the system records it as a success.

Rubber-stamping is not a behaviour you can train out of people. It is what running out of review capacity looks like from the inside.

*[Pause. Then change tone completely for the next slide.]*

---

---

## 6. The formula
So let us put a number on it, because I think this is a capacity problem wearing a culture problem's clothing, and capacity problems have arithmetic.

**The formula.** It is a division. That is genuinely all it is, and I am not going to derive it.

Three of these you can get from a spreadsheet this afternoon.

The one worth being careful about is the first. It is not everyone who has the approve button. It is the people whose signature you would stand behind if this went wrong and somebody asked. In every organisation I have discussed this with, asking that question honestly cuts the number roughly in half. That is usually the first uncomfortable moment, and it is worth sitting in.

The fourth one, the cost of checking, is the one nobody has. Hold that thought, because I am coming back to it and it turns out to be the whole talk.

---

---

## 7. Six people, twenty-one
Let me make it concrete.

**Twenty-one.** Six people, eight hours each on paper, of which just over half survives contact with the calendar, and an honest check on a schedule re-baseline takes about an hour and a quarter. Twenty-six hours of real capacity, so twenty-one decisions.

Twenty-one a week. That is a real organisation's real capacity for that one decision type.

Now the agents produce seventy.

*[Let it sit for a second.]*

The number I want you to take away is not the ratio. It is **forty-nine**.

Forty-nine times a week, somebody signs their name to something they did not have the capacity to check. Not once. Not on a bad week. Forty-nine, every week, structurally, by arithmetic.

And I will say it again because it matters: nobody in that team is doing anything wrong.

These figures are illustrative, by the way. They are in the repository and the repository says on the same page that they are synthetic. I will come back to that.

---

---

## 8. Four classes
So what do you do. You cannot hire twenty more qualified people and I am not going to pretend you can.

The first move is to stop treating all decisions as one pile.

**Four classes.** And the thing that sorts them is not what you expect, so let me be direct about it.

You already classify by risk. Everybody does. And risk is the right question for whether you *must* check something. It is the wrong question for what checking *costs*, and those are genuinely different axes.

Two examples so this is not abstract.

Reconciling a forty million pound budget rollup against the ledger. Very high risk. A machine does it in nine seconds and tells you the answer.

Whether to renegotiate a minor dependency with a partner team. Low risk, nobody would put it on a board pack. And to check it properly you need somebody who remembers what was agreed in March, why that dependency exists, and how that particular relationship works.

High risk, cheap to check. Low risk, expensive to check. If you only have the risk axis, you cannot see that.

*[On Class D, if there is a visible reaction:]*

Class D is the one people push on, so let me get ahead of it. It is not that these decisions are too important for a machine. It is that they have no finite cost of checking, so there is no quantity of them you can afford. That is arithmetic, not caution. Agents can prepare them, and that is where most of the value is anyway.

---

---

## 9. The quadrant
Which leads to the thing I would most like you to leave with, if you leave with one thing.

**The quadrant.** Top right. Let me name three things that live there.

Portfolio prioritisation. Vendor dispute strategy. Strategic dependency renegotiation.

Now, the awkward part. The models are genuinely good at all three. That is not the problem. I am not standing here telling you the technology is not ready.

The problem is that your review capacity for those decisions is a couple of dozen a week. Which means your deployment is capped at a couple of dozen a week, no matter how good the model gets, forever, until you change something other than the model.

Every impressive demo you have seen this year lives in that box. It looks best in a demo precisely because it is hard, and hard is where the model looks most impressive.

You do not fix that box by deploying harder. You fix it by moving work to the left, and moving left means making the decision genuinely cheaper to check. Which is engineering work, not a renaming exercise.

I want to be clear that this is not a rule against ambition. It is a sequencing rule. Reclassify, then deploy.

---

---

## 10. Part 2 divider
*[Mark this clearly. Half the room has been waiting for it.]*

That was the argument. This is the design.

Five layers. None of them is a new department, and none of them needs a data
scientist. Four of the five are things you already have, redesigned around a
constraint you did not previously have a number for.

You have about twelve minutes of this, so nobody should get comfortable.

---

---

## 11. Five layers
*[Do not read the table. Give the shape and move.]*

The reason I am showing you the whole thing before any of the parts is that each
layer only makes sense as an answer to a question, and the questions are what
you will actually take back.

Layer three will be new to most people here. Layer five will be uncomfortable.
Everything else you already do, just sorted by a different axis.

---

---

## 12. Layer 1, deployment order
This is the quadrant from Part 1, turned from a warning into a sequencing rule.

Here is the sentence that makes it real, and it is the one I would like you to
argue with over coffee.

*[Slowly:]* Risk analysis is the easier AI problem. It should go live later than
status reporting.

That inverts what is on almost every roadmap in this room. And it inverts it for
a reason you can check rather than a reason you have to believe. Status reporting
can be checked against the source systems in minutes. A risk analysis needs
somebody who knows the programme, and there are four of those people.

*[Expect the objection that risk analysis is more valuable. Take it seriously:]*

Yes, and value is not the axis. Value tells you what you want. Verification cost
tells you what you can actually run. You need both numbers and most roadmaps only
have the first.

---

---

## 13. Layer 2, four fields
Two quick reference slides, then back to the interesting part.

**Four fields.** Every agent gets a contract with these four, and the number four is doing real work.

A contract gets read twice. Once at approval, when everyone is calm and has time and a fifteen-field document looks thorough. And once at six on a Friday when the thing is misbehaving and somebody has to decide in five minutes whether to pull it.

Only the second reading matters, and that is the one a fifteen-field contract fails.

*[Then the question that always lands:]*

Let me ask you the fourth one directly. Who here could switch off your AI tooling this afternoon, on your own authority, without booking a meeting?

*[Wait. It usually goes quiet.]*

That is the field people leave out.

---

---

## 14. Layer 2, the people
*[This is the slide people photograph. Leave it up longer than feels comfortable.]*

Three jobs invert and two jobs appear.

The inversion is the part that will land in the room. The project manager stops
chasing and starts checking. That is a genuine change to somebody's working week
and I would rather say it plainly than dress it up as an opportunity.

The two new roles are the point, so let me say why they never get created.
Neither of them is technical, so no budget line obviously owns them. And both of
them are accountability rather than delivery, so nobody volunteers.

*[If asked whether these are full-time, and somebody always does:]*

At forty projects, the verification lead is about a day a week and the agent
steward about two. They are not headcount. They are named responsibility. But
they do have to be named, because a budget nobody owns is a budget nobody
defends when somebody senior wants to ship.

---

---

## 15. Layer 3, blast radius
The ladder itself is easy to follow, so I want to spend the time on what is
missing from it.

Almost every AI governance framework any of you have seen gates on confidence.
High confidence, more autonomy. It is intuitive and it is backwards.

Confidence is the agent's opinion of its own work. It is exactly as trustworthy
as the thing you were trying to check in the first place. Blast radius is a
property of the decision, not of the agent, and you know it before the agent
runs.

*[If somebody asks how this relates to the four classes:]*

Different axes, and you need both. Class tells you what checking costs, so it
sizes the budget. Blast radius tells you what happens if you are wrong, so it
sets the authority. A decision can be cheap to check and catastrophic to get
wrong.

The practical note: you can build this table in an afternoon. Most organisations
already have a delegated authority matrix for spend. This is the same idea
pointed at reversibility instead of money.

---

---

## 16. Layer 4, six fields
**Six fields.** These travel with every decision.

The single most useful thing I can tell you about this list is what it is not. It is not an audit trail.

An audit trail is built for somebody reconstructing what happened, months later, who was not there. This is built for somebody deciding right now, this afternoon, with eleven other things in their queue. Those two goals produce genuinely different documents, and only one of them changes your capacity.

Ask any reviewer where the time goes on a hard review. It is almost never the judgement. It is finding the inputs again. That is typically half the clock, and half of it is the agent already having had those inputs and not telling you.

*[If time allows, the mechanism behind field three:]*

The third one has a subtle effect worth thirty seconds. Without it, the reviewer's question is "is this right", and that question has no natural end: they have to generate the options themselves and then check each one. With it, the question becomes "is one of these rejection reasons wrong", and that is a list you can get to the bottom of. One honest alternative beats four decorative ones.

---

---

## 17. Layer 4, reference shape
*[Trace it left to right with your hand once, then stop and talk about the line at
the bottom. That line is the slide.]*

Most teams put the governance boundary at the model. What may it see, what may it
be asked, which prompts are allowed. That is the wrong boundary, because reading
is not where the risk lives.

The boundary belongs on the write path. An agent that reads everything and writes
nothing until a check has cleared is a safe agent, whatever else it is doing.

Which gives you a test anybody in your organisation can apply to any proposed
integration, without understanding a single thing about models. Ask: can this
agent write to a source system without a verification step in between? If the
answer is yes, the boundary is in the wrong place, and no amount of prompt
engineering moves it.

Notice the analysts are marked propose only. That is Class C from Part 1 showing
up in the architecture rather than in a policy document nobody reads.

---

---

## 18. Layer 4, agents supplying capacity
Now the part that I think is actually new, and the part I am least certain about, so I am going to give you the caveats first.

**The second formula.** An agent checking another agent. It closes some of the work, the humans see the rest, capacity goes up without hiring.

If I stopped there, you would be right to be suspicious. So, three rules.

One. The checker's own output has to be machine-checkable. If a human has to read its reasoning to decide whether to trust it, you have not removed the cost, you have moved it one step to the left and made it somebody else's problem.

Two, and this is the one that matters. Somebody has to have measured how often that checker waves through a decision that was actually bad. Not how often it agrees with humans. How often it misses. If nobody has measured that, the number you put in the formula is zero. Not a guess, not a conservative estimate. Zero.

Three. Use the bottom of the confidence range, never the headline number. You are sizing a safety margin, not writing a press release.

*[If the room is technical, add:]*

There is a sting in this and it is in the repository as a known limitation. The checker closes the easy ones first. So the queue that reaches your human gets harder over time, which means your cost of checking goes up as your containment goes up. The framework does not have a clean correction for that. The honest guidance is to re-measure after every change, and I would rather tell you that than pretend.

---

---

## 19. Layer 5, six numbers
**Six numbers.** I am not going to read these.

One thing only. Never average them across your portfolio. Your healthy classes will cover your failing one and the board will see a green light. In the example in the repository the portfolio figure is about 0.2, which looks excellent, and one class inside it is at 3.3.

The third row is the one that matters, and it gets its own slide.

---

---

## 20. Layer 5, measuring drift
How do you measure whether an approval was real. It sounds impossible. It is not, but it is delicate.

**The floor.** The idea is a line below which a review could not physically have happened. Not a target, not a standard. A physical impossibility line.

You get it by watching about thirty real reviews and asking each person afterwards whether they genuinely checked. Then you take a low percentile, not the average, because you are not trying to catch fast reviewers. Fast reviewers are good. You are trying to catch reviews that could not have occurred.

Then the reading rule on the right, which is the part that catches people out. A tenth-percentile line reports about ten percent even when everything is fine. That is arithmetic, not a problem. So the number you watch is the excess above that, not the number itself.

*[Now the important part. Slow down.]*

And one rule, which I will say twice.

Never point this at an individual. Never.

The moment you do, review time becomes a thing people manage rather than a thing you measure. People leave documents open. The numbers rise. Your drift rate goes to zero and stays there, and you have lost the only instrument that can see this failure.

If your organisation cannot resist doing that, then do not collect it at all. A corrupted metric is worse than a missing one, because a missing metric does not tell you everything is fine.

*[Optional, if you have the time:]*

One pattern from the example data. The overdraft is constant from week one. The drift does not show up for about six weeks, because the backlog absorbs it first. Which is exactly why people look at an overdraft, see nothing bad happen, and conclude it was harmless. It was not harmless. It was queued.

---

---

## 21. Layer 5, the dashboard
*[Slow down. This is the most useful slide in Part 2.]*

Every one of those four numbers is a metric a real PMO reports today. Not one of
them can see the failure.

It is worse than that. Three of them move in the direction that looks like
success while the failure gets worse. Approvals rise, because approving got
faster. Cycle time falls, for the same reason.

And the cruellest one is the reversal rate. It falls, and on a board pack that
reads as quality improving. It is falling because detection stopped.

*[Pause.]*

So here is the instruction, and it is a governance decision rather than a
technical one. Put drift on the same page as those four numbers. Not in an
appendix. Not on a separate dashboard that somebody opens quarterly. On the same
page, so that a board has to look at both in one glance.

On its own page nobody looks at it, and four green numbers win every time.

These figures are illustrative. Say so.

---

---

## 22. Four gates
**Four gates.** Two before it runs, two while it runs, every one with a number attached.

A gate without a number attached to it is a meeting.

*[Usually gets a laugh. Let it, then:]*

I am being slightly flippant but the point is serious. Every threshold on this slide is in the repository, and so is the code that checks it, so this is not a slide of good intentions.

The first one fails more often than teams expect. Two qualified people classify fifty decisions separately and do not agree. That feels like a bad day, and it is actually the most useful thing the gate produces, because if you cannot agree what class something is, you do not know what checking it costs, and every number downstream of that is decoration.

*[If time, the criterion people find strange:]*

There is one criterion in the replay gate that people argue with, and I will defend it. If the agent disagrees with your history and turns out to be right, it still fails, unless a reviewer could have adjudicated that disagreement inside the budgeted time. A right answer nobody can check is not a usable answer. That is the whole talk in one rule.

---

---

## 23. Part 3 divider
Right. That was the design. This is what to do about it.

Where you are, what I have got wrong, and the smallest useful thing you can do on
Monday.

About six minutes, then questions.

---

---

## 24. S0 to S4
**Five stages.** I am not going to walk you through these, because you will place yourself more honestly if I do not.

Instead, one question. Answer it privately.

What does it cost you, in hours, to check one expert decision? And when did you last measure it?

*[Pause and let it land.]*

If there is no number and no date, you are at the far left. Most organisations that would describe themselves as being in the middle are at the far left with better paperwork, and I include people I respect a great deal in that.

The hard step is the second one, and it is not technical at all. It is being willing to say no to a deployment that is over budget, when the deployment is popular and somebody senior wants it.

*[Then the ending of this slide, which people remember:]*

You will notice it stops at five and there is a cross where a sixth would be. Let me tell you why, because someone always asks.

A sixth stage would be a system that also sets its own risk appetite and audits its own drift. No human in the loop at all.

That is not a further stage of maturity. It is the removal of the thing this whole model exists to manage. There is no verification budget without a verifier whose approval means something outside the system making the claim.

Such a system might well be right. It just could not be *known* to be right by the people running it. And an organisation that cannot know is not governing. It is hoping.

---

---

## 25. What I do not know
*[Deliver this flat and quickly. Do not apologise your way through it. It buys more credibility than anything else in the talk.]*

Before I finish, the parts I have got wrong or have not solved.

*[Run down them briskly. Then stop on the second one:]*

The second one is a real gap and I would like help with it. The budget is a rate. Work does not arrive at a steady rate, it arrives in lumps around gates and board dates. So you can be comfortably under budget across a quarter and still drop reviews in the week the board pack is due. The correct treatment is a queueing model and I am not the right person to build one. If you know queueing theory, please find me afterwards.

And the last one. Every figure I have shown you today is illustrative. There is no field data on the cost of checking, anywhere, that I have been able to find. The repository says so on the same page it prints the numbers, and if you screenshot one of my figures I would ask you to screenshot that caveat with it.

Which is why the thing I want most is on the next slide.

---

---

## 26. Monday
So, four things, and they are deliberately small.

**Monday.** Not a programme. Not a policy. One person, one afternoon, no permission needed.

The second one is the one that gets skipped, and it is the one that makes the whole number mean anything. When you ask people afterwards whether they genuinely checked, some of them will say no. Throw those away. Without that question you are measuring how long approvals take, and under an overdraft that is a completely different quantity from how long checking takes.

And then just show one person the gap. Not a deck. One number and one conversation.

If it comes back under one, good, you have headroom and you should deploy more aggressively than you are.

If it comes back over, you now know something you did not know on Friday. And knowing it is genuinely the whole of the first stage.

---

---

## 27. Take it and use it
*[Get this up early and leave it up through the whole question session.]*

That is everything. It is all here.

Three things I would like, in order of how much I want them.

First and by a distance: if you measure your cost of checking, send it to me. Anonymised is completely fine, round the numbers if you need to. There is an issue template for it. One measured number from a real organisation is worth more to me than any number of citations.

Second: if you disagree with how something should be classified, tell me. Especially if you think the decision tree gives the wrong answer. That is a defect and I want to fix it.

Third: the queueing thing.

The codes are the repository, the calculator, and me. Thank you.

*[Stop talking. Do not summarise. Take questions.]*

---

---

## Questions you should expect

**"Is this not just governance with extra steps?"**
Governance tells you what should be checked. This tells you what you can afford to check. Most governance frameworks assume review capacity is unlimited, and they were right to, until about two years ago.

**"Our reviewers are experienced, they can go faster than your floor."**
Good, and the floor is derived from your own reviewers rather than from mine, so it will reflect that. The floor is not a standard. It is a line below which a review could not have happened at all, and it is derived from watching your people work.

**"How do we measure the cost of checking without a big project?"**
Thirty reviews, one decision type, a stopwatch, and one question afterwards. It is an afternoon, not a workstream. Start with the decision type that worries you most.

**"What if we do not have enough qualified reviewers to hit any of these numbers?"**
Then you already knew that and this puts a figure on it. The useful move is usually reclassification rather than hiring, because hiring is slow and qualification is slower.

**"Does this mean we should slow down our AI adoption?"**
No, and I would push back on that reading. It means deploy where checking is cheap, which is usually more aggressive than what people are doing, not less. The constraint is on where, not on how much.

**"Where did the three point three come from?"**
Synthetic data, generated by a script in the repository, and it says so. It demonstrates the arithmetic works. It is not evidence and I would not want it quoted as evidence.

**"Who else is using this?"**
Nobody yet, it went public this week. That is the honest answer and I would rather give it than imply otherwise.
