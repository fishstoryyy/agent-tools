---
name: grill-the-goal
description: Interview the user to turn a vague or unscoped goal into a decision-ready brief by clarifying the relevant context, actors, sources, outcome, success evidence, tradeoffs, constraints, and unknowns before implementation planning. Use when the user has a fuzzy goal, an unscoped request, or asks to "grill the goal," "scope this," or "figure out what I actually want." Deliberately avoids implementation steps, architecture, and sequencing — pair with plan mode or grill-me afterward.
disable-model-invocation: true
---

# Grill the Goal

Interview the user relentlessly about what they actually want — not how to build it. Apply this whether the goal is a whole new product or a single feature in an existing system. Walk down each relevant branch until the goal is decision-ready. Infer what you can from the conversation and available materials, then let the user confirm or correct your working understanding.

## Rules

1. **Resolve one decision per turn.** Ask one focused question at a time. Never bundle unrelated decisions.
2. **Offer a working hypothesis.** When there is ambiguity, give 2-3 concrete choices, recommend one, and briefly explain the basis for the recommendation. Make it easy to reject the framing entirely. When there is only one sane answer, state it as an assumption and ask for confirmation instead of manufacturing false choices.
3. **Inspect available evidence before asking.** Check the conversation, codebase, and referenced materials for answers the user should not have to repeat. State the inference and its source, and ask for correction only when meaningful uncertainty remains.
4. **Stay off the "how."** Do not ask the user to choose implementation details such as architecture, libraries, data structures, or sequencing; use `/plan` or `grill-me` for that afterward. Goal-level questions about causality, adoption, measurement, ownership, source authority, and technical constraints are still in scope.
5. **Cover the relevant lenses, roughly in order:**
   - **Context and intent** — What happens today? What problem or opportunity motivates the goal? Why now, and what happens if nothing changes?
   - **Actors** — Who benefits, uses, approves, operates, maintains, or may be adversely affected? Whose definition of success governs, and whose behavior must change?
   - **Sources and materials** — Which codebases, documents, tickets, examples, datasets, or existing workflows are relevant? Record where each lives and whether it is a source of truth, background, constraint, example, or validation evidence. Note relevant versions, branches, or dates; establish precedence when sources conflict; and flag anything unavailable, stale, or incomplete. Inspect enough to clarify the goal, but defer exhaustive rule extraction to the next stage.
   - **Outcome and scope** — What observable state or behavior should change? What is included, explicitly excluded, and the minimum acceptable result?
   - **Success evidence** — What baseline, target, measurement method, time horizon, and guardrails establish success? What would make this a failure even if it technically runs or ships?
   - **Priorities and tradeoffs** — When desired qualities conflict, what wins? Which requirements are non-negotiable and which are preferences?
   - **Constraints and dependencies** — What must never happen? What limits, deadlines, obligations, integrations, people, or external systems are fixed or required?
   - **Assumptions and unknowns** — What must be true for the goal to make sense? Distinguish established facts, inferences, and decisions. Record what remains uncertain and what could invalidate or materially reshape the goal.
6. **Use relevance, not checklist completion.** Treat the lenses as prompts for judgment. Explore only lenses that could materially change the goal, its evaluation, or its boundaries. A lens may be resolved, explicitly not applicable, or left as a named unknown. Do not invent content merely to fill every section.
7. **Check for consistency before stopping.** Confirm that the outcome serves the stated actors and intent, success evidence is observable, priorities resolve likely tradeoffs, constraints do not contradict success, source authority and gaps are clear, and assumptions are not presented as facts.
8. **Stop when the goal is decision-ready.** Stop when material ambiguities are resolved, irrelevant lenses have been skipped, and remaining unknowns are explicitly recorded with their likely impact. Do not require every lens to contain content or manufacture extra questions.
9. **Close with a goal brief.** Recap the relevant context and intent, actors, outcome and scope, success evidence, priorities, constraints and dependencies, sources and materials, and assumptions or open questions. Omit inapplicable sections. For each source, include its location, role, authority, relevant version or date, and known gaps. Make the brief ready to hand to whatever does the actual planning or building.
