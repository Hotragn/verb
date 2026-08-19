# Script expansions, 62 minutes

`SCRIPT.md` runs the 27 slides in about 35 minutes. GSDC has given you 60 to 70 minutes plus 15 minutes of questions. This file is the extra 27 minutes.

It is not more slides. It is depth, three polls, two live demos and four objections handled out loud. That is the right way to fill a 70-minute virtual slot, because slides you talk over for four minutes hold attention and slides you flip through do not.

**How to use this.** Run `SCRIPT.md` as your spine. Where it says `[EXPAND n]` below, you are in the corresponding slide's section and you insert the block from here. Nothing in this file repeats what is on a slide.

---

## Running order, 62 minutes

| | Slide | Base | Expansion | Total |
|---|---|---|---|---|
| **Open** | 1 Title | 1:00 | +1:00 host thanks, what this is not | 2:00 |
| | 2 Part 1 | 0:20 | | 0:20 |
| **Part 1** | 3 Thirty years | 1:30 | +1:30 `[EXPAND A]` the pre-agent PMO | 3:00 |
| | 4 What did not move | 1:30 | +2:00 `[EXPAND B]` **POLL 1** | 3:30 |
| | 5 Nobody decides to | 2:00 | +1:30 `[EXPAND C]` the eleven minutes | 3:30 |
| | 6 The formula | 2:00 | +2:00 `[EXPAND D]` each letter, slowly | 4:00 |
| | 7 Six people, twenty-one | 2:00 | +2:30 `[EXPAND E]` **LIVE DEMO 1** | 4:30 |
| | 8 Four classes | 2:00 | +2:00 `[EXPAND F]` classify three live | 4:00 |
| | 9 The quadrant | 1:30 | +1:30 `[EXPAND G]` the risk-analysis trap | 3:00 |
| | | | | **~28:00** |
| | 10 Part 2 | 0:20 | | 0:20 |
| **Part 2** | 11 Five layers | 1:00 | +0:30 | 1:30 |
| | 12 Layer 1 order | 1:30 | +1:00 `[EXPAND H]` | 2:30 |
| | 13 Four fields | 1:30 | +1:00 `[EXPAND I]` revocation story | 2:30 |
| | 14 The people | 1:30 | +2:00 `[EXPAND J]` **POLL 2** | 3:30 |
| | 15 Blast radius | 2:00 | +1:30 `[EXPAND K]` | 3:30 |
| | 16 Six fields | 1:30 | +1:30 `[EXPAND L]` | 3:00 |
| | 17 Reference shape | 1:30 | +1:00 `[EXPAND M]` | 2:30 |
| | 18 Agents supplying | 1:30 | +1:30 `[EXPAND N]` | 3:00 |
| | 19 Six numbers | 1:00 | +0:30 | 1:30 |
| | 20 Measuring drift | 2:00 | +1:00 `[EXPAND O]` | 3:00 |
| | 21 The dashboard | 1:30 | +1:00 `[EXPAND P]` **POLL 3** | 2:30 |
| | 22 Four gates | 1:30 | +1:30 `[EXPAND Q]` | 3:00 |
| | | | | **~32:00** |
| | 23 Part 3 | 0:20 | | 0:20 |
| **Part 3** | 24 S0 to S4 | 1:30 | +1:00 `[EXPAND R]` | 2:30 |
| | 25 What I do not know | 1:30 | +1:00 `[EXPAND S]` | 2:30 |
| | 26 Monday | 1:30 | +1:00 `[EXPAND T]` **LIVE DEMO 2** | 2:30 |
| | 27 Take it and use it | 1:00 | +0:30 | 1:30 |
| | | | | **~9:30** |

**About 62 minutes.** You have 60 to 70, so you have slack. If you are running long at slide 19, drop expansions M, O and Q and you land at 56.

**Do not drop:** 7, 15, 21, 26. Those are the four slides people will remember, and three of them are in Part 2.

---

## Open, before slide 1

Wait for the moderator to finish, then:

> Thanks Pritam, and thanks to everyone who has joined at what I know is a strange hour for about half of you.

Then, before the title slide lands, one sentence about what this is not. It saves you twenty minutes of the wrong questions:

> Quick framing so nobody is waiting for something that is not coming. This is not a tools talk. I am not going to compare platforms, I am not going to demo a vendor, and I am not selling anything. This is one number, where it comes from, and what changes once you have it. Everything I show you is open source and the link is on the last slide.

**Camera note.** Stay on camera for the first ninety seconds before you share. People decide whether to keep the tab open in that window.

---

## `[EXPAND A]` Slide 3, the pre-agent PMO

Ninety seconds of shared memory. This is where you earn the room, because everybody on the call has lived it.

> Think about what your Thursday used to look like. Somebody had to open forty project files. Somebody had to work out which of the dates had moved and which had moved because somebody typed over them. Somebody had to chase eleven risk owners who had all replied "no change" to make the number go away.
>
> And the honest thing about all of that work is that it was mostly transcription. Move a number from one system to another system, write a sentence about it, put the sentence in a deck. That is what a PMO analyst's week was, and everybody in this call knows it because everybody in this call has done it.

Then the turn:

> I want to be careful here, because the easy version of this story is "AI did the boring work and now we do the interesting work", and that story is wrong. It is not wrong because AI cannot do it. It is wrong because of what happens next, and what happens next is the whole talk.

---

## `[EXPAND B]` Slide 4 and POLL 1

Run the poll before you explain the slide. You want their number before you tell them what the number means.

**POLL 1** (launch it, leave it open 45 seconds):

> How many people in your organisation are genuinely qualified to review the most consequential kind of decision your agents produce?
>
> 1 to 2  /  3 to 5  /  6 to 10  /  more than 10  /  we do not have agents producing decisions yet

Read the results out loud. The modal answer is almost always 1 to 2 or 3 to 5.

> Right. So most of the room is at three to five people. Hold that number, because in about four minutes I am going to divide by something and that number is going to be on top.

Then the substance:

> Here is the part that took me a while to see. When the models got better, two of the three things in that fraction got worse, not better.
>
> The number of qualified reviewers did not change. But the artifacts got harder to check, because a well-written wrong answer takes longer to catch than a badly-written wrong answer. And the queue got longer, because production went up. So you have the same people, checking harder things, more often.

---

## `[EXPAND C]` Slide 5, the eleven minutes

Slow down here. This is the emotional centre of Part 1 and it should not be rushed.

> I want to describe somebody, and I would like you to tell me in the chat whether you recognise them.
>
> It is Thursday. The pack goes out tomorrow. There are nineteen items in the review queue and there are eleven minutes before the next call. This person is not lazy, they are not careless, and they are not cutting corners because they do not care. They are the most conscientious person on your team. That is usually why they are the reviewer.
>
> And they approve nineteen items in eleven minutes. Not because they decided to wave them through. Because there was no version of that eleven minutes in which nineteen items got checked, and the queue does not have a button that says "I did not have time for this."

Pause. Then:

> Every one of those nineteen approvals is now in your governance record as a review. If somebody audits you in March, the record is clean. Nineteen decisions, nineteen approvals, named reviewer, timestamped.

Then the line that has to land clean:

> Nobody chose to do that. And there was no error message.

Let two seconds go by. Then:

> That is what I mean by silent drift. It is silent because your system records it as success.

**Chat prompt:** ask them to type a single word if they recognise the person. You will get a wall of "yes". Acknowledge it: *"OK, that is a lot of yes. Let us go and do the arithmetic on it."*

---

## `[EXPAND D]` Slide 6, each letter slowly

Two extra minutes taking the formula apart for the non-PMO half of the audience. Do not apologise for going slowly.

> Four letters, and I want to do them one at a time, because three of them are easy and one of them is the whole problem.
>
> **R** is people. Not headcount, not full-time equivalents, and not everybody with the approve button in the tool. The test I use is uncomfortable and it is the right test: if this decision went wrong and somebody senior asked who checked it, whose name would you be willing to say out loud? Those people are R. Usually it is a smaller number than the org chart suggests.
>
> **H** is hours a week each of them has nominally set aside for reviewing. Whatever is in the calendar.
>
> **u** is what is left of H after the calendar happens to it. Meetings, escalations, somebody's laptop dying. If you have never measured it, half is a fair first guess. If somebody tells you their utilisation is ninety percent, they have not measured it either.
>
> Multiply those three and you have hours of genuine review capacity per week. That is the top of the fraction and there is nothing surprising in it.

Then:

> **c** is the one that matters. c is how long it takes one qualified person to genuinely check one decision. And almost nobody has this number.
>
> That is not a criticism, it is just true, and the reason it is true is that measuring it is annoying. You have to time real reviews. And then you have to do the step everybody skips, which is go back to the reviewer afterwards and ask: did you actually check that, or did you approve it? And then throw away the ones where they say they approved it.
>
> That last step is what separates a verification cost from an approval duration. When you are over budget, those are two completely different numbers, and if you skip the step you will measure the wrong one and your budget will look fine.

---

## `[EXPAND E]` Slide 7 and LIVE DEMO 1

The calculator, live. Two and a half minutes. **Have the tab already open before the session starts.**

> Rather than have you take my word for the arithmetic, let me just do it in front of you.

Share the calculator. Type the numbers from the slide.

> Six people. Eight hours each. Utilisation point five five. And cost per decision, one and a quarter hours.
>
> Twenty-one. That is the number of these a week that this organisation can genuinely review.
>
> Now demand. They are producing seventy.

Let the overdraft figure appear. Then:

> Three point three. And the thing I want you to look at is not the three point three, it is the row underneath: about forty-nine decisions a week with nobody's genuine review on them. Not at risk of not being reviewed. Not reviewed. The arithmetic does not leave anywhere else for them to go.

Then the part that makes it theirs:

> Now let me do the thing that makes this useful. Watch what happens when I change c.

Halve c on screen.

> Halve the cost of checking and the budget doubles. I did not hire anybody. That is the entire strategy of this framework in one interaction, and Part 2 is thirty minutes on how you actually do it.

Then hand it to them:

> The link is on the last slide. It runs entirely in your browser, it makes no network calls, and nothing you type goes anywhere. Put your own four numbers in it during the Q&A and tell me what you get.

---

## `[EXPAND F]` Slide 8, classify three live

Two minutes. Do this as a call-and-response in chat. It is the fastest way to make the classes stick.

> I am going to read out three decisions and I want you to put A, B, C or D in the chat. And I want to be clear that I am not asking how risky they are or how hard they are. I am asking how expensive it is to check one.
>
> One. An agent recalculates the critical path after somebody updates a task.

Wait. Answers will be mostly A.

> A. Yes. You can recompute it and compare, and the comparison is the answer.
>
> Two. An agent writes the status narrative for forty projects.

Answers will split B and C. Use the split:

> Good, and look at the split, because the split is right. It is B, with a catch, and the catch is the most useful thing in this section. It is B for the thirty-seven projects nobody outside the programme reads. It is C for the three that go in the board pack, because a sample of twenty will miss those three, and those three are the reason anybody cares.
>
> That is not a compromise, that is the answer. You split the population. Same decision type, two classes.
>
> Three. An agent recommends cancelling a workstream.

Answers will be D.

> D. And notice nobody had to think about it. That is what D feels like: you know before you finish the sentence.

Then close the loop:

> Which brings me to the rule that I get the most argument about, so let me say it plainly. Agents do not make D decisions. Ever. Not with a confidence threshold, not with two approvers, not with a committee. And the reason is not caution, it is arithmetic. A D decision has no finite checking cost, so it has no budget, so there is no amount of it you can afford. Delegating it is not accepting risk, it is spending money that is not there.
>
> But you still get the throughput, and the trick is in Part 2.

---

## `[EXPAND G]` Slide 9, the risk-analysis trap

Ninety seconds. This is the slide that changes a roadmap, so make the consequence concrete.

> I want to push on the top-right box, because that is where I have watched good teams lose a year.
>
> Every genuinely impressive demo I have seen in this space lives in that box. Portfolio prioritisation. Vendor dispute strategy. Dependency renegotiation across programmes. And they are impressive because the model really is good at them. That is not marketing.
>
> But they are all expensive to check. So your budget for them is a couple of dozen a week. Which means your deployment is capped at a couple of dozen a week, no matter how good the model gets, and no matter how much you spent.

Then the counter-intuitive line, which is the whole slide:

> Here is the version of this that upsets people. Risk analysis is the easier AI problem than status reporting. And it should go live later.
>
> Because a status report can be checked against the source systems in about ninety seconds. A risk analysis needs somebody who was in the room in March. Difficulty and checking cost are different axes, and only one of them is your constraint.

**Expect pushback in the chat here.** Acknowledge it and park it: *"I can see a couple of you disagreeing and I would genuinely like to hear it in the Q&A."*

---

## `[EXPAND H]` Slide 12, sequencing

> The practical version of this is a sequencing rule, and it is one line. **Reclassify, then deploy.**
>
> Not deploy and then improve the checking, which is what everybody does, including me the first time. Because during the gap you are running an overdraft, and the overdraft is invisible, so nothing forces the gap to close. Six months later the improvement is still on the roadmap and the agent is still running.

---

## `[EXPAND I]` Slide 13, the revocation story

One minute. The fourth field is the one people leave out, so give it a story rather than an argument.

> I want to dwell on the fourth one, because it is the one that gets dropped and it is the one that matters at the worst moment.
>
> Ask your own team this question this week: who can turn agent X off, right now, without a meeting, and how long does it take? If the answer involves a change advisory board, you do not have a revocation clause. You have a hope.
>
> And there is a second half of that question that almost nobody has thought about, which is: what happens to the work already in flight? Does it stop? Does it finish? Does it roll back? Because if you revoke an agent and twenty decisions are half-made, somebody has to decide what those twenty are, and you do not want to be deciding that at the same time as you are deciding to pull the agent.
>
> The clause should be one action, one person, no meeting, and a stated number of minutes. And you should have tested it, with a stopwatch, in a non-production environment. An untested kill switch is not a kill switch.

---

## `[EXPAND J]` Slide 14 and POLL 2

**POLL 2** (launch before you talk through the slide):

> Which of these exists in your organisation today, with a named person in it?
>
> Somebody who owns agent contracts  /  Somebody who owns review capacity  /  Both  /  Neither  /  Not sure

The answer will be overwhelmingly Neither. Use it:

> Ninety-odd percent neither. That is not a criticism of the room, that is the finding. Two roles that this operating model needs, and almost nobody has either of them.

Then:

> And I want to be honest about why, because it is not that people have not thought of it. It is that neither of these is a technical role. Neither of them is a data scientist. They are both accountability roles, and accountability roles are the hardest thing to get funded, because you cannot demo them.
>
> The second one is the one I would fight for. Somebody has to own the number. Somebody has to be able to walk into a steering committee and say: we cannot take that agent live, because Class C is already at three times its budget and this would make it four. If nobody owns that sentence, nobody says it, and every deployment gets approved on its own merits while the aggregate quietly breaks.

**Chat prompt:** *"If either of these exists in your organisation, put the job title in the chat. I collect these."*

---

## `[EXPAND K]` Slide 15, why not confidence

Ninety seconds, and it is the sharpest point in Part 2.

> Look at the middle column and tell me what is missing from it.
>
> Model confidence. It is not there. Not at any level.
>
> That is deliberate and it is the single most useful thing on this slide. Every governance design I have seen tries to use confidence as the gate. Above ninety percent it acts, below ninety percent it asks. And it is seductive, because the number is right there in the response and it feels like it means something.
>
> It does not work, for a reason that is easy to say and hard to accept: confident and wrong on an irreversible decision is still a disaster. The confidence did not make the decision reversible. The blast radius is a property of the world, and the confidence is a property of the model, and you cannot govern the first with the second.

Then:

> Confidence still belongs in the system, and it is one of the six evidence fields on the next slide but one. Its job is to tell a reviewer where to look. Its job is not to decide who gets to decide.

---

## `[EXPAND L]` Slide 16, the two questions

> There are two of these six I want to draw out, because they do different jobs and people conflate them.
>
> The sources field is the one that saves time. When you time real reviews and ask people what took so long, it is almost never the thinking. It is going and finding the four things the agent had already found. So put them in the artifact, with links, and you delete the biggest block of the cost. That is forty to sixty percent, in my experience, and it is the cheapest thing on this list to implement.
>
> The counter-case is the one that catches errors. It is the agent saying: here is the strongest reason I am wrong, and here is where you would see it. And that changes what a review is. Without it, a reviewer reads the whole artifact evenly, hoping something jumps out. With it, they are looking for one named thing. That is a completely different activity and it is much better at finding problems.
>
> One saves you time. The other finds the mistakes. You want both, and if you only build one, build the sources.

---

## `[EXPAND M]` Slide 17, the write path

> One line on this diagram and then I will move on, because it is the line that makes it a governance diagram rather than an architecture diagram.
>
> Nothing writes back to the source systems until it has cleared verification. Everything flows left to right, and the write path is the boundary.
>
> Which means the boundary is enforced by plumbing rather than by policy. If a decision has not cleared the verification layer, it physically cannot reach the project plan, because it does not have the credentials. That is worth more than any amount of documentation, because documentation degrades and permissions do not.

---

## `[EXPAND N]` Slide 18, the two rules

> There are two rules that keep this honest, and without them this slide is the most dangerous one in the deck, because it sounds like free capacity.
>
> First rule. An agent can check another agent only if checking the checker is free. Which in practice means the verifier emits assertions, not prose. If your verifier writes a paragraph explaining why it thinks the decision is fine, congratulations, you have created a second thing a human has to read. You have moved the cost, not removed it.
>
> Second rule, and this is the one I would put on the wall. You only count the capacity if you have measured how often the verifier passes something bad. A verifier that passes everything looks fantastic on this slide. It closes one hundred percent of decisions and it catches nothing, and every bad decision now reaches production wearing a green tick, which is strictly worse than no verifier at all, because at least without it somebody might have looked.
>
> So: measure the false negatives, report a confidence interval, and put the bottom of the interval in your budget rather than the middle. If you have not measured it, the answer is zero. Not "probably about half". Zero.

Then the honest catch, because it will occur to somebody:

> And there is a catch that took me embarrassingly long to notice. The verifier closes the easy ones first. So the queue that reaches your humans is harder than the average was, which means your cost per decision goes up as your containment goes up. I do not have a clean correction for that. What I have is a rule: re-measure the cost every time containment moves. It is on the limitations slide too.

---

## `[EXPAND O]` Slide 20, the floor

> Two things about the floor, because this is the part that gets implemented wrong.
>
> First, the floor comes from your own data, not from mine. You take a period where you know people were genuinely reviewing, because you sat with them and asked, and you take the tenth percentile of those times. That is your "nobody who is actually checking goes faster than this" line. Do not use my numbers. Mine are from a synthetic example.
>
> Second, and this is the one that makes the metric survive contact with an organisation: never use this against an individual. Never put it in a performance review. Never send somebody a chart of their own review times.
>
> Because the moment you do, people manage the number instead of you measuring it. They leave the artifact open while they get a coffee. Times go up, drift goes to zero, and you have lost the only instrument that sees this failure mode. Report it by class. Not by person. If your organisation cannot resist doing it by person, do not collect it at all, because a corrupted metric is worse than a missing one. A missing metric does not tell you everything is fine.

---

## `[EXPAND P]` Slide 21 and POLL 3

**POLL 3**, and this one is rhetorical rather than diagnostic. Launch it, let it sit for 30 seconds, then reveal.

> Look at these four numbers. Approval rate ninety-seven percent. Reversal rate two percent. Cycle time down forty-one. Escalations steady. Would you take that to a steering committee?
>
> Yes, happily  /  Yes, with caveats  /  No  /  I would want a fifth number

Then:

> Most of you said yes. And you would be right to, because those are good numbers and every single one of them improved.
>
> They are also all four consistent with supervision having completely stopped. Approval rate goes up when people stop checking. Cycle time goes down when people stop checking. Reversals stay low because you only reverse what you notice, and you do not notice what you did not check. Escalations stay steady because the agent's thresholds did not change.
>
> There is no number on that dashboard that goes red when verification stops. That is the point of the slide. Not that the metrics are wrong, but that they are all blind in the same direction, and it is the direction that matters.

Then the ask:

> So the practical thing I would take from this whole talk, if you take one thing: put drift on the same page as the good news. Not in an appendix. On the same page. Because the good news is real, and it is also not the whole picture, and those two facts have to arrive together or the second one never arrives at all.

---

## `[EXPAND Q]` Slide 22, the gate that gets skipped

> I want to flag which of these gets skipped, because it is predictable and it is always the same one.
>
> It is the cost measurement inside gate one. And the reason is that it is the least interesting one to do. Three reviewers, twenty real outputs, a stopwatch, and then the awkward conversation where you ask somebody whether they actually checked the thing they approved.
>
> Nobody wants to run that. It has no demo. It produces one number.
>
> It is also the only one of the four that tells you how far you can scale, and everything else in this talk is denominated in it. If you skip it, every other gate is measuring something in units you do not have. So it went into the first gate deliberately, so that skipping it fails the gate rather than being a to-do item.

Then, on the escalation probe:

> And one more on gate three. The escalation test is at one hundred percent, not ninety-five, and people push back on that. The reason is that it is not a sample, it is a mechanism test. You are not estimating what fraction of escalations fire. You are asking whether each named condition works. If one of them does not fire when you inject the exact condition it names, that condition is not implemented, whatever the contract says. There is no acceptable percentage of safety mechanisms that do not work.
>
> And do not fix a failure by loosening the condition until it stops failing. I have seen that done. It converts a problem you measured into a problem you do not.

---

## `[EXPAND R]` Slide 24, the one question

> There is one question that tells you which stage you are actually at, and it takes about four seconds.
>
> What is your verification cost per decision for your most consequential class, and when did you last measure it?
>
> If there is a number and a date, you are at least at S1. If there is not, you are at S0, and it does not matter how much governance documentation you have, how many committees exist, or how many agents are live. Most organisations that describe themselves as being well down this road are at S0 with good paperwork.
>
> Which is not a disaster. S1 is a few weeks of work. It is genuinely the cheapest step on this ladder and it is the only one you cannot skip.

On the absence of S5, keep it short and do not get philosophical:

> And on why it stops at four. A system that also sets its own risk appetite and audits its own drift is not a further stage of this. It is the removal of the thing the model is about. The budget is a budget of human verification. Take the human out and you do not have an infinite budget, you have no budget, because there is nobody whose approval means anything from outside the system making the claim. So four is the ceiling by construction, not because I am being cautious.

---

## `[EXPAND S]` Slide 25, the honest minute

Do not rush this and do not undersell it. Naming your own gaps is what makes the rest credible, and this audience contains people who will test you on it.

> The queueing one is the one I would most like help with, so let me be specific about what is wrong.
>
> The formula gives you a rate. Twenty-one a week. But decisions do not arrive at a constant rate. They arrive in a lump the week before the board pack. So you can be comfortably inside your budget averaged across a quarter and still drop reviews in week three, and the average will tell you nothing was wrong.
>
> The right treatment is a proper queueing model with class-based priority and a stated service discipline. I have not built one. If somebody on this call knows queueing theory, that is the open problem, and it is issue one in the repository.

Then the one that matters most for credibility:

> And the number I showed you earlier. Three point three. That is synthetic. It comes from a generated example in the repository with a fixed seed, and it exists to show that the arithmetic works and that the tooling reproduces. It is not evidence, it is not a benchmark, and please do not put it in a slide as though it were a finding about the industry.
>
> What I actually want from this talk is the real version of that number, from you. There is an issue template in the repository called "Report a measured verification cost". Anonymised is fine. One measured cost with the method attached is worth more than everything I have said in the last hour.

---

## `[EXPAND T]` Slide 26 and LIVE DEMO 2

Thirty seconds of terminal, then the ask. **Have the terminal open, in the right directory, font already scaled up.**

> The whole thing is one command, so let me show you rather than describe it.

```
vb budget --input examples/pmo40
```

> Four classes, four budgets, four demands, and one of them in red. That is the synthetic example, so those are the synthetic numbers. Point it at your own config and it is your numbers.

Then the ask, and this is the last thing you say before the closing slide, so make it small enough that somebody actually does it:

> I am not going to ask you to adopt a framework. That is not a thing anyone does on a Tuesday.
>
> I am going to ask for one number. Pick your most consequential decision type, the one where you would be uncomfortable if it went wrong. Time three of those reviews this week. Ask the reviewer afterwards whether they genuinely checked. Write the number down.
>
> That is it. That is S1 for one decision type, and it is about forty minutes of work. And most of you will not like what the number says, which is exactly why it is worth having.

---

## Closing, slide 27

Let the QR codes sit on screen for a full fifteen seconds without talking over them. People need time to raise a phone.

> Everything is there. The formula, the schemas, the calculator, the eval harness, the code that generates every number I showed you. Apache 2.0, so take it, change it, put your own name on the front of it if that gets it adopted where you work. I would rather it was used than credited.
>
> Three codes. The repository, the calculator, and me, if you want to argue about any of this afterwards, which I would enjoy.
>
> And genuinely, the thing I am asking for is on that middle line: issues and measured verification costs. If one person on this call sends me a real cost figure from a real organisation, this hour was worth more than if a hundred of you agreed with me.

Then hand back:

> Thanks very much. I am happy to take questions.

---

## Q&A, 15 minutes

The moderator reads from chat. Six you should expect, with the short answer. Full versions are at the end of `SCRIPT.md`.

| Question | Short answer |
|---|---|
| "Is this not just human-in-the-loop with extra steps?" | Human-in-the-loop tells you a human should be there. This tells you how many humans, for how many decisions, and what happens when you run out. It is the capacity model under the slogan. |
| "Our reviewers are fast, our c is low." | Good. Measure it and tell me the number. If it is genuinely low you have more headroom than most, and you will be the first organisation I have asked that had the number ready. |
| "What about agents checking agents, does that not solve it?" | It helps, on two conditions, and it is slide 18. Checking the checker has to be free, and you have to have measured how often it passes something bad. Otherwise it is a risk transfer that looks like a cost saving. |
| "Which tools do you recommend?" | Deliberately not answering that, and not because I am being coy. Nothing in this depends on a platform. It is arithmetic and four contract fields, and you can implement it in a spreadsheet this week. |
| "How do I sell this to a CFO who wants headcount reduction?" | You do not fight it. Verification capacity is what caps how much of the automation actually counts. This is how you show the ceiling with a number instead of a worry, and then argue about where to spend against it. |
| "Is silent drift not just a trust issue?" | It is a capacity issue that looks like a trust issue. Your reviewer is behaving rationally under the constraint you handed them. You cannot train it away, and you cannot policy it away. You can only budget it. |

**If a question stumps you.** Say so, and say it plainly: *"I do not know. That is a better question than most of the ones on my limitations slide. Would you put it in the repo as an issue so I do not lose it?"* That answer costs you nothing with this audience and it is consistent with everything else you have said for an hour.

**If it goes quiet.** Prompt with the poll result: *"Nearly everybody said Neither on that roles poll. I would like to hear from anyone who said Both, because I want to know what you called the job."*
