---
name: budget-grill-me
description: A budgeted interview to sharpen the intent behind a prompt, plan, or design — at most 6 questions, highest-value first, stopping early once nothing more would change what the agent does.
disable-model-invocation: true
---

Interview me to sharpen what I'm asking for — a plan, a design, or the intent behind a prompt — but on a strict budget: **at most 6 questions**. Spend them where they matter most.

Rank the open decisions by expected value — how much the answer would change what you'd do, weighted by how unsure it is — and ask the highest-value one first. Ask one question at a time, with your recommended answer, and wait. Each answer reshapes the picture, so re-rank what's left before the next question.

If a *fact* can be found by exploring the environment (filesystem, tools, etc.), look it up rather than spending a question on it. The *decisions* are mine — put each to me and wait for my answer.

Stop the moment no remaining question would materially change what you'd do — don't spend the budget just because it's there. Six is the ceiling, not the target.

When you stop, give me a short recap: the decisions we settled, and the high-value questions you chose *not* to ask — each with the assumption you'll act on in its place. The budget skips questions; it must never skip them silently.

Don't act until I confirm the recap, assumptions included.
