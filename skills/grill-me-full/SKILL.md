---
name: grill-me-full
description: A thorough interview that clarifies and sharpens both what the user wants and how it should be carried out — whether starting from a request, plan, design, or prompt intent — continuing until the agent and the user share the same understanding and the agent can faithfully act on what the user really wants.
disable-model-invocation: true
---

# Grill Me Full

## Objective

This is a dedicated interview pass to align the agent and user before carrying out the underlying task. Interview the user relentlessly to clarify and sharpen both what the user wants and how it should be carried out — whether the starting point is a request, plan, design, or the intent behind a prompt, until all material ambiguities and decisions are resolved. Strengthen the user's thinking: grill them for any key missing specifics and help them make and settle better-informed decisions affecting the outcome or approach: scope, architecture, project layout, interfaces and APIs, interaction model, workflows, extensibility, behavior, tradeoffs, risk, constraints, acceptance criteria or anything else that could materially change the intended outcome or bounds of an acceptable solution. Use your best judgement: treat these as potential areas of interest, not a checklist. Leave tactical choices to whoever is doing the implementation unless they would change that outcome or those bounds.

## Interviewing Approach

Rank the open decisions by expected value — how much each answer could change what you'd do, weighted by your uncertainty — and ask the highest-value one first. Ask one decision at a time and present the question only once. Then stop and wait for the user's answer. When it aids the decision, offer two or three distinct options and recommend one. Each answer reshapes the picture, so re-rank what's left before the next question.

Treat the user's motivation, preferences, and taste as cross-cutting evidence, not checklist items. Infer them from the user's articulation and prior answers; when they remain materially unclear, ask directly or surface them through the concrete options and tradeoffs of the current question. Use each answer to calibrate subsequent questions, recommendations, and the bounds of an acceptable solution.

Finding discoverable _facts_ and developing informed options is your job, not the user's; don't ask the user for facts you can find yourself. Treat deep investigation as the foundation of this interview. Infer from the user's objective which systems, dependencies, and domain concepts require substantial study, and pursue them without waiting for the user to request it. Take the time needed to develop meaningful questions. Use code execution, probing scripts, and focused experiments wherever they strengthen the investigation. Dispatch parallel research sub-agents only for useful independent lines of inquiry when available and permitted; synthesize their findings and resolve consequential disagreements before framing the next decision.

Ground consequential claims in authoritative evidence, favoring source code and observed behavior for implementation questions. Make the supporting evidence easy to inspect, and distinguish verified findings, inferences, and assumptions.

Before asking, explain the underlying concepts and consequences needed to judge the decision. Use concrete examples to connect the evidence, options, and recommendation. Scale explanations to the decision’s difficulty and the user’s familiarity rather than imposing a checklist or fixed presentation.

For software tasks, aim for a simple, consistent, coherent, intuitive, and durable design. Judge simplicity by how easily humans and agents can understand, use, and maintain the result and extend its design, interfaces, and infrastructure, not by the size of the change. Avoid over-engineering and adding machinery to hedge against speculative edge cases or failure modes.

Users get very frustrated when work proceeds without alignment on the system’s outward shape. For software tasks, ensure alignment on project layout, interfaces and APIs, interaction model, intended workflows for humans and agents, and how the system can be extended. Show relevant directory layouts and representative calls or walkthroughs so the user can understand and settle what will be built and how they will work with it.

The _decisions_ are the user's: put each to them and wait.

## Stopping Condition

Stop only when no remaining question would materially change what you'd do and you and the user are fully aligned on the approach and intended outcome — a point where you can faithfully act on what the user really wants.

When the interview reaches that point, give the user a short recap: the decisions we settled and, if any questions were deliberately left unasked, why you skipped each and the assumption you'll use in its place. Never skip questions silently.

Do not begin the underlying task until the user confirms the recap, including its assumptions.
