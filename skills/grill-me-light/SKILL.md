---
name: grill-me-light
description: Bounded interview for stress-testing a plan, design, architecture, implementation approach, product idea, or vague prompt before building. Use when the user asks to be grilled, wants Matt Pocock-style alignment with fewer questions, asks for a capped or lightweight grilling session, or wants assumptions, decisions, and risks clarified without slowing development.
---

# Grill Me Light

## Overview

Sharpen the user's plan through a short, high-signal interview. Preserve the original grilling spirit: reach shared understanding before building, but optimize for development momentum.

## Core Rules

- Use five question turns as the default interview budget.
- Ask no more than ten question turns unless the user explicitly requests a deeper grilling session.
- Ask one question turn at a time, then wait for the user's answer.
- Include your recommended answer with each question.
- Ask fewer than five questions when enough is already clear.
- Do not ask questions that can be answered by inspecting files, running commands, or reading provided context. Investigate first.
- Do not ask questions whose answers would not change the plan. State a reasonable assumption instead.
- Favor decisive defaults. When the user accepts a recommendation or does not care, proceed with that default.

## Question Budget

Track question count explicitly in your reasoning. A "question turn" is one message that asks the user for a decision or missing fact.

Questions one through five are the normal budget. Continue with questions six through ten only when all are true:

- The missing answer materially changes architecture, scope, data model, security, cost, migration strategy, or user-facing behavior.
- A wrong assumption would be expensive to unwind.
- You state why extending the interview is worthwhile before asking question six.

Make the checkpoint and question six a single turn so the checkpoint does not add another interaction. Use this shape:

```text
I have reached the default five-question budget. I recommend continuing because <reason>. You can answer the next question or tell me to proceed with the current assumptions.

Question 6/10: <question>
Options:
- A. <option and consequence>
- B. <option and consequence>
Recommended answer: <recommendation>
```

After question six, continue only while each remaining question meets the same materiality and unwind-cost criteria. Stop at ten and proceed with stated assumptions unless the user explicitly asks for deeper grilling.

## Workflow

1. Restate the user's plan or request in one compact paragraph.
2. Identify the highest-risk uncertainty that would most change execution.
3. Ask the next best question with a recommended answer.
4. After each user answer, update the working plan and decide whether another question is still worth asking.
5. Stop when the remaining unknowns can be handled with assumptions. After five question turns, continue only under the extension criteria; stop at ten unless the user explicitly asks for deeper grilling.
6. Produce an alignment brief, then offer the post-brief options.

## Question Style

Use concise, concrete questions:

- Prefer tradeoffs over open-ended prompts.
- Offer two or three options when that helps the user answer quickly.
- Recommend one option and explain the consequence in one sentence.
- Keep each question focused on one decision.
- Avoid re-asking resolved questions in different words.

Example:

```text
Question 2/5: Should this be optimized for a quick local tool or a reusable team workflow?

Options:
- A. Quick local tool: fastest to build, but future runs may drift.
- B. Reusable team workflow: slightly more structure now, more consistent later.

Recommended answer: B. Reusable team workflow, because the naming and validation rules keep future runs consistent with little extra cost.
```

## Alignment Brief

When the interview is done, summarize:

- Decisions made.
- Assumptions you will carry forward.
- Remaining risks, if any.
- Concrete next action.

After the brief, present exactly these options and wait for the user's choice:

```text
Post-brief options:
1. Continue into execution now.
2. Enter plan mode and create an implementation plan from this grilling session.
3. Create a markdown handoff artifact and hand the task to another agent with fresh context.
```

Recommend one option based on the situation:

- Recommend option 1 when the task is clear, low-risk, and ready to build.
- Recommend option 2 when execution still needs sequencing, milestones, risk reduction, or approval.
- Recommend option 3 when the work should move to a fresh context, another agent, or a separate thread.

## Handoff Artifact

If the user chooses handoff, create a markdown file that lets another agent resume as smoothly as possible without reading the full conversation. Optimize for transfer fidelity and operational continuity, not brevity. Include enough context for the next agent to understand the work, preserve the user's intent, and continue as if it had participated in the grilling session.

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

Prefer precise details over a short summary when precision would help the next agent avoid re-discovering context or accidentally changing direction.

After creating the artifact, provide the markdown artifact path and a ready-to-send handoff prompt.

## Escape Hatches

If the user says "just proceed", "use your judgment", "no more questions", or similar, stop interviewing and act on the best available assumptions. If the user asks for a deeper grilling session, you may relax the cap, but continue to make every question earn its place.
