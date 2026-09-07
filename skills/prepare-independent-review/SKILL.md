---
name: prepare-independent-review
description: Produce only a short, paste-ready prompt for an independent code reviewer. Invoke on the agent that completed the work to transfer the problem and essential context without describing its implementation.
disable-model-invocation: true
---

# Prepare Independent Review

Return only the paste-ready prompt: no preamble, commentary, heading, or code fence. Do not create an artifact or perform the review. Keep the prompt to a few short sentences, aiming for 100 words or fewer.

Ground it in the original request and subsequent user clarifications: the problem, essential context, intended outcome, and binding constraints. Make it self-contained for a reviewer who cannot see this conversation. Do not recast your implementation choices as requirements or invent missing context.

Omit change summaries, added or edited file lists, solution details, implementation rationale, test-result claims, and your own verdict or suggested findings. Include only the minimal locator needed to identify the review target, such as a repository or worktree path and branch, commit range, or uncommitted state; recover it from available context or read-only inspection.

Tell the reviewer to first reason independently about how to solve the stated problem before reading the implementation or diff, then inspect the changes against the requirements and that reasoning. Authorize any necessary tests and investigative probes, including temporary edits. Require no net changes to the worktree or index when finished: preserve pre-existing work and undo only review-created edits and artifacts. Request evidence-backed material findings, or an explicit statement when none are found.
