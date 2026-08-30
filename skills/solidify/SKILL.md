---
name: solidify
description: An evidence-led challenge of an already articulated request, goal brief, plan, or design that tests assumptions, resolves material tradeoffs, and makes its goal and normative constraints decision-ready.
disable-model-invocation: true
---

Start from the user's existing articulation and subject it to evidence-led challenge. Bring relevant domain knowledge together with discovered facts to expose unsupported assumptions, contradictions, implications, and material tradeoffs. Do not repeat settled goal discovery unless new evidence would materially change or invalidate a prior decision.

Sharpen only the normative "how": architectural and ownership boundaries, required tradeoffs, compatibility or migration commitments, risk and permission constraints, and verification obligations. Do not turn the artifact into a file-by-file implementation plan or task sequence; leave tactical choices to the implementing agent unless a choice is itself part of the accepted contract.

Rank the open decisions by expected value — how much the answer would change what you'd do, weighted by how unsure it is — and ask the highest-value one first. Ask one question at a time and wait.

Offer two or three concise, distinct options when they would make the decision easier. Put your recommended option first. When options would be artificial, ask the question directly and include your recommended answer. Each answer reshapes the picture, so re-rank what's left before the next question.

Finding discoverable _facts_ and developing informed options is your job, not the user's. Before asking a question, aggressively inspect available sources (the codebase, filesystem, tools, etc.) that could materially affect how you frame it; don't ask the user for facts you can find yourself. Don't merely collect facts or use them to frame questions; synthesize them with your domain knowledge into the challenges, options, and recommendations you put to the user. Asking a question without thorough fact-finding is dangerous: it can steer the conversation in the wrong direction. A question grounded in deep domain understanding can instead add substantial value. The _decisions_ are the user's: put each to them and wait.

Stop when the surviving goal and normative constraints can withstand the discovered evidence, and no unresolved question would materially change the intended outcome or acceptable solution space. A complete implementation plan is not required.

When you stop, give the user a short recap: the decisions we settled and, if any questions were deliberately left unasked, why you skipped each and the assumption you'll use in its place. Never skip questions silently.

Don't act until the user confirms the recap, assumptions included.

When substantial downstream work will follow, hand the confirmed decisions to the repository's canonical change lifecycle. Persist only the accepted goal, normative approach decisions and rationale, constraints, assumptions, and acceptance criteria; leave tactical planning to the implementing agent. If no repository lifecycle authority exists, provide a self-contained handoff and obtain explicit direction before creating repository artifacts.
