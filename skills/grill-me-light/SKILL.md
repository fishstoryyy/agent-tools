---
name: grill-me-light
description: Bounded interview for stress-testing a plan, design, architecture, implementation approach, product idea, or vague prompt before building. Use when the user asks to be grilled, wants Matt Pocock-style alignment with fewer questions, asks for a capped or lightweight grilling session, or wants assumptions, decisions, and risks clarified without slowing development.
disable-model-invocation: true
---

# Grill Me Light

## Overview

Sharpen the user's plan through a short, high-signal interview. Preserve the original grilling spirit: reach shared understanding before building, but optimize for development momentum.

## Core Rules

- Use six question turns as the default interview budget.
- Ask no more than twelve question turns unless the user explicitly requests a deeper grilling session.
- Ask one question turn at a time, then wait for the user's answer.
- Ask every interview question and post-brief choice through the runtime's native structured user-question tool when one is available in the current mode, such as `AskUserQuestion`, `ask`, or `request_user_input`. Follow that tool's schema and UI conventions, but submit exactly one question even when it supports batching. Otherwise ask in normal conversation; do not change modes solely to gain a question tool.
- Include your recommended answer with each question.
- Ask fewer than six questions when enough is already clear.
- Do not ask questions that can be answered by inspecting files, running commands, or reading provided context. Investigate first.
- Do not ask questions whose answers would not change the plan. State a reasonable assumption instead.
- Favor decisive defaults.

## Question Budget

Track question count across turns. A "question turn" is one message that asks the user for a decision or missing fact.

Questions one through six are the normal budget. Continue with questions seven through twelve only when all are true:

- The missing answer materially changes architecture, scope, data model, security, cost, migration strategy, or user-facing behavior.
- A wrong assumption would be expensive to unwind.
- You state why extending the interview is worthwhile before asking question seven.

Make the checkpoint and question seven a single turn so the checkpoint does not add another interaction. Put the checkpoint in the native question tool's prompt or description when its schema supports that; otherwise state it immediately before calling the tool. Use this content:

```text
I have reached the default six-question budget. I recommend continuing because <reason>. You can answer the next question or tell me to proceed with the current assumptions.

Question 7: <question>
Recommended answer: <recommendation>
```

After question seven, continue only while each remaining question meets the same materiality and unwind-cost criteria. Stop at twelve and proceed with stated assumptions unless the user explicitly asks for deeper grilling.

## Working Ledger

Maintain a compact working ledger throughout the interview:

- Objective and observable success criteria.
- Confirmed decisions and important rationale.
- Discovered facts and their sources.
- Assumptions and defaults.
- Constraints and non-goals.
- Unresolved decisions, ranked by expected impact.

Record a choice as confirmed when the user accepts a recommendation or explicitly delegates that decision.

Do not print the full ledger after every answer. Treat partial answers as resolving only what they explicitly settle. When new information conflicts with an earlier decision, surface the conflict instead of silently replacing either one.

## Workflow

1. Restate the user's plan or request in one compact paragraph.
2. Identify the unresolved decision with the highest expected value: the one whose answer is most likely to change scope, user-visible behavior, architecture, or an expensive-to-reverse choice. When the objective or success criteria are unclear, resolve those before implementation details.
3. Ask the next best question with a recommended answer.
4. After each user answer, reconcile the working ledger and decide whether another question is still worth asking.
5. Stop when the remaining unknowns can be handled with assumptions. After six question turns, continue only under the extension criteria; stop at twelve unless the user explicitly asks for deeper grilling.
6. Produce an alignment brief, then offer the post-brief options.

## Question Style

Use concise, concrete questions:

- Prefer tradeoffs over open-ended prompts.
- Offer two or three options when that helps the user answer quickly.
- Recommend one option and explain the consequence in one sentence.
- Base the recommendation on the user's stated objective and priorities. Label preference-sensitive recommendations as judgment calls instead of presenting them as facts.
- Keep each question focused on one decision.
- Make it easy for the user to reject the framing or supply an option you missed.
- When using a native question tool, put the recommended option first and mark it as recommended when the tool supports that.

When no native question tool is available, use this shape:

```text
Question 2: Should this be optimized for a quick local tool or a reusable team workflow?

Options:
- A. Quick local tool: fastest to build, but future runs may drift.
- B. Reusable team workflow: slightly more structure now, more consistent later.

Recommended answer: B. Reusable team workflow, because the naming and validation rules keep future runs consistent with little extra cost.
If neither fits, tell me what constraint the framing misses.
```

## Alignment Brief

When the interview is done, summarize the following, omitting empty sections:

- Objective and observable success criteria.
- In-scope work, non-goals, and constraints.
- Confirmed decisions and important rationale.
- Verified facts and relevant evidence.
- Assumptions and defaults, clearly labeled.
- Remaining risks or open questions and their likely impact.
- Immediate next action and its completion condition.

Treat this brief as the working contract for subsequent planning or execution. Revise it when new evidence or user direction materially changes it.

After the brief, present these options through the native question tool when available, then wait for the user's choice:

```text
Post-brief options:
1. Continue into execution within the agreed scope.
2. Prepare a markdown handoff for another agent or session.
3. Stop here with the alignment brief.
```

Recommend one option based on the situation:

- Recommend option 1 when the task is clear, low-risk, and ready to build.
- Recommend option 2 when the work should move to a fresh context, another agent, or a separate thread.
- Recommend option 3 when clarification was the deliverable or the user does not want to continue yet.

## Handoff Artifact

If the user chooses handoff, create a markdown file that lets another agent resume without reading the full conversation. Use the user's requested path; otherwise write `./temp/HANDOFF.md` from the workspace or project root. If the target already contains unrelated content, ask before overwriting it.

Optimize for transfer fidelity and operational continuity, not brevity. Include enough context for the next agent to preserve the user's intent and continue as if it had participated in the grilling session.

Include (where relevant):

- Task objective.
- Current status.
- User intent and preferences.
- Decisions from the grilling session.
- Decision rationale and important tradeoffs.
- Assumptions to preserve.
- Rejected options or paths not taken.
- Relevant files, commands, links, or artifacts.
- Constraints, risks, and non-goals.
- Recommended next steps, including the immediate next action.
- Open questions for the next agent, if any.

Separate verified facts from assumptions and never imply that an unperformed check ran. Prefer precise details over a short summary when precision would help the next agent avoid re-discovering context or accidentally changing direction.

After creating the artifact, read it back, then provide the markdown artifact path and a ready-to-send handoff prompt.

## Escape Hatches

If the user asks to stop interviewing, produce the alignment brief immediately. If the user explicitly asks to proceed, continue within the agreed scope after the brief without requiring another choice. If the user asks for a deeper grilling session, you may relax the cap, but continue to make every question earn its place.
