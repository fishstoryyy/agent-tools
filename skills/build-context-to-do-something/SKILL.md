---
name: build-context-to-do-something
description: Generate a concise, accurate, ready-to-send prompt that gives a fresh agent just enough context to perform a user-specified task effectively. Use mid-session when the current agent holds relevant conversation or workspace context and the user asks to brief, prepare, hand off, or build context for another agent to do something, such as review a diff, investigate a bug, continue implementation, or evaluate a plan.
---

# Build Context to Do Something

Create a self-contained launch prompt for a fresh agent that cannot see the current conversation. Transfer the context needed to perform the requested task without replaying the session.

## Workflow

1. Extract the downstream task from the invocation. If it is missing, ask one concise question. Otherwise, ask only when an unresolved ambiguity would materially change the task.
2. Reconstruct the relevant context from the conversation and inspect the workspace, files, diffs, commits, commands, or other artifacts as needed. Do not ask the user to repeat available information.
3. Select only context that changes how the recipient should understand, execute, or evaluate the task:
   - The concrete task and expected deliverable.
   - The objective and relevant success criteria.
   - The target artifacts and their current state.
   - Decisions, constraints, assumptions, and non-goals that must be preserved.
   - Known risks or unresolved questions that materially affect the task.
   - Exact paths, commits, diff ranges, commands, tests, results, or links needed to get oriented.
4. Separate verified facts from assumptions. Do not invent context, imply that checks were run when they were not, or present the current agent's interpretation as established fact.
5. Account for what the recipient can access. Prefer precise references over copied content when both agents share the workspace. Include essential facts directly when the recipient may not have access to an artifact. Never rely on phrases such as "above," "earlier," or "as discussed."
6. Write the prompt as direct instructions to the recipient. Tell it what to inspect and what to produce. Preserve useful context without prescribing conclusions that the downstream task should determine independently.
7. Keep the prompt concise. Target 100-250 words by default; exceed that only when omitting context would materially reduce accuracy or effectiveness. Remove chronology, commentary, repeated descriptions, and facts the recipient can discover immediately from the referenced artifacts.
8. Do not perform the downstream task or create a separate handoff artifact unless the user explicitly asks. Return only `Ready-to-send prompt:` followed by the prompt in a fenced text block.

## Task Adaptation

- For a review, identify the exact review target, intended behavior, relevant diff or base, validation already performed, and material risk areas without suggesting a verdict.
- For continuing work, state the current status, decisions already made, immediate objective, constraints, and evidence needed to verify completion.
- For investigation or research, define the question, known evidence, source constraints, unresolved uncertainty, and expected output.

Before returning the prompt, verify that a fresh agent can identify the task, target, purpose, constraints, accessible evidence, and completion condition without seeing the current conversation.
