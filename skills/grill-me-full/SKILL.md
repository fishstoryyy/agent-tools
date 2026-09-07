---
name: grill-me-full
description: A thorough interview that clarifies and sharpens both what the user wants and how it should be carried out — whether starting from a request, plan, design, or prompt intent — continuing until the agent and the user share the same understanding and the agent can faithfully act on what the user really wants.
disable-model-invocation: true
---

# Grill Me Full

## Objective

This is a dedicated interview pass to align the agent and user before carrying out the underlying task. Interview the user relentlessly to clarify and sharpen both what the user wants and how it should be carried out — whether the starting point is a request, plan, design, or the intent behind a prompt, until all material ambiguities and decisions are resolved. Strengthen the user's thinking: grill them for any key missing specifics and help them make and settle better-informed decisions affecting the outcome or approach: scope, architecture, behavior, tradeoffs, risk, constraints, acceptance criteria or anything else that could materially change the intended outcome or bounds of an acceptable solution. Use your best judgement: treat these as potential areas of interest, not a checklist. Leave tactical choices to whoever is doing the implementation unless they would change that outcome or those bounds.

Remember that the user may also be finding their footing through this conversation—building familiarity with what will happen on their behalf, and confidence in letting it happen.

## Interviewing Approach

Rank the open decisions by expected value — how much each answer could change what you'd do, weighted by your uncertainty — and ask the highest-value one first. Ask one decision at a time and present the question only once. Then stop and wait for the user's answer.

Offer two or three concise, distinct options when they would make the decision easier. Put your recommended option first and briefly explain why. When options would be artificial, ask the question directly and include your recommended answer. Each answer reshapes the picture, so re-rank what's left before the next question.

Treat the user's motivation, preferences, and taste as cross-cutting evidence, not checklist items. Infer them from the user's articulation and prior answers; when they remain materially unclear, ask directly or surface them through the concrete options and tradeoffs of the current question. Use each answer to calibrate subsequent questions, recommendations, and the bounds of an acceptable solution.

Finding discoverable _facts_ and developing informed options is your job, not the user's. Before asking a question, aggressively inspect available sources (the codebase, filesystem, tools, etc.) that could materially affect how you frame it; don't ask the user for facts you can find yourself. Asking a question without thorough fact-finding is dangerous: it can steer the conversation in the wrong direction. A question grounded in deep domain understanding can instead add substantial value. The _decisions_ are the user's: put each to them and wait.

## Stopping Condition

Stop only when no remaining question would materially change what you'd do and you and the user are fully aligned on the approach and intended outcome — a point where you can faithfully act on what the user really wants.

When the interview reaches that point, give the user a short recap: the decisions we settled and, if any questions were deliberately left unasked, why you skipped each and the assumption you'll use in its place. Never skip questions silently.

Do not begin the underlying task until the user confirms the recap, including its assumptions.
