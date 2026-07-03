---
name: grill-the-goal
description: Interview the user to lock down a vague goal's outcome, success criteria, and constraints before any work starts. Use when the user has a fuzzy goal, an unscoped request, or asks to "grill the goal," "scope this," or "figure out what I actually want." Deliberately does not touch implementation steps, architecture, or sequencing — pair with plan mode or grill-me for that.
---

# Grill the Goal

Interview me relentlessly about what I actually want — not how to build it. This applies whether the goal is a whole new product or a single feature in an existing system. Walk down each branch until three things are locked: the outcome, how we'll know it's done, and the hard constraints. Ask one question at a time, and always propose your own best-guess answer so I'm confirming or correcting, not staring at a blank page. If something can be inferred from context already in this conversation, or from files/codebase you can check, don't ask — state your inference and let me correct it.

## Rules

1. **One question per turn.** Never bundle.
2. **Every question comes with options and a recommended answer.** Defaulting to "what do you think?" is lazy.
3. **Stay off the "how."** Don't ask the user to make implementation decisions (which data structure, which library, how to sequence the work) — that's a different job (use `/plan` or `grill-me` for that, after this). But technical facts can still be constraints: "must integrate with the existing risk-engine process," "must not add new external dependencies," "must hit sub-millisecond latency," "must reuse the existing order-routing module."
4. **Cover three areas, roughly in order:**
   - **Outcome** — what does done actually look like, concretely, for this specific thing? What's in scope, what's explicitly not?
   - **Success criteria** — how will we know it worked? What would make it a failure even if it technically "runs" or "ships"?
   - **Constraints** — what must never happen, what's fixed and non-negotiable, what's explicitly out of scope?
5. **Stop when genuinely resolved.** Don't manufacture extra questions once all three areas are locked.
6. **Close with a recap** — the finished goal, success criteria, and constraints in plain language, ready to hand to whatever does the actual planning or building.
