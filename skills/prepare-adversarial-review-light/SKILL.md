---
name: prepare-adversarial-review-light
description: Create a context-rich markdown brief and ready-to-send prompt for an independent adversarial review of work produced in the current session, including plans, analyses, code, strategy research, infrastructure, or prior reviews. Use when handing work to a fresh reviewer or third-line audit agent who needs the conversation's decisions, evidence, resources, and unresolved risks without replaying the session.
---

# Prepare Adversarial Review Light

Prepare a fresh reviewer to understand the work as though they had followed the session and still evaluate it independently.

## Instructions

1. Reconstruct the relevant context from the conversation and inspect the current workspace as needed. Do not ask the user to repeat available information.
2. Identify the review target and its current state. Capture the objective, user intent, decisions and rationale, assumptions, constraints, non-goals, rejected paths, and unresolved questions that affect evaluation.
3. Give the reviewer an operational trail to the evidence: exact file paths, links, commits, commands, tests and results, data or source material, and other artifacts. Verify references when practical; never imply that unperformed validation occurred.
4. Separate evidence and established facts from assumptions, interpretations, and incumbent conclusions. Include known failures and unresolved uncertainties, but do not preselect criticism, defend the work, or suggest a verdict.
5. Create a markdown artifact at the user's requested path, or `adversarial-review-brief.md` near the reviewed work when no path is given. Use whatever structure communicates the context naturally. Omit irrelevant topics and avoid ceremonial sections, fixed templates, and forced brevity.
6. Generate a self-contained, ready-to-send prompt that points to the artifact and review target. Tell the new agent to treat the brief as orientation rather than authority, establish its own review criteria and challenge approach, inspect primary evidence, seek disconfirming evidence, and report prioritized findings with reasoning.
7. Return the artifact path followed by the prompt.

When the target is a prior review, preserve the original work, the review's findings and evidence, responses or resolutions, and contested items. Ask the next agent to audit both layers independently rather than inherit the first reviewer's judgments.

Write for a reviewer who cannot see the current chat. Include enough context to prevent rediscovery and accidental drift, but do not prescribe the reviewer's conclusions.
