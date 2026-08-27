---
name: grill-me-full
description: A thorough interview that clarifies and sharpens requests, plans, designs, or the intent behind prompts by asking the highest-value question first and continuing until further answers would not change the agent’s approach.
disable-model-invocation: true
---

Interview me relentlessly to clarify and sharpen what I’m asking for—a request, a plan, a design, or the intent behind a prompt—by adding needed specificity and improving key decisions.

Rank the open decisions by expected value — how much the answer would change what you'd do, weighted by how unsure it is — and ask the highest-value one first. Ask one question at a time and wait. Render every question through the runtime's native structured user-question tool when one is available; follow its schema and UI conventions, but submit exactly one question even when it supports batching. Otherwise ask in normal conversation.

Offer two or three concise, distinct options when they would make the decision easier. Put your recommended option first and mark it as recommended when the tool supports that. When options would be artificial, ask the question directly and include your recommended answer. Each answer reshapes the picture, so re-rank what's left before the next question.

Finding discoverable _facts_ is your job, not the user's. When a question needs a fact available from the environment (codebase, filesystem, tools, etc.), look it up aggressively rather than spending a question on it; don't ask the user for anything you could find yourself. The _decisions_ are the user's: put each to them and wait.

Stop when no remaining question would materially change what you'd do and you have reached a shared understanding with the user — a point where you can confidently act on what the user really wants.

When you stop, give me a short recap: the decisions we settled, and the high-value questions you chose *not* to ask (if any) — each with the assumption you'll act on in its place. Never skip questions silently.

Don't act until I confirm the recap, assumptions included.
