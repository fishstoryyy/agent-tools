---
name: budget-grill-me
description: A budgeted interview to sharpen the intent behind a prompt, plan, or design — at most 6 questions, highest-value first, stopping early once nothing more would change what the agent does.
disable-model-invocation: true
---

Interview me to sharpen what I'm asking for — a plan, a design, or the intent behind a prompt — but on a strict budget: **at most 6 questions**. Spend them where they matter most.

Rank the open decisions by expected value — how much the answer would change what you'd do, weighted by how unsure it is — and ask the highest-value one first. Ask one question at a time and wait. Render every question through the runtime's native structured user-question tool when one is available; follow its schema and UI conventions, but submit exactly one question even when it supports batching. Otherwise ask in normal conversation.

Offer two or three concise, distinct options when they would make the decision easier. Put your recommended option first. When options would be artificial, ask the question directly and include your recommended answer. Each answer reshapes the picture, so re-rank what's left before the next question.

Finding discoverable _facts_ and developing informed options is your job, not mine. Before asking a question, aggressively inspect available sources (the codebase, filesystem, tools, etc.) that could materially affect how you frame it; don't ask me for facts you can find yourself. Asking a question without thorough fact-finding is dangerous: it can steer the conversation in the wrong direction. A question grounded in deep domain understanding can instead add substantial value. The _decisions_ are mine: put each to me and wait.

Stop the moment no remaining question would materially change what you'd do — don't spend the budget just because it's there. Six is the ceiling, not the target.

When you stop, give me a short recap: the decisions we settled, and the high-value questions you chose *not* to ask and why — each with the assumption you'll act on in its place. The budget skips questions; it must never skip them silently.

Don't act until I confirm the recap, assumptions included.
