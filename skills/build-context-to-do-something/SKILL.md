---
name: build-context-to-do-something
description: Generate an accurate, ready-to-send prompt that gives a fresh agent the non-obvious context it needs to perform a user-specified task effectively. Use mid-session when the current agent holds relevant conversation or workspace context and the user asks to brief, prepare, hand off, or build context for another agent to do something, such as review a diff, investigate a bug, continue implementation, or evaluate a plan.
---

# Build Context to Do Something

Create a launch prompt for a fresh agent that is capable at reasoning but blind to this conversation and the work done in it. Test every element against one bar: does the agent need this to do the task correctly, and can it not recover this on its own? Include what clears both; drop the rest. Conciseness is the result of applying that bar honestly — do not add a separate pressure to shorten, and do not pad for safety.

## Workflow

1. Identify the downstream task from the invocation. If it is missing, ask one concise question. If it is present but ambiguous, ask only when the ambiguity would materially change the work.
2. Reconstruct the relevant context from the conversation and inspect the workspace or source artifacts as needed. Do not ask the user for what you can recover yourself.
3. Lead with the task and expected result: what the agent must produce, the scope boundaries, and what a correct or finished result looks like. Make this part specific — vagueness here is the most common cause of wrong work.
4. Then include only what clears the bar: precise pointers (repository-relative paths, commits, diff ranges, links); non-obvious intent, binding constraints, and prior decisions, including a decision's rationale where that rationale is what makes the task make sense; and essential state the recipient could not quickly discover. For genuinely unsure cases, decide by checking whether the agent can recover the information — open the file, trace the reference — not by defaulting to include or to cut.
5. Reference an artifact when the agent can open it cheaply; inline the content when it is small, central to the task, or conversation-only. "Above," "earlier," and "as discussed" are invisible to the recipient — inline the substance or drop it.
6. Leave out session chronology and step-by-step instructions on how to do the task, unless the user made a specific method a constraint. Keep the brief "why" behind non-obvious choices — that is intent, not hand-holding.
7. Do not invent context, imply that checks were run when they were not, or bias the work (for example, do not pre-load a review with your own verdict). Mark assumptions as assumptions.
8. Before returning, read the prompt once as the blind recipient and confirm the bar held both ways: nothing recoverable or unneeded was left in, and nothing needed was left out. Fix either failure.
9. Do not perform the downstream task or create a separate handoff artifact unless the user explicitly asks. Return only `Ready-to-send prompt:` followed by the prompt in a fenced text block.