---
name: task-story
description: Create or append a succinct Markdown storyline for work spanning multiple AI coding sessions. Use only when explicitly invoked to record one or more logical checkpoints, preserving high-level progress, key decisions and their reasons, and the evolving direction for subsequent agents.
disable-model-invocation: true
---

# Task Story

Give agents joining a task a shared sense of what it aims to achieve, how it has developed, and where it is heading. Run only on explicit invocation; reading the artifact does not trigger an update.

## Artifact

Use the supplied path or the known story file for this task. Otherwise create `temp/<task-name>-story.md` under the project root, using a short, descriptive, hyphenated task name. Keep one file per task. If an existing target belongs to another task or the intended story is ambiguous, clarify before writing.

For a new file, add a task title and establish the objective in the opening checkpoint. Record the known journey in one or more entries. For an existing file, cover meaningful developments not already recorded.

## Checkpoints

Read the existing story and relevant conversation context. Check workspace evidence where it could change a material claim. Use only supported context; do not invent missing sessions or dates, or turn tentative ideas into settled decisions.

Identify distinct logical checkpoints in the unrecorded history: meaningful milestones, discoveries, or changes of direction. One invocation can append several checkpoints in chronological order, including several from the same session. Let meaningful developments determine the boundaries; do not split routine activity into extra entries.

For each checkpoint, append a numbered heading with its date when known and a short title, followed by one short narrative paragraph, usually about three sentences. Capture meaningful progress, the reason behind an important choice, and the high-level direction as it stood at that point. Preserve the causal thread: what was learned or changed, and how that shaped the work.

For example:

> **Checkpoint 3 — 2026-09-22 — Foundation established**
>
> The storage model and ingestion interfaces are in place. We explored batch and streaming ingestion and chose batch first because real-time updates aren't needed yet. The next phase is to connect one source end to end and see whether the foundation holds up against real data.

Omit implementation inventories, command logs, task checklists, and routine activity. Include a path only when it materially helps orientation. The story provides context; it does not assign the next agent an executable plan.

## Append rules

- Preserve all existing content exactly. Never rewrite, condense, reorder, or remove earlier entries to keep the file short; keep each new entry succinct instead.
- Explain corrections and changes of direction in a new entry, identifying which earlier conclusion changed and why.
- Avoid repeating earlier context. If nothing meaningful has changed, leave the file untouched and say so.
- Update only when explicitly invoked. Leave deletion to the user when the task is finished.

After writing, read back the result and confirm that prior content is unchanged. Return the artifact path and a brief statement of what was added, then stop.
