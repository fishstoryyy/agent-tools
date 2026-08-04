---
name: orca-two-agent-loop
description: Run an explicitly requested Orca-native manager-engineer workflow through goal interview, planning, adversarial plan review, implementation, adversarial code review, and delivery. The invoking agent becomes manager and supervises one persistent engineer session through fresh Orca Tasks and Dispatches. Use only when the user explicitly says "orca two-agent loop" or "manager-engineer loop," or deliberately asks two agents to plan, implement, and review a goal end to end with Orca.
disable-model-invocation: true
---

# Orca Two-Agent Loop

Act as the manager. Coordinate one persistent engineer session with Orca after
the user explicitly starts this workflow. Keep the user involved through the
goal interview, then operate autonomously except for the last-resort escape
hatch below.

This skill defines workflow policy, not Orca command syntax. Before acting,
confirm that `grill-the-goal` and `adversarial-review` are discoverable, then
fetch and follow the version-matched guides:

```bash
orca skills get orchestration
orca skills get orca-cli
```

Favor native Orca commands for every supported worktree, terminal,
orchestration, messaging, and workspace-status operation. The fetched guides
override remembered syntax and the limited provider conventions below.

## Roles and Authority

- **Manager:** the already-running agent that invoked this skill. Own the goal
  interview, plan, Run, coordinator commands, review, and delivery. Do not
  relaunch the manager to change its model or thinking level.
- **Engineer:** one persistent supervised worker session. Own implementation and
  send `ask`, `heartbeat`, `escalation`, and `worker_done` from its own terminal
  under the active Dispatch contract.

The manager may create and revise `plan.md` before implementation. Once
implementation starts, the manager treats the engineer worktree as read-only;
all code fixes belong to the engineer.

## Resolve the Engineer

If the user omitted the agent family, ask them to choose it. Do not infer
Codex versus Claude versus OMP from unrelated configurations.

After the family is known, explicit model and thinking values win. Resolve
missing values from that agent's real configuration and current CLI help, then
confirm once:

> Engineer: `<agent>` / `<model>` / `<thinking>` (`<source>`). Say so to change.

Proceed unless the user objects. Never insert a hard-coded model into this
template.

The Orca guides already document known agent IDs and the custom Codex launch
path. Do not repeat those instructions here. When the fetched guide lacks an
equivalent custom launch convention, verify the installed CLI help and use:

- Claude Code: `claude --model <model> --effort <level>`
- OMP: `omp --model <model> --thinking <level>`

Wrap any custom agent command with the native Orca terminal/worktree procedure
from the fetched guide. If a newer guide documents the provider, follow it
instead of these conventions.

## Workflow

1. **Interview:** invoke `grill-the-goal`. Stop when it produces a
   decision-ready goal brief. Keep this phase about *what*, not implementation.
2. **Plan:** decide the implementation approach with concise, stated defaults.
   Cover file-level changes, risks, validation, and acceptance checks without a
   second blocking interview.
3. **Provision:** create one Run and, by default, a new Orca child worktree for
   the engineer. The manager remains in its current worktree. Use agent-first
   native creation when it supports the resolved worker command; otherwise use
   the custom-command path in the current Orca guide.
4. **Materialize the plan:** write canonical `plan.md` in the engineer child
   worktree before sending the first review Dispatch. The manager may revise
   only this file during plan review; do not dirty the manager's worktree.
5. **Review the plan:** create a review-only Task and Dispatch instructing the
   engineer to invoke `adversarial-review` against `plan.md`. The engineer
   reports findings through its own `worker_done`; the manager accepts or
   rejects them with reasons and revises `plan.md` when warranted.
6. **Implement:** dispatch the agreed plan as a fresh Task and Dispatch to the
   same engineer terminal. The engineer implements, validates, and reports
   `worker_done` with evidence and modified paths.
7. **Review the implementation:** the manager invokes `adversarial-review`
   read-only against the engineer's diff and validation evidence. Dispatch
   accepted fixes or requests for stronger evidence back to the same engineer.
8. **Deliver:** after acceptance, summarize the result and validation, identify
   the engineer worktree, and use native Orca status commands to mark it
   `completed`.

## Rounds, Context, and Convergence

- Use a fresh Task + Dispatch for every plan-review round, implementation, and
  code-review round. This creates clean lifecycle and provenance boundaries.
- Reuse the same engineer terminal throughout. Its model context persists
  across rounds; a fresh Dispatch does **not** create context isolation.
- Make every task specification self-contained even though context persists, so
  the contract remains inspectable and recoverable.
- Allow at most three rounds per review gate. If disagreement remains, the
  manager decides when the issue is reversible and adequately evidenced.
- Before forcing a decision on a high-stakes unresolved gap that the interview
  missed, use the user escape hatch below.

## User Escape Hatch

After the interview, re-engage the user only when adversarial review exposes a
high-stakes goal or product decision that the interview missed and the two
agents cannot resolve faithfully. This takes precedence over the round-limit
default. Do not ask the user about implementation details the agents can settle.

## Guardrails

- Never edit the manager's worktree, another worktree, or `main` as part of
  implementation. Limit manager writes in the engineer worktree to `plan.md`
  before implementation begins.
- Wait through Orca's mailbox lifecycle; do not poll terminal input. Treat wait
  timeouts as checkpoints, not automatic worker failure.
- If a Dispatch fails three times or the engineer terminal dies, report the
  blocker to the user instead of repeatedly retrying.
- Do not claim fresh-context review, successful skill composition, or runtime
  completion unless each was actually tested.
