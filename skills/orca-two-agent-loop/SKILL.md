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

This skill defines workflow policy, not Orca command syntax. Before acting, use
the installed `orca-cli` skill to resolve the correct Orca executable for the
current platform and environment; never assume bare `orca`. Confirm that
`grill-the-goal` and `adversarial-review` are discoverable to the manager, then
fetch and follow the version-matched guides. Replace `<ORCA>` with the resolved
executable; do not run the placeholder literally.

```bash
<ORCA> skills get orchestration
<ORCA> skills get orca-cli
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

## Placement and Git Base

Use a separate Orca worktree by default because this workflow requires the
engineer to edit without touching the manager's checkout. State that concrete
checkout conflict before creation; it is the justification required by the
Orca guide.

Decide Orca lineage and Git base separately:

- If the goal depends on committed work from the manager's branch, use child
  lineage and explicitly base the new branch on the manager branch's committed
  HEAD.
- If the goal is independent, use top-level lineage and the repository default
  base.
- If required work exists only as uncommitted manager changes, do not silently
  omit or copy it. Resolve during the interview whether the user will commit it,
  explicitly permit the engineer to share the current worktree, or exclude that
  work. Choosing the shared worktree explicitly waives the default checkout
  isolation for that run.

## Workflow

1. **Interview:** invoke `grill-the-goal`. Stop when it produces a
   decision-ready goal brief. Keep this phase about *what*, not implementation.
2. **Plan:** decide the implementation approach with concise, stated defaults.
   Cover file-level changes, risks, validation, acceptance checks, the delivery
   boundary, and who owns any commit, PR, or merge without a second blocking
   interview.
3. **Provision:** create one Run and the chosen Orca worktree and persistent
   engineer terminal. The manager remains in its current worktree. Initial
   provisioning intentionally uses the guide's low-level worktree/terminal path
   rather than `worker-start`, because `plan.md` must exist before the first
   review Dispatch. Prefer agent-first worktree creation when it supports the
   exact worker command; use the documented custom-command path otherwise.
4. **Materialize the plan:** write canonical `plan.md` in the engineer
   worktree before sending the first review Dispatch. The manager may revise
   only this file during plan review; do not dirty the manager's worktree unless
   the user selected the shared-current exception above.
5. **Review the plan:** create a review-only Task and Dispatch instructing the
   engineer to invoke `adversarial-review` against `plan.md`. First confirm the
   skill is discoverable in the engineer's own agent environment using that
   agent's native discovery mechanism. When a remote environment cannot be
   preflighted, make discovery the first clause of the Dispatch and require
   immediate escalation if it is unavailable. The engineer reports findings
   through its own `worker_done`; the manager accepts or
   rejects them with reasons and revises `plan.md` when warranted. This is an
   explicit exception to the review-only coordinator-edit rule: the user made
   the manager owner of the plan artifact. It never authorizes manager code
   edits.
6. **Implement:** dispatch the agreed plan as a fresh Task and Dispatch to the
   same engineer terminal. The engineer implements, validates, and reports
   `worker_done` with evidence and modified paths.
7. **Review the implementation:** the manager invokes `adversarial-review`
   read-only against the engineer's diff and validation evidence. Dispatch
   accepted fixes or requests for stronger evidence back to the same engineer.
8. **Deliver:** after acceptance, summarize the result and validation, identify
   the engineer worktree, and hand any commit, PR, or merge to the owner named
   in the plan. Use native Orca status commands: keep the worktree `in-review`
   while the agreed integration step remains outstanding; mark it `completed`
   only when the agreed delivery boundary has been satisfied.

## Rounds, Context, and Convergence

- Use a fresh Task + Dispatch for every plan-review round, implementation, and
  code-review round. This creates clean lifecycle and provenance boundaries.
- Reuse the same engineer terminal throughout. Its model context persists
  across rounds; a fresh Dispatch does **not** create context isolation.
- Make every task specification self-contained even though context persists, so
  the contract remains inspectable and recoverable.
- Allow at most three rounds per review gate. The limit ends repeated opinion
  exchange; it does not force an unsupported decision.
- After the limit, decide with a one-line rationale when the choice is
  reversible and adequately evidenced. Otherwise run the cheapest available
  falsification test or reshape the choice to make it reversible.
- If a consequential, hard-to-reverse choice remains thinly evidenced after
  that attempt, use the user escape hatch. If the user cannot resolve it, report
  the loop blocked rather than inventing policy.

## User Escape Hatch

After the interview, re-engage the user only when adversarial review exposes a
consequential, hard-to-reverse decision that the agents cannot resolve
faithfully with evidence. This includes technical decisions when choosing on
the user's behalf would exceed the manager's authority. This takes precedence
over the round-limit default. Do not ask the user about implementation details
the agents can settle.

## Guardrails

- Never edit the manager's worktree, another worktree, or `main` as part of
  implementation unless the user explicitly selected the shared current
  worktree for required uncommitted changes. Limit manager writes in the
  engineer worktree to `plan.md` before implementation begins.
- Wait through Orca's mailbox lifecycle; do not poll terminal input. Treat wait
  timeouts as checkpoints, not automatic worker failure.
- If a Dispatch fails three times or the engineer terminal dies, report the
  blocker to the user instead of repeatedly retrying.
- Do not claim fresh-context review, successful skill composition, or runtime
  completion unless each was actually tested.
