---
name: prepare-adversarial-review-light
description: Create a context-rich markdown brief and concise ready-to-send prompt for an independent adversarial review of work produced in the current session, including plans, analyses, code, strategy research, infrastructure, or prior reviews. Use when handing work to a fresh reviewer or third-line audit agent who needs the conversation's decisions, evidence, resources, and unresolved risks without replaying the session.
---

# Prepare Adversarial Review Light

Prepare a fresh reviewer to understand the work as though they had followed the session and still evaluate it independently.

## Instructions

1. Reconstruct the relevant context from the conversation and inspect the current workspace as needed. Do not ask the user to repeat available information.
2. Identify the review target and its current state. Capture the objective, user intent, decisions and rationale, assumptions, constraints, non-goals, rejected paths, and unresolved questions that affect evaluation.
3. Give the reviewer an operational trail to the evidence: exact file paths, links, commits, commands, tests and results, data or source material, and other artifacts. Verify references when practical; never imply that unperformed validation occurred.
4. Separate evidence and established facts from assumptions, interpretations, and incumbent conclusions. Include known failures and unresolved uncertainties, but do not preselect criticism, defend the work, or suggest a verdict.
5. Create a markdown artifact at the user's requested path, or `adversarial-review-brief.md` near the reviewed work when no path is given. Use whatever structure communicates the context naturally. Omit irrelevant topics and avoid ceremonial sections, fixed templates, and forced brevity. Make this brief the complete context and mandate.
6. In the brief, tell the reviewer to save the substantive review as a markdown file, verify that it exists, and then reply only with its path plus a concise prompt for the upstream agent. For a second-line review, that prompt should ask the original agent to read the report, address material findings, improve and verify the work, and document evidence-backed disagreements. For an audit, address the prompt to the reviewed reviewer.
7. Generate a ready-to-send launch prompt of two to four short sentences and no more than 100 words. Keep it as a pointer rather than repeating the brief: name the role, link the brief, request independent evidence-based review, and repeat the markdown-report and return-prompt requirement.
8. Return the artifact path followed by the prompt.

When the target is a prior review, preserve the original work, the review's findings and evidence, responses or resolutions, and contested items. Ask the next agent to audit both layers independently rather than inherit the first reviewer's judgments.

Write for a reviewer who cannot see the current chat. Include enough context to prevent rediscovery and accidental drift, but do not prescribe the reviewer's conclusions. Treat the brief and review report as the source-of-truth artifacts; keep both prompts concise.
