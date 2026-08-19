# Script, 45 minutes

For the GSDC session. 45 minutes of talk, then 15 minutes of questions, inside a 60 to 70 minute slot. That leaves you real slack, which you want on a virtual session where the first four minutes go on somebody's audio.

`SCRIPT.md` is the spine: what you say on each of the 27 slides, in order. This file does two things. It sets the 45-minute running order, and it holds the eight additions that turn the 35-minute version into 45. Nothing here repeats what is on a slide.

**Reserve material** is at the bottom. Twelve more blocks, roughly seventeen minutes. If you finish at 38 you have somewhere to go.

---

## Running order

| | Slide | Time | Cumulative |
|---|---|---|---|
| **Open** | before slide 1 | 0:45 | 0:45 |
| | 1 Title | 1:00 | 1:45 |
| | 2 Part 1 divider | 0:20 | 2:05 |
| **Part 1** | 3 Thirty years | 1:30 | 3:35 |
| | 4 What did not move | 1:30 + **POLL 1** 1:30 | 6:35 |
| | 5 Nobody decides to | 2:00 + `[A]` 1:00 | 9:35 |
| | 6 The formula | 2:00 | 11:35 |
| | 7 Six people, twenty-one | 2:00 + **DEMO 1** 2:00 | 15:35 |
| | 8 Four classes | 2:00 | 17:35 |
| | 9 The quadrant | 1:30 | 19:05 |
| | 10 Part 2 divider | 0:20 | 19:25 |
| **Part 2** | 11 Five layers | 1:00 | 20:25 |
| | 12 Layer 1, order | 1:30 | 21:55 |
| | 13 Four fields | 1:30 | 23:25 |
| | 14 The people | 1:30 | 24:55 |
| | 15 Blast radius | 2:00 + `[B]` 1:00 | 27:55 |
| | 16 Six fields | 1:30 | 29:25 |
| | 17 Reference shape | 1:30 | 30:55 |
| | 18 Agents supplying | 1:30 + `[C]` 1:00 | 33:25 |
| | 19 Six numbers | 1:00 | 34:25 |
| | 20 Measuring drift | 2:00 + `[D]` 0:45 | 37:10 |
| | 21 The dashboard | 1:30 + **POLL 2** 1:15 | 39:55 |
| | 22 Four gates | 1:30 | 41:25 |
| | 23 Part 3 divider | 0:20 | 41:45 |
| **Part 3** | 24 S0 to S4 | 1:30 | 43:15 |
| | 25 What I do not know | 1:30 + `[E]` 0:45 | 45:30 |
| | 26 Monday | 1:30 + **DEMO 2** 1:00 | 48:00 |
| | 27 Take it and use it | 1:00 | 49:00 |

That lands at **49 minutes**, which is four over. Two ways to take them back, pick one on the day:

- **If Part 1 ran long,** drop slide 12 and slide 17. You lose the sequencing rule and the write-path diagram. Both are in the repo and neither is a headline. Saves 3:00.
- **If you are still long at slide 19,** cut `[D]` and shorten slide 22 to the one paragraph about the gate that gets skipped. Saves 1:45.

**Do not cut:** 5, 7, 15, 21, 26. Those are what people remember, and 21 is the one that changes behaviour.

**Two hard checkpoints.** You should be leaving slide 9 at **19 minutes** and leaving slide 21 at **40 minutes**. If you are more than three minutes past either, take the cuts above rather than speeding up. Talking faster on a webinar loses people; dropping a slide does not.

---

## Open, before slide 1

Wait for Pritam to finish, then camera on, no share yet.

> Thanks Pritam, and thanks to everyone who has joined at what I know is an odd hour for about half of you.

Then one sentence about what this is not. It saves you twenty minutes of the wrong questions later:

> Quick framing so nobody is waiting for something that is not coming. This is not a tools talk. I am not comparing platforms, I am not demoing a vendor, and I am not selling anything. This is one number, where it comes from, and what changes once you have it. All of it is open source and the link is on the last slide.

**Stay on camera for the full 45 seconds before you share.** People decide whether to keep the tab open in that window, and they decide about a face, not a slide.

---

## POLL 1, on slide 4

Launch it before you explain the slide. You want their number before you tell them what it means.

> How many people in your organisation are genuinely qualified to review the most consequential kind of decision your agents produce?
>
> 1 to 2  /  3 to 5  /  6 to 10  /  more than 10  /  we do not have agents producing decisions yet

Leave it open 45 seconds. Read the result out loud. The modal answer is almost always the second option.

> Right. Most of the room is at three to five people. Hold that number, because in about five minutes I am going to divide something by something else, and that number is going to be on top.

Then the substance, which is the bit the slide does not say:

> Here is what took me a while to see. When the models got better, two of the three things in that fraction got worse.
>
> The number of qualified reviewers did not change. But the artifacts got harder to check, because a well-written wrong answer takes longer to catch than a badly-written one. And the queue got longer, because production went up. Same people, harder things, more often.

---

## `[A]` Slide 5, the eleven minutes

One minute. Slow down here. This is the emotional centre of Part 1 and rushing it wastes the best material in the talk.

> I want to describe somebody, and I would like you to tell me in the chat whether you recognise them.
>
> It is Thursday. The pack goes out tomorrow. Nineteen items in the review queue, eleven minutes before the next call. This person is not lazy and they are not careless. They are the most conscientious person on the team. That is usually why they are the reviewer.
>
> And they approve nineteen items in eleven minutes. Not because they decided to wave them through. Because there was no version of that eleven minutes in which nineteen items got checked, and the queue has no button that says "I did not have time for this."

Pause. Then:

> All nineteen approvals are now in your governance record as reviews. If somebody audits you in March, the record is clean. Named reviewer, timestamped, complete.

Two beats of silence, then the line:

> Nobody chose that. And there was no error message.

**Chat prompt:** ask for a one-word yes if they recognise the person. You will get a wall of them. Acknowledge it and move: *"That is a lot of yes. Let us go and do the arithmetic on it."*

---

## DEMO 1, on slide 7

Two minutes, live. **Have the calculator tab open and font-scaled before the session starts.** If the share fails, read the numbers off the slide and carry on; do not debug on air.

> Rather than have you take my word for the arithmetic, let me do it in front of you.

Share. Type the numbers.

> Six people. Eight hours each. Utilisation point five five. Cost per decision, one and a quarter hours.
>
> Twenty-one. That is how many of these a week this organisation can genuinely review.
>
> Now demand. They are producing seventy.

Let the overdraft appear.

> Three point three. And the number I want you to look at is not that one, it is the row underneath. About forty-nine decisions a week with nobody's genuine review on them. Not at risk of it. The arithmetic does not leave anywhere else for them to go.

Then the move that makes it useful rather than depressing:

> Now watch what happens when I change the cost of checking.

Halve `c` on screen.

> Halve it and the budget doubles. I did not hire anybody. That is the whole strategy of this framework in one interaction, and Part 2 is how you actually do it.

Then hand it over:

> Link is on the last slide. It runs entirely in your browser, makes no network calls, and nothing you type leaves your machine. Put your own four numbers in during the Q&A and tell me what you get.

---

## `[B]` Slide 15, why not confidence

One minute, and it is the sharpest point in Part 2.

> Look at the middle column and tell me what is missing.
>
> Model confidence. Not there. Not at any level.
>
> That is deliberate, and it is the most useful thing on this slide. Every governance design I have seen tries to use confidence as the gate. Above ninety percent it acts, below ninety it asks. It is seductive because the number is right there in the response and it feels like it means something.
>
> It does not work, for a reason that is easy to say and hard to accept. Confident and wrong on an irreversible decision is still a disaster. The confidence did not make the decision reversible. Blast radius is a property of the world; confidence is a property of the model. You cannot govern the first with the second.

Then:

> Confidence still belongs in the system, and it is one of the six fields two slides from now. Its job is to tell a reviewer where to look. Its job is not to decide who gets to decide.

---

## `[C]` Slide 18, the two rules

One minute. Without this, slide 18 is the most dangerous one in the deck, because it sounds like free capacity.

> Two rules keep this honest.
>
> First. An agent can check another agent only if checking the checker is free. In practice that means the verifier emits assertions, not prose. If your verifier writes a paragraph explaining why the decision looks fine, you have created a second thing a human has to read. You moved the cost, you did not remove it.
>
> Second, and I would put this one on a wall. You only count the capacity if you have measured how often the verifier passes something bad. A verifier that passes everything looks magnificent on this slide. It closes a hundred percent of decisions and catches nothing, and every bad decision now reaches production wearing a green tick, which is worse than having no verifier, because at least without it somebody might have looked.
>
> So measure the false negatives, report an interval, and put the bottom of the interval in your budget rather than the middle. If you have not measured it, the answer is zero. Not "probably about half". Zero.

If you have thirty spare seconds, add the catch, because somebody will think of it:

> And there is a catch I was slow to notice. The verifier closes the easy ones first, so the queue reaching your humans is harder than the average was, which means your cost per decision goes up as containment goes up. I have no clean correction for that. What I have is a rule: re-measure the cost every time containment moves.

---

## `[D]` Slide 20, the rule that keeps the metric alive

45 seconds. This is the part that gets implemented wrong, and getting it wrong destroys the measurement.

> One rule about this, and it matters more than the maths.
>
> Never use this against an individual. Never put it in a performance review. Never send somebody a chart of their own review times.
>
> Because the moment you do, people manage the number instead of you measuring it. They leave the artifact open while they get a coffee. Times go up, drift goes to zero, and you have lost the only instrument that sees this failure mode. Report it by class, not by person. If your organisation cannot resist doing it by person, do not collect it at all. A corrupted metric is worse than a missing one, because a missing metric does not tell you everything is fine.

---

## POLL 2, on slide 21

Rhetorical rather than diagnostic. Launch, 30 seconds, then reveal.

> Look at these four numbers. Approval rate ninety-seven percent. Reversal rate two percent. Cycle time down forty-one. Escalations steady. Would you take that to a steering committee?
>
> Yes, happily  /  Yes, with caveats  /  No  /  I would want a fifth number

Most will say yes. That is the point.

> Most of you said yes, and you would be right to. Those are good numbers and every one of them improved.
>
> They are also all four consistent with supervision having completely stopped. Approval rate goes up when people stop checking. Cycle time goes down when people stop checking. Reversals stay low because you only reverse what you notice, and you do not notice what you did not check. Escalations stay steady because the agent's thresholds did not change.
>
> There is no number on that dashboard that goes red when verification stops. Not that the metrics are wrong. That they are all blind in the same direction, and it is the direction that matters.

Then the practical ask, which is the single most useful sentence in the talk:

> So if you take one thing from the whole hour: put drift on the same page as the good news. Not in an appendix. The same page. Because the good news is real, and it is also not the whole picture, and those two facts have to arrive together or the second one never arrives at all.

---

## `[E]` Slide 25, the honest 45 seconds

Do not undersell this. Naming your own gaps is what makes everything else credible, and this audience contains people who will test you.

> The queueing one is the one I would most like help with. The formula gives you a rate, twenty-one a week. But decisions do not arrive at a constant rate, they arrive in a lump the week before the board pack. So you can be comfortably inside budget averaged over a quarter and still drop reviews in week three, and the average tells you nothing was wrong. The right treatment is a proper queueing model with class-based priority. I have not built one. If somebody here knows queueing theory, that is issue one in the repo.

Then the one that matters most:

> And the number I showed you earlier. Three point three. That is synthetic. It comes from a generated example with a fixed seed, and it exists to show the arithmetic works and the tooling reproduces. It is not evidence, it is not a benchmark, and please do not put it in a slide as though it were a finding about the industry.
>
> What I want from this talk is the real version of that number, from you. There is an issue template called "Report a measured verification cost". Anonymised is fine. One measured cost with its method attached is worth more than everything I have said in the last forty minutes.

---

## DEMO 2 and the ask, on slide 26

One minute. **Terminal open, in the right directory, font already large.**

> The whole thing is one command, so let me show you rather than describe it.

```
vb budget --input examples/pmo40
```

> Four classes, four budgets, four demands, one of them in red. That is the synthetic example. Point it at your own config and it is your numbers.

Then the ask. Make it small enough that somebody actually does it:

> I am not going to ask you to adopt a framework. Nobody adopts a framework on a Tuesday.
>
> I am going to ask for one number. Pick your most consequential decision type, the one where you would be uncomfortable if it went wrong. Time three of those reviews this week. Ask the reviewer afterwards whether they genuinely checked. Write the number down.
>
> That is about forty minutes of work, and it is stage one for one decision type. Most of you will not like what the number says, which is exactly why it is worth having.

---

## Closing, slide 27

Let the QR codes sit on screen for a full fifteen seconds without talking over them. People need time to find a phone.

> Everything is there. Formula, schemas, calculator, eval harness, and the code that generates every number I showed you. Apache 2.0, so take it, change it, put your own name on the front if that gets it adopted where you work. I would rather it was used than credited.
>
> Three codes: the repository, the calculator, and me, if you want to argue about any of this, which I would enjoy.
>
> And the thing I am actually asking for is on that middle line. If one person here sends me a real cost figure from a real organisation, this was worth more than a hundred of you agreeing with me.

> Thanks very much. Happy to take questions.

---

## Q&A, 15 minutes

Pritam's moderator reads from chat. Six to expect, with the short answer. Longer versions are at the end of `SCRIPT.md`.

| Question | Short answer |
|---|---|
| "Is this not human-in-the-loop with extra steps?" | Human-in-the-loop says a human should be there. This says how many humans, for how many decisions, and what happens when you run out. It is the capacity model underneath the slogan. |
| "Our reviewers are fast, our cost is low." | Good. Measure it and tell me the number. If it is genuinely low you have more headroom than most, and you would be the first person I have asked who had the number ready. |
| "Does agents checking agents not solve this?" | It helps, on two conditions, and it was slide 18. Checking the checker has to be free, and you have to have measured how often it passes something bad. Otherwise it is a risk transfer that looks like a saving. |
| "Which tools do you recommend?" | Deliberately not answering, and not to be coy. None of this depends on a platform. It is arithmetic and four contract fields, and you could do it in a spreadsheet this week. |
| "How do I sell this to a CFO who wants headcount out?" | Do not fight it. Verification capacity is what caps how much of the automation actually counts. This gives you the ceiling as a number instead of a worry, and then you argue about where to spend against it. |
| "Is silent drift not a trust problem?" | It is a capacity problem wearing a trust problem's clothes. Your reviewer is behaving rationally given the constraint you handed them. You cannot train it away or policy it away. You can only budget it. |

**If one stumps you.** Say so plainly: *"I do not know. That is a better question than most of the ones on my limitations slide. Would you put it in the repo as an issue so I do not lose it?"* That costs you nothing with this audience and it is consistent with the last forty-five minutes.

**If it goes quiet.** Use the poll: *"Nearly all of you said yes to that dashboard. I would like to hear from anyone who said they would want a fifth number, and what the fifth number would have been."*

---

# Reserve

Twelve blocks, about seventeen minutes. Use these if you are running short. Ordered by what I would reach for first.

**R1. Slide 3, the pre-agent PMO (90s).** Shared memory, and it earns the room because everyone has lived it. Describe the old Thursday: opening forty project files, working out which dates moved and which were typed over, chasing eleven risk owners who all replied "no change" to make the question go away. Then: most of that work was transcription. Move a number from one system to another, write a sentence about it, put the sentence in a deck. Then the turn: the easy version of this story is "AI did the boring work so now we do the interesting work", and that story is wrong. Not because AI cannot do it, but because of what happens next.

**R2. Slide 6, each letter slowly (2m).** For the non-PMO half of the audience, and do not apologise for it. `R` is not headcount and not everybody with the approve button. The test: if this went wrong and somebody senior asked who checked it, whose name would you be willing to say out loud? `H` is hours in the calendar. `u` is what survives the calendar; half is a fair guess, and anyone claiming ninety percent has not measured it. Then `c`, and the step everybody skips: after timing the review, ask the reviewer whether they actually checked it, and throw away the ones who say they just approved it. That step is what separates a verification cost from an approval duration, and under overdraft those are different numbers.

**R3. Slide 8, classify three live (2m).** Call and response in chat, and the fastest way to make the classes stick. Read three decisions, ask for A, B, C or D. Critical path recalculation after a task update: A, because you recompute and compare and the comparison is the answer. Status narrative for forty projects: answers will split B and C, and the split is right. B for the thirty-seven nobody outside the programme reads, C for the three in the board pack, because a sample of twenty misses those three and those three are why anybody cares. You split the population; same decision type, two classes. Recommending a workstream cancellation: D, and notice nobody had to think about it.

**R4. Slide 9, the risk-analysis trap (90s).** Every impressive demo in this space lives in the top-right box, and they are impressive because the model really is good at them. But they are expensive to check, so the budget is a couple of dozen a week, so the deployment is capped at a couple of dozen a week however good the model gets. Then the line that upsets people: risk analysis is the easier AI problem than status reporting, and it should go live later. A status report can be checked against source systems in ninety seconds. A risk analysis needs somebody who was in the room in March. Expect pushback in chat; park it for Q&A.

**R5. Slide 13, the revocation story (1m).** Ask your own team this week: who can turn agent X off, right now, without a meeting, and how long does it take? If the answer involves a change advisory board, you do not have a revocation clause, you have a hope. Then the half nobody has thought about: what happens to work already in flight? Does it stop, finish, or roll back? You do not want to be deciding that at the same moment you are deciding to pull the agent. One action, one person, no meeting, a stated number of minutes, and tested with a stopwatch. An untested kill switch is not a kill switch.

**R6. Slide 14, the two roles (2m, includes a poll).** Poll: which of these exists in your organisation today with a named person in it? Somebody who owns agent contracts / somebody who owns review capacity / both / neither / not sure. The answer will be overwhelmingly neither, and that is the finding, not a criticism. Then why: neither is a technical role, neither is a data scientist, and accountability roles are the hardest thing to fund because you cannot demo them. The second is the one to fight for. Somebody has to be able to walk into a steering committee and say we cannot take that agent live, because this class is already at three times budget. If nobody owns that sentence, nobody says it, and every deployment gets approved on its own merits while the aggregate quietly breaks.

**R7. Slide 16, the two jobs (90s).** Two of the six do different jobs and people conflate them. Sources saves time: when you time real reviews, it is almost never the thinking, it is going and finding the four things the agent already found. Put them in the artifact with links and you delete the biggest block of cost, forty to sixty percent. The counter-case catches errors: the agent saying here is the strongest reason I am wrong and here is where you would see it. Without it a reviewer reads evenly and hopes something jumps out. With it they are looking for one named thing. One saves time, the other finds mistakes. If you only build one, build sources.

**R8. Slide 22, the gate that gets skipped (90s).** It is the cost measurement in gate one, predictably and always. Three reviewers, twenty outputs, a stopwatch, and an awkward conversation. Nobody wants to run it, it has no demo, it produces one number. It is also the only one of the four that tells you how far you can scale, and everything else in the talk is denominated in it. Which is why it went into the first gate rather than an appendix: so skipping it fails a gate instead of becoming a to-do. Then the escalation probe: it is at a hundred percent, not ninety-five, because it is a mechanism test, not a sample. If a named condition does not fire when you inject exactly the condition it names, that condition is not implemented, whatever the contract says. And do not fix a failure by loosening the condition until it stops failing; that turns a problem you measured into one you did not.

**R9. Slide 24, the one question (1m).** One question tells you which stage you are at and it takes four seconds. What is your verification cost per decision for your most consequential class, and when did you last measure it? A number and a date means at least stage one. No number means stage zero, however much governance documentation exists, however many committees, however many agents are live. Most organisations describing themselves as well down this road are at stage zero with good paperwork. Which is not a disaster: stage one is a few weeks and it is the only step you cannot skip.

**R10. Slide 24, why it stops at four (45s).** Keep it short and do not get philosophical. A system that also sets its own risk appetite and audits its own drift is not a further stage, it is the removal of the thing the model is about. The budget is a budget of human verification. Take the human out and you do not have an infinite budget, you have no budget, because there is nobody whose approval means anything from outside the system making the claim. Four is the ceiling by construction, not caution.

**R11. Slide 12, the sequencing rule (45s).** One line: reclassify, then deploy. Not deploy and then improve the checking, which is what everybody does. Because during the gap you are running an overdraft, the overdraft is invisible, so nothing forces the gap to close. Six months later the improvement is still on the roadmap and the agent is still running.

**R12. Slide 17, the write path (45s).** One line that turns an architecture diagram into a governance diagram: nothing writes back to source systems until it has cleared verification. The write path is the boundary, which means the boundary is enforced by plumbing rather than policy. A decision that has not cleared verification physically cannot reach the project plan, because it does not have the credentials. That is worth more than any amount of documentation, because documentation degrades and permissions do not.
