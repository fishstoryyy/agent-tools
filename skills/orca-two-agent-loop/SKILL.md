---
name: orca-two-agent-loop
description: Run an explicitly requested Orca-native manager-engineer workflow through goal interview, engineer-authored planning, adversarial plan review, implementation, adversarial code review, and delivery. The manager owns the interview, the resulting goal brief, and both review gates; one persistent engineer session owns the plan and the implementation. Use only when the user explicitly says "orca two-agent loop" or "manager-engineer loop," or deliberately asks two agents to plan, implement, and review a goal end to end with Orca.
disable-model-invocation: true
---

# Orca Two-Agent Loop

Act as the manager. Coordinate one persistent engineer session with Orca after
the user explicitly starts this workflow. Keep the user involved through the
goal interview, then operate autonomously except for the last-resort escape
hatch below.

This skill defines workflow policy, not Orca command syntax. Before acting,
confirm that `orca-cli`, `grill-the-goal`, and `adversarial-review` are
discoverable to the manager. Use the installed `orca-cli` skill to resolve the
correct Orca executable for the current platform and environment; never assume
bare `orca`. Then fetch and follow the version-matched guides. Replace `<ORCA>`
with the resolved executable; do not run the placeholder literally.

```bash
<ORCA> skills get orchestration
<ORCA> skills get orca-cli
```

Favor native Orca commands for every supported worktree, terminal,
orchestration, messaging, and workspace-status operation. The fetched guides
override remembered syntax and the limited provider conventions below.

## Roles and Authority

- **Manager:** the already-running agent that invoked this skill. Own the goal
  interview, the resulting brief, the Run, coordinator commands, both review
  gates, and delivery coordination. Do not author the plan or the
  implementation. Do not relaunch the manager to change its model or thinking
  level.
- **Engineer:** one persistent supervised worker session. Own the plan and the
  implementation end to end: draft `plan.md` from the brief, revise it under
  review, implement it, resolve review findings, and carry out the agreed
  delivery boundary once the manager approves. Send `ask`, `heartbeat`,
  `escalation`, and `worker_done` from its own terminal under the active
  Dispatch contract.

The manager writes nothing in the engineer worktree and reviews read-only from
the first Dispatch onward. Every plan and code edit belongs to the engineer.
The interview conversation stays with the manager; only the brief crosses to
the engineer, so the brief must stand on its own.

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
   Make sure the brief settles the acceptance criteria and the delivery
   boundary: whether the work ends at a validated working tree, a commit, a
   pushed branch, an open PR, or a merge. That boundary is outcome scope and
   belongs to the user. Who performs those steps is not a user question — the
   engineer does, because the manager never writes in that worktree.
2. **Provision:** create the Run, create the first Task whose spec carries the
   goal brief inline and asks the engineer to draft `plan.md`, then start the
   engineer through the guide's composed `worker-start` path. Nothing needs to
   exist in the worktree beforehand, so provisioning and the first Dispatch are
   one step. `worker-start` expresses every lineage and Git-base choice from the
   section above; fall back to the guide's custom-argv path only when the
   engineer needs a custom agent command, and attach that terminal to the
   Dispatch rather than dispatching outside the composed path. The manager
   remains in its own worktree.
3. **Plan:** the engineer drafts `plan.md` in its own worktree from the brief —
   approach, file-level changes, risks, validation strategy, and sequencing —
   then reports `worker_done`. `plan.md` is a working artifact: keep it out of
   the deliverable commit and out of the reviewed implementation diff.
4. **Review the plan:** the manager reads `plan.md` read-only and invokes
   `adversarial-review` against it. Dispatch accepted findings back as a fresh
   Task and Dispatch; the engineer revises `plan.md` or defends it with
   evidence. Iterate until the manager accepts the plan.
5. **Implement:** dispatch the agreed plan as a fresh Task and Dispatch to the
   same engineer terminal. The engineer implements, validates, and reports
   `worker_done` with evidence and modified paths.
6. **Review the implementation:** the manager invokes `adversarial-review`
   read-only against the engineer's diff and validation evidence. Dispatch
   accepted fixes or requests for stronger evidence back to the same engineer.
7. **Deliver:** after acceptance, summarize the result and validation and
   identify the engineer worktree. The manager approves; the engineer then
   carries out the agreed delivery boundary as a final Task and Dispatch,
   unless the brief names a different owner for that step. Use native Orca
   status commands: keep the worktree `in-review` while the agreed integration
   step remains outstanding; mark it `completed` only when the agreed delivery
   boundary has been satisfied.

## Rounds, Context, and Convergence

- Use a fresh Task + Dispatch for the plan draft, every plan-review round, the
  implementation, and every code-review round. This creates clean lifecycle and
  provenance boundaries. The plan draft is the Dispatch created by
  `worker-start`, not a review round.
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
  worktree for required uncommitted changes. The manager writes nothing in the
  engineer worktree.
- Wait through Orca's mailbox lifecycle; do not poll terminal input. Treat wait
  timeouts as checkpoints, not automatic worker failure.
- If a Dispatch fails three times or the engineer terminal dies, report the
  blocker to the user instead of repeatedly retrying.
- Do not claim fresh-context review, successful skill composition, or runtime
  completion unless each was actually tested.
