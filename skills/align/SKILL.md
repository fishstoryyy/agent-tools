---
name: align
description: Settle every material decision or ambiguity with the user before acting on a request, while strengthening their thinking and integrating motivation, preferences, and taste. Use when the user wants a full decision-ready alignment before whoever acts on the result.
disable-model-invocation: true
---

This is a dedicated investigation and interview pass to align the agent and user before carrying out the underlying task. Investigate the available sources thoroughly and interview the user relentlessly to clarify intent and settle every decision or ambiguity that could materially change or sharpen the intended outcome or acceptable approach. Be mindful of cognitive debt: the agent can produce changes faster than the user can understand them, leaving costly catch-up during review and maintenance. Help the user build enough of a mental model to connect the proposed changes to the problem, understand consequential tradeoffs, and judge the result.

Assume the request’s why, what, and how may not yet be fully thought through. Strengthen the user’s thinking: think through the task on their behalf, grill them for any key missing specifics, and help them make better-informed decisions. Surface hidden assumptions, contradictions, and material tradeoffs. Treat the user’s motivation, preferences, and taste as cross-cutting evidence that shapes materiality, questions, options, and recommendations.

Build on relevant session context. Treat deep investigation as the foundation of this interview. Infer from the user's objective which systems, dependencies, and domain concepts require substantial study, and pursue them without waiting for the user to request it. Take the time needed to develop meaningful questions. Use code execution, probing scripts, and focused experiments wherever they strengthen the investigation. Dispatch parallel research sub-agents freely for useful independent lines of inquiry when available and permitted; synthesize their findings and resolve consequential disagreements before framing the next decision.

Ground consequential claims in authoritative evidence, favoring source code and observed behavior for implementation questions. Make the supporting evidence easy to inspect, and distinguish verified findings, inferences, and assumptions.

Before asking, explain the underlying concepts and consequences needed to judge the decision. Use concrete examples to connect the evidence, options, and recommendation. Scale explanations to the decision’s difficulty and the user’s familiarity rather than imposing a checklist or fixed presentation.

For tasks involving files or scripts, show the relevant proposed directory layout and explain their responsibilities and relationships. Walk through representative user interactions so the user understands what will be built and how it will be used. Probe what humans and agents control and how they understand what happens. Use these walkthroughs throughout the interview to build familiarity and ground questions about material choices.

Ask one decision at a time and present the question only once. Then stop and wait for the user's answer. When it aids the decision, offer two or three grounded options and recommend one; leave non-material tactical choices to whoever acts on the result.

When no material decision or ambiguity remains, briefly recap the settled decisions and any assumptions that will guide the work. Carry forward any agreed needs for explanation or review so whoever executes can help the user assess the finished work. Do not act until the user confirms the recap.

If execution nevertheless reveals a significant conflict with settled decisions or an unresolved consequential choice, bring it back to the user before proceeding on that point. This is a fallback, not a reason to leave foreseeable decisions unsettled.
