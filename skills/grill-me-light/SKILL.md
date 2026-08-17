---
name: grill-me-light
description: A budgeted interview to align intent and define evidence-backed acceptance criteria before execution — at most 10 questions, highest-value first, stopping early once nothing more would change what the agent does or how success will be validated. Use when the user asks for lightweight or capped grilling before an agent takes action.
disable-model-invocation: true
---

Interview me to sharpen what I'm asking for — a plan, a design, or the intent behind a prompt — but on a strict budget: **at most 10 questions**. Spend them where they matter most.

Rank the open decisions by expected value — how much the answer would change what you'd do, weighted by how unsure it is — and ask the highest-value one first. Ask one question at a time and wait. Render every question through the runtime's native structured user-question tool when one is available; follow its schema and UI conventions, but submit exactly one question even when it supports batching. Otherwise ask in normal conversation.

Offer two or three concise, distinct options when they would make the decision easier. Put your recommended option first and mark it as recommended when the tool supports that. When options would be artificial, ask the question directly and include your recommended answer. Each answer reshapes the picture, so re-rank what's left before the next question.

If a *fact* can be found by exploring the environment (filesystem, tools, etc.), look it up rather than spending a question on it. The *decisions* are mine — put each to me and wait for my answer.

Stop the moment no remaining question would materially change what you'd do — don't spend the budget just because it's there. Ten is the ceiling, not the target.

For any task that will create or change an artifact, system, or external state, use the same question budget to align on an acceptance contract before acting. Scale its rigor to the task's risk. Pure explanation or brainstorming can stop after intent alignment.

Inspect the available context, then draft the acceptance contract instead of making me author it from scratch. For every material outcome, define an observable pass condition, a validation method, and the concrete evidence you will report. Prefer automated tests when they can prove the outcome; otherwise use an explicit manual check or another inspectable form of evidence. Cover functional behavior, relevant failure cases, regressions, and material nonfunctional risks as the task requires.

Rank intent gaps and acceptance gaps together within the ten-question ceiling. Grill me only on gaps or tradeoffs whose answers would materially change the work or its validation. Put any consequential gap you do not ask about into the recap as an explicit assumption.

When you stop, give me a short recap: the decisions we settled, and the high-value questions you chose *not* to ask — each with the assumption you'll act on in its place. The budget skips questions; it must never skip them silently.

For an execution task, include the acceptance contract in that recap so my confirmation covers both what you will do and how you will establish that it works.

If a material criterion cannot be conclusively validated, identify the validation gap and residual risk before acting. Proceed only after I explicitly accept that risk, and never report that criterion or the work as fully validated.

Don't act until I confirm the recap, assumptions included.

After execution, report every agreed criterion with its validation method, result, and concrete evidence, such as test commands and outputs, screenshots, or manual-check findings. Mark anything unverified. Treat passing validation as review against the confirmed acceptance contract, not as proof that the work is defect-free or equivalent to traditional line-by-line human review.
