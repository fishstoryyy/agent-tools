---
name: create-session-handoff
description: Create or refresh a durable Markdown handoff file that lets a fresh agent or model continue active work in the same project without access to the current conversation. Use when the user is ending a session, switching models through a new session, pausing unfinished work, or explicitly asks for a handoff file, continuation file, session checkpoint, or restart artifact. Write the artifact into the workspace; do not use this skill for prompt-only handoffs or independent review briefs.
disable-model-invocation: true
---

# Create Session Handoff

Produce the smallest reliable source-of-truth artifact a capable fresh agent needs to continue the next phase. Preserve non-discoverable intent and decisions; point to discoverable workspace evidence instead of copying it.

## Output

Use the path requested by the user. Otherwise write `./temp/HANDOFF.md`, resolving `.` from the workspace or project root.

Create the parent directory when needed. If the target already contains a handoff, inspect it and refresh it to current truth rather than appending another chronological update. If the target appears unrelated, ask before overwriting it.

## Workflow

1. Identify the downstream objective, immediate next phase, scope boundaries, and completion criteria. Infer these from available context when safe; ask one concise question only when ambiguity would materially change the handoff.
2. Reconstruct relevant conversation-only context: user intent, decisions and rationale, rejected paths worth avoiding, constraints, preferences, unresolved questions, and unfinished thought.
3. Inspect the live workspace. Check relevant files and documentation, Git status and diff when applicable, and available test or command results. Do not ask the user for facts that can be recovered safely.
4. Separate information into:
   - **State explicitly:** non-discoverable intent, decisions, rationale, constraints, uncertainty, ownership, and exact next action.
   - **Point to:** code, documents, diffs, logs, issues, and other artifacts a fresh agent can inspect directly.
5. Reconcile conversation claims with workspace evidence. Prefer current artifacts when they conflict, and record the discrepancy when it matters.
6. Write the handoff using only the sections that carry useful information.
7. Read the completed file back. Confirm that paths resolve where practical and that every claimed verification result is accurate.

## Artifact shape

Start with a direct mandate to the next agent. Adapt the headings, but cover the following when relevant:

- **Objective and done criteria:** the outcome, boundaries, and observable completion conditions.
- **Current state:** what is complete, in progress, not started, blocked, or failing.
- **Decisions and constraints:** non-obvious choices, rationale that prevents drift, user requirements, and explicit non-goals.
- **Workspace pointers:** repository-relative paths, branch or commit identifiers, relevant diff areas, issue or document links, and generated artifacts.
- **Verification evidence:** commands actually run and concise results. Clearly label checks that were not run or need rerunning.
- **Next actions:** an ordered, executable starting sequence for the recipient.
- **Open questions and risks:** unresolved choices, assumptions, suspected failures, and likely traps.
- **Rejected approaches:** include only when omission would cause costly repetition.

Omit empty sections. Prefer bullets and short paragraphs over a fixed ceremonial template.

## Quality rules

- Write for a capable agent with the same workspace and tools but none of this conversation.
- Make the next action unambiguous. The recipient should know what to inspect first and what outcome to produce.
- Do not write a transcript, retrospective, or chronological diary.
- Do not reproduce large code blocks, logs, diffs, or file contents when a precise pointer is enough.
- Preserve rationale when it controls future choices; omit history that does not change the next agent's behavior.
- Distinguish verified facts, user-reported facts, assumptions, and hypotheses.
- Never imply that a test, build, command, review, or deployment ran when it did not.
- Include uncommitted work and dirty-worktree state when relevant. Do not stage, commit, revert, or clean changes unless separately requested.
- Exclude secrets, credentials, hidden reasoning, and irrelevant personal or environment details.
- Do not continue the downstream implementation after creating the handoff.
- Optimize for sufficient context, not maximal context or minimal word count.

## Final response

Return:

1. The handoff file path.
2. One short kickoff instruction the user can send in the new session, pointing the recipient to the file and asking it to verify the live workspace before continuing.

Do not duplicate the handoff contents in the response.
