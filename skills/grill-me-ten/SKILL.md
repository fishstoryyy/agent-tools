---
name: grill-me-ten
description: A budgeted interview that clarifies and sharpens requests, plans, designs, or the intent behind prompts by adding needed specificity and improving key decisions—at most 10 high-value questions, stopping early when further answers would not change the agent’s approach.
disable-model-invocation: true
---

Interview me to clarify and sharpen what I’m asking for—a request, a plan, a design, or the intent behind a prompt—by adding needed specificity and improving key decisions. Use a budget: **at most 10 questions**. Spend them where they matter most.

Rank the open decisions by expected value — how much the answer would change what you'd do, weighted by how unsure it is — and ask the highest-value one first. Ask one question at a time and wait. Render every question through the runtime's native structured user-question tool when one is available; follow its schema and UI conventions, but submit exactly one question even when it supports batching. Otherwise ask in normal conversation.

Offer two or three concise, distinct options when they would make the decision easier. Put your recommended option first. When options would be artificial, ask the question directly and include your recommended answer. Each answer reshapes the picture, so re-rank what's left before the next question.

Finding discoverable _facts_ and developing informed options is your job, not mine. Before asking a question, aggressively inspect available sources (the codebase, filesystem, tools, etc.) that could materially affect how you frame it; don't ask me for facts you can find yourself. Asking a question without thorough fact-finding is dangerous: it can steer the conversation in the wrong direction. A question grounded in deep domain understanding can instead add substantial value. The _decisions_ are mine: put each to me and wait.

Stop the moment no remaining question would materially change what you'd do.

When you stop, give me a short recap: the decisions we settled, and the high-value questions you chose *not* to ask and why — each with the assumption you'll act on in its place. The budget skips questions; it must never skip them silently.

Don't act until I confirm the recap, assumptions included.
