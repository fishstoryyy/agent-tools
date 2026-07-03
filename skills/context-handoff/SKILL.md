---
name: context-handoff
description: Use this skill whenever the user wants to hand a task off to a fresh agent, subagent, or new chat session that won't share this conversation's history — e.g. "write a handoff prompt so a new session can review this diff", "give me something I can paste into a new chat to keep working on this", "brief a fresh agent on this so they can pick it up", "condense this into a prompt for someone else to run with", "I'm going to open a new session for X, set it up with the right context". The output is a single, tight, self-contained prompt — not a recap of the conversation — built around whatever task the user names.
---

# Context Handoff

## What this skill produces

One prompt, ready to copy and paste into a fresh session. That fresh agent will have the same tools and environment you do (it can read the same files, run the same commands, browse the same web) but none of the history of this conversation. Your job is to write down only what would otherwise be lost when that history disappears.

## The core question to ask yourself

For every fact you're tempted to include, ask: **could a competent agent discover this on its own by looking at the environment?**

- "The auth module is in `src/auth/`" — discoverable. Skip it, or just point at the path.
- "We tried JWT refresh tokens first and dropped them because they broke the mobile SSO flow" — not discoverable. That's a decision that only exists in this conversation, and a fresh agent could easily re-propose the same dead end without it.
- "The function is called `validateSession`" — discoverable, don't bother.
- "The user wants error messages to stay generic for security reasons, even though that makes debugging harder" — not discoverable, and easy to get wrong by "improving" it later.

The stuff sitting in the code, files, or repo isn't your job to transfer — the new agent can go read it, and it'll be more current and accurate than your summary. Your job is the stuff that only lives in the conversation: decisions made and why, dead ends already ruled out, constraints and preferences the user stated out loud, and the current state of anything in progress. If the thing being handed off (a draft, an idea, a half-finished scene) only exists *in the conversation itself* and isn't saved anywhere, that content itself becomes something you have to state, not just point to — don't assume it's recoverable just because it feels like it should be.

## Process

1. **Pin down the task.** The user names it when invoking this skill ("review the diff," "continue the chapter," "keep debugging this"). If it's vague, use your judgment on scope rather than asking — a handoff prompt that's slightly too broad is still useful; stalling to ask isn't.

2. **Scan the conversation for what's task-relevant.** Most sessions wander — dead ends, tangents, meta-discussion, earlier drafts that got replaced. Almost none of that belongs in the handoff. Pull out only the decisions, constraints, and state that bear on the named task.

3. **Split what you found into "point at it" vs. "state it."** Anything that lives in a file, repo, doc, or URL: give a path or link, don't reproduce it. Anything that only exists because of this conversation: state it plainly, in your own words, not as a quote or transcript excerpt.

4. **Draft the prompt, task-first.** Lead with what the new agent should *do*, not a chronological story of how you got here. "We discussed X, then tried Y, then decided Z" is a narrative for a human; a fresh agent needs the current state, not the journey.

5. **Cut it down.** A wall of context is nearly as useless as no context — the important two sentences get buried in twenty unimportant ones. If a sentence doesn't change what the new agent would do, cut it.

6. **Check yourself for accuracy before handing it over.** Don't upgrade something tentative ("we might use Redis") into something settled ("uses Redis"). Don't invent plausible-sounding specifics you're not actually sure of — an under-specified handoff is recoverable (the new agent can ask or investigate), a confidently wrong one isn't.

## Shape of the output

Not a rigid template — adapt to the task — but most handoffs end up with some version of:

- **Task**: one or two sentences, stated as an instruction to the new agent.
- **Relevant background**: the decisions, rationale, and constraints that only exist in this conversation. Bullets, not prose paragraphs.
- **Where things are**: file paths, links, IDs — pointers, not reproductions.
- **Watch out for / open questions**: anything unresolved, uncertain, or likely to trip up someone encountering this fresh.

Skip any section that's empty for this task rather than padding it out.

## Format

Output as a single plain-text block the user can copy directly — no surrounding commentary before or after explaining what you did, since that's not part of the prompt they're going to paste. A short one-line intro like "Here's a handoff prompt for that:" is fine, but the block itself should be self-contained and ready to use as-is.

## Example

Task: "review this diff." The conversation established that caching validation results was considered and rejected for staleness risk, and that the diff lives at `feature/session-fix.diff`.

```
Task: Review the diff at feature/session-fix.diff, which fixes a session-expiry race condition.

Relevant background:
- Caching validation results was considered and rejected — introduces staleness risk that outweighs the perf gain here. Don't suggest it as an improvement.
- The fix intentionally keeps the retry logic synchronous; an earlier async version caused duplicate token refreshes under load.

Where things are:
- Diff: feature/session-fix.diff
- Original bug report: issue #482

Watch out for:
- The mobile client hits the same endpoint but wasn't part of this fix — flag if the diff touches shared code paths that could affect it.
```

## Common ways this goes wrong

- **Chronological recap.** "First we tried X, then discovered Y, then pivoted to Z" reads like a story, not a briefing. State where things stand now.
- **Dumping everything you know.** More context isn't safer — it costs the new agent time and attention to sort signal from noise, and important constraints get lost in restated boilerplate.
- **Reproducing what's discoverable.** If it's in the file, don't retype it — point at it.
- **False confidence.** Stating an assumption as a fact is worse than leaving it out, because the new agent won't know to double check it.
