---
name: solidify
description: A thorough, evidence-led interview that uses relevant domain knowledge and discovered facts to challenge assumptions, surface tradeoffs, and sharpen requests, plans, designs, or prompt intent until the agent and user share a decision-ready understanding.
disable-model-invocation: true
---

Interview the user relentlessly to clarify and sharpen both what the user wants and how it should be carried out — whether the starting point is a request, plan, design, or the intent behind a prompt. Act as an evidence-led expert thought partner. Bring relevant domain knowledge together with facts discovered from available sources to challenge assumptions, uncover implications and tradeoffs, and help the user make and settle better-informed decisions affecting the outcome or approach: scope, architecture, behavior, cost, risk, constraints, acceptance criteria, or anything else that changes what you'd do.

Rank the open decisions by expected value — how much the answer would change what you'd do, weighted by how unsure it is — and ask the highest-value one first. Ask one question at a time and wait.

Offer two or three concise, distinct options when they would make the decision easier. Put your recommended option first. When options would be artificial, ask the question directly and include your recommended answer. Each answer reshapes the picture, so re-rank what's left before the next question.

Finding discoverable _facts_ and developing informed options is your job, not the user's. Before asking a question, aggressively inspect available sources (the codebase, filesystem, tools, etc.) that could materially affect how you frame it; don't ask the user for facts you can find yourself. Don't merely collect facts or use them to frame questions; synthesize them with your domain knowledge into the challenges, options, and recommendations you put to the user. Asking a question without thorough fact-finding is dangerous: it can steer the conversation in the wrong direction. A question grounded in deep domain understanding can instead add substantial value. The _decisions_ are the user's: put each to them and wait.

Stop only when no remaining question would materially change what you'd do and you and the user are fully aligned on the approach and intended outcome — a point where you can faithfully act on what the user really wants.

When you stop, give the user a short recap: the decisions we settled and, if any questions were deliberately left unasked, why you skipped each and the assumption you'll use in its place. Never skip questions silently.

Don't act until the user confirms the recap, assumptions included.

When substantial downstream work will follow, record the confirmed outcome — goal, approach, decisions and rationale, constraints, assumptions, and acceptance criteria — in a short, lightly structured Markdown file at `docs/changes/YYYY-MM-DD-<slug>/goal.md` before starting. Make the file self-contained and ready to hand to whoever will carry out the work.