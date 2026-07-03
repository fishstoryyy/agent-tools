---
name: build-context-to-do-something
description: Generate a minimal, accurate, ready-to-send prompt that gives a fresh agent only the non-obvious context needed to perform a user-specified task effectively. Use mid-session when the current agent holds relevant conversation or workspace context and the user asks to brief, prepare, hand off, or build context for another agent to do something, such as review a diff, investigate a bug, continue implementation, or evaluate a plan.
---

# Build Context to Do Something

Create a concise, effective launch prompt for a fresh agent that cannot see the current conversation. Assume the receiving agent is highly capable: transfer only context it cannot readily infer or efficiently recover from the task and referenced artifacts.

## Workflow

1. Extract the downstream task from the invocation. If it is missing, ask one concise question. Otherwise, ask only when an unresolved ambiguity would materially change the task.
2. Reconstruct the relevant context from the conversation and inspect the workspace or source artifacts as needed. Do not ask the user to repeat available information.
3. Put the task and expected result first. Then include only:
   - Precise pointers to the target, such as repository-relative paths, commits, diff ranges, or links.
   - Non-obvious intent, binding constraints, prior decisions, or assumptions that materially affect the task.
   - Essential state the recipient could not quickly discover and whose omission could cause incorrect work.
4. Omit implementation advice, suggested steps, technical explanations, session chronology, and facts the recipient can discover directly. Do not tell a capable agent how to do the task unless the user explicitly makes that method a constraint.
5. Prefer references over copied content when the recipient can access the same artifacts. Include information directly only when it is essential and otherwise unavailable. Never rely on phrases such as "above," "earlier," or "as discussed."
6. Separate verified facts from assumptions. Do not invent context, imply that checks were run when they were not, or bias work such as reviews toward the current agent's conclusions.
7. Make the prompt as short as possible while remaining effective. Use no minimum length and normally stay under 150 words. For every sentence, ask: would removing this plausibly cause incorrect work or expensive rediscovery? If not, remove it.
8. Do not perform the downstream task or create a separate handoff artifact unless the user explicitly asks. Return only `Ready-to-send prompt:` followed by the prompt in a fenced text block.

Before returning the prompt, verify that a capable fresh agent can identify the task, target, non-obvious constraints, and expected result without seeing the current conversation.
