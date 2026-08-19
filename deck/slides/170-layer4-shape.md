layout: default
section: Layer 4, technology
---
## Reference shape, end to end.

```small
   SOURCES              AGENTS                EVIDENCE PLANE          VERIFICATION
   ------------         ------------------    -------------------     ------------------
   Work tracker    -->  Class A checkers  --> Decision artifacts  -->  Rule engine (auto)
   Code and CI     -->  Summarisers       --> Source links        -->  Sampling queue
   Finance ledger  -->  Analysts          --> Counter-case        -->  Expert review queue
   Comms and docs       (propose only)    --> Reversal path       -->  Committee record
                        Escalation router
        ^                                                                     |
        |                                                                     |
        +---------------------  write path, only after  ----------------------+
                                verification clears
```

<p class="lead">Nothing writes back to the source systems until it has cleared
verification. The write path is the governance boundary.</p>

@notes

Trace the arrows left to right with your hand once, then stop and talk about the
line at the bottom, because that is the whole slide.

Most teams put the governance boundary at the model: what may the agent see,
what may it be asked. That is the wrong boundary, because reading is not where
the risk is. The boundary belongs on the write path. An agent that reads
everything and writes nothing until a check clears is a safe agent, whatever
else it is doing.

This also gives you a cheap architectural test that anybody can apply. Ask of any
proposed integration: can this agent write to a source system without a
verification step in between? If yes, the boundary is in the wrong place, and no
amount of prompt engineering fixes that.

Note the analysts are marked propose only. That is Class C from Part 1 showing up
in the architecture rather than in a policy document.
