---
name: specify-to-spec
description: Interview the user until a task and its execution design are fully specified, exempting only answers that follow unambiguously from established context. Use when explicitly requested to produce a complete specification before execution.
disable-model-invocation: true
---

# Specify To Spec

Interview the user until the underlying task and execution design are fully specified. This is a dedicated specification pass: investigate and write the specification, but do not execute the underlying task.

## Investigate and interview

Build on the session's context. Investigate available evidence before asking; discover facts yourself where possible. Distinguish verified facts, user decisions, and inferred answers. Surface contradictions and resolve them through investigation or further questions.

Build the user's understanding throughout the interview. For tasks that create or change files, show the proposed directory tree and explain each planned file or script's purpose and relationships. Walk through representative user interactions, covering entry points, inputs, actions, outputs, and feedback as applicable. Use these concrete walkthroughs to ground questions, explain tradeoffs, and settle unresolved choices about the files, layout, and interaction flows. Explain choices already established by context without reopening them unnecessarily. Scale the detail to the task and the user's familiarity.

Strengthen the user's thinking and help them make better decisions. Think through the task on their behalf: examine the underlying goal, challenge weak premises, surface overlooked consequences, and recommend better approaches grounded in evidence. Explain why a recommendation serves their goal and what it costs; let the user decide whether to include related improvements.

Short examples of this approach, when supported by the investigation:

- "This change uses ABC, whose duplicated rules caused the inconsistency. I recommend consolidating them now to prevent recurrence; should we include that?"
- "Your goal is faster lookup. Improving search may achieve it without a new dashboard; I recommend trying that first. Would that meet your need?"
- "Automatic retries could duplicate this action. I recommend a duplicate-prevention check despite the added work; should we include it?"

Ask one unresolved decision at a time, prioritizing the answer that would most shape the remaining specification. Explain relevant tradeoffs and offer grounded options and a recommendation when useful. Present the question once, then wait for the user's answer and reassess what remains.

Only skip an unanswered question when its answer follows unambiguously from established context. Record each inferred answer and its basis. A likely preference, conventional default, or minor implementation detail is not an exemption. Recommendations remain proposals until the user settles them; uncertainty or silence does not settle a decision.

Specify intent, scope, expected behavior, interfaces and interaction flows, constraints, implementation choices, execution steps, and failure handling as applicable. Define observable acceptance criteria and how each will be verified. Follow dependencies between decisions and revisit earlier answers when new evidence exposes a conflict. Do not leave execution-design choices to the implementer merely because they are tactical.

Continue without a question budget. Once every task and execution-design decision is either explicitly settled by the user or follows unambiguously from established context, end the interview and write the specification. If any decision remains unresolved, continue investigating or interviewing.

## Write and approve

Write a self-contained specification to `docs/changes/YYYY-MM-DD-<slug>/spec.md` under the active workspace root, using the workspace's local date and a concise kebab-case task slug. Create missing directories.

Include the intended outcome, requirements and boundaries, execution design and steps (including the agreed file layout, file/script responsibilities, and user interaction flows), acceptance and verification criteria, and any inferred answers with their basis. Organize these to fit the task, omitting inapplicable sections. Preserve settled decisions without inventing requirements or leaving placeholders for unresolved choices.

Ask the user to review the file. Discuss objections, reopen affected decisions, and revise until the user explicitly approves it. Then stop. Do not execute the underlying task, stage, or commit the specification.
