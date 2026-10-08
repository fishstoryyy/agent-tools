---
name: specify-to-spec
description: Interview the user to settle consequential task and execution-design decisions, resolve routine implementation details, and write a complete specification for approval. Use when explicitly requested to produce a complete specification before execution.
disable-model-invocation: true
---

# Specify To Spec

Interview the user to settle consequential decisions about the underlying task and execution design, and resolve routine implementation details yourself. This is a dedicated specification pass: investigate and write the complete specification, but do not execute the underlying task.

## Investigate and interview

Build on the session's context. Investigate available evidence before asking; discover facts yourself where possible. Distinguish verified facts, user decisions, and inferred answers. Surface contradictions and resolve them through investigation or further questions.

For software tasks, aim for a simple, consistent, coherent, intuitive, and durable design. Judge simplicity by how easily humans and agents can understand, use, and maintain the result and extend its design, interfaces, and infrastructure, not by the size of the change. Avoid over-engineering and adding machinery to hedge against speculative edge cases or failure modes.

Build the user's understanding throughout the interview. Aim for a shared mental model of the system’s visible shape. For tasks that create or change files, show the proposed directory tree and explain each planned file or script's purpose and relationships. Show the relevant interfaces, including APIs, and walk through representative workflows and user interactions. Use these concrete walkthroughs to ground questions, explain tradeoffs, and settle unresolved choices about the files, layout, and interaction flows. Explain choices already established by context without reopening them unnecessarily. Scale the detail to the task and the user's familiarity.

Strengthen the user's thinking and help them make better decisions. Think through the task on their behalf: examine the underlying goal, challenge weak premises, surface overlooked consequences, and recommend better approaches grounded in evidence. Explain why a recommendation serves their goal and what it costs; let the user decide whether to include related improvements.

Short examples of this approach, when supported by the investigation:

- "This change uses ABC, whose duplicated rules caused the inconsistency. I recommend consolidating them now to prevent recurrence; should we include that?"
- "Your goal is faster lookup. Improving search may achieve it without a new dashboard; I recommend trying that first. Would that meet your need?"
- "Automatic retries could duplicate this action. I recommend a duplicate-prevention check despite the added work; should we include it?"

Ask one unresolved decision requiring the user's judgment at a time, prioritizing the answer that would most shape the remaining specification. Explain relevant tradeoffs and offer grounded options and a recommendation when useful. Present a concrete recommended design at a level the user can meaningfully assess. Explain its supporting details without turning each into a separate question unless it presents an independent consequential choice. Present the question once, then wait for the user's answer and reassess what remains.

Ask the user about unresolved choices that could materially affect the intended outcome, observable behavior, constraints, or consequential tradeoffs. Resolve routine implementation details yourself using the established direction, available evidence, and repository conventions. A choice being technical or small does not make it routine; ask when reasonable alternatives have materially different consequences. Distinguish agent-selected details from user decisions and inferred answers in the specification.

Specify intent, scope, expected behavior, interfaces and interaction flows, constraints, implementation choices, execution steps, and failure handling as applicable. Define observable acceptance criteria and how each will be verified. Follow dependencies between decisions and revisit earlier answers when new evidence exposes a conflict. Resolve and document routine execution-design choices yourself rather than leaving them to the implementer.

Continue until no unresolved choice requires the user's judgment and you can write a complete, coherent specification. Resolve remaining routine details and include them in the draft for review. If doing so reveals a consequential unresolved choice, return to the interview.

## Write and approve

Write a self-contained specification to `docs/changes/YYYY-MM-DD-<slug>/spec.md` under the active workspace root, using the workspace's local date and a concise kebab-case task slug. Create missing directories.

Include the intended outcome, requirements and boundaries, execution design and steps (including the proposed file layout, file/script responsibilities, interfaces, workflows, and user interaction flows), acceptance and verification criteria, and any inferred answers or agent-selected implementation choices with their basis. Organize these to fit the task, omitting inapplicable sections. Preserve settled decisions without inventing requirements or leaving placeholders for unresolved choices.

Ask the user to review the file. Discuss objections, reopen affected decisions, and revise until the user explicitly approves it. Then stop. Do not execute the underlying task, stage, or commit the specification.
