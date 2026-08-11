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
override remembered syntax and any command names referenced below.

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

From the first Dispatch onward, the manager treats the engineer's selected
checkout as read-only. Every plan and code edit belongs to the engineer. The
interview conversation stays with the manager; only the brief crosses to the
engineer, so the brief must stand on its own.

## Resolve the Engineer

Explicit user values always win. Fill anything the user left unspecified from
the default engineer — Codex / `gpt-5.6-sol` / `xhigh` — rather than inferring
it from unrelated configurations. Confirm the resolved spec once:

> Engineer: `<agent>` / `<model>` / `<thinking>`. Say so to change.

Proceed unless the user objects.

Launch the fresh engineer through the current orchestration guide's composed
`worker-start` path. Pass the resolved agent, model, and effort as
per-invocation launch preferences when the guide supports them; treat model
identifiers as opaque provider values. Do not construct provider-specific argv
merely to select a model or effort. Use the guide's low-level custom-argv path
only when composed start cannot express the resolved engineer, and follow its
setup, topology, and recovery rules exactly. Read the start receipt and confirm
that the effective launch preferences match the resolved spec. If Orca did not
apply the model or effort, never proceed with a different engineer. Recover to
the custom-argv path without re-engaging the user: stop that Dispatch with
`worker-stop` first, then relaunch through the guide's replacement mechanism,
including `--retry-of`, so the round never carries two Dispatches.

Composed launch preferences reach only the agents and models Orca supports, and
only when the worker server advertises that support. Custom argv remains the
fallback whenever composed start cannot express the resolved engineer or did not
apply the requested model or effort. The fetched guides illustrate only the
Codex shape, so use these directly rather than spending a `--help` call. Verify
only when a command fails, and prefer a fetched guide that documents a provider
differently:

- Codex: `codex --model <model> -c model_reasoning_effort="<effort>"` — effort
  is one of `none`, `minimal`, `low`, `medium`, `high`, `xhigh`, `max`.
- Claude Code: `claude --model <model> --effort <level>` — effort is one of
  `low`, `medium`, `high`, `xhigh`, `max`.
- OMP: `omp --model <model> --thinking <level>` — thinking is one of `off`,
  `minimal`, `low`, `medium`, `high`, `xhigh`, `max`, `auto`.

## Placement and Git Base

Use the current Orca worktree by default. The manager stays read-only from the
first Dispatch while the engineer edits there. Create a separate worktree only
when the user explicitly requests one or a concrete checkout or filesystem
conflict makes sharing unsafe or impossible; state that conflict before
creation.

Before the first Dispatch in a shared checkout, capture its full baseline:
HEAD plus the staged, unstaged, and untracked contents. Carry its HEAD and
changed-path list in every Task. Any required edit that
overlaps a pre-existing changed path is a concrete sharing conflict; use a
separate worktree unless the user explicitly accepts mixed ownership. Settle
known overlap at provisioning from the brief. If overlap surfaces only from the
plan, use the user escape hatch rather than replacing the persistent engineer
mid-run. Both review gates and the delivery boundary cover only the engineer's
delta from the baseline. Never commit, stash, or revert pre-existing work.

For an allowed new worktree, decide Orca lineage and Git base separately:

- If the goal depends on committed work from the manager's branch, use child
  lineage and explicitly base the new branch on the manager branch's committed
  HEAD.
- If the goal is independent, use top-level lineage and the repository default
  base.
- If required work exists only as uncommitted manager changes, do not silently
  omit or copy it. Resolve during the interview whether the user will commit it,
  return to the shared current worktree, or exclude that work.

For every new worktree, request setup through composed `worker-start` and let
Orca enforce the repository's startup policy. Read the returned receipt before
continuing; never race or relax `wait-for-setup`. If a custom-argv engineer is
unavoidable, first read the repository's agent-startup policy with
`<ORCA> repo show --repo <repo> --json`; neither fetched guide names the field
that carries it. That path cannot honor `wait-for-setup`, so if the repository
requires it, use the user escape hatch.

## Workflow

1. **Interview:** invoke `grill-the-goal`. Stop when it produces a
   decision-ready goal brief. Keep this phase about *what*, not implementation.
   Make sure the brief settles the acceptance criteria and the delivery
   boundary: whether the work ends at a validated working tree, a commit, a
   pushed branch, an open PR, or a merge. That boundary is outcome scope and
   belongs to the user. Who performs those steps is not a user question — the
   engineer does, because the manager is read-only in the selected checkout
   from the first Dispatch onward.
2. **Provision:** select placement under the policy above, create the Run, and
   create the first Task whose spec carries the goal brief inline, invites
   brief-clarity questions before drafting, and asks the engineer to draft
   `plan.md`. Start the engineer through composed `worker-start`, passing the
   resolved agent, model, and effort through the guide's per-worker launch
   preferences. For a new worktree, request setup through the same composed
   start. Nothing needs to exist in the checkout beforehand, so provisioning
   and the first Dispatch are one step. Take a low-level custom-argv path only
   for an engineer configuration the fetched guide cannot express. The manager
   remains in its existing session and read-only from this Dispatch onward.
3. **Plan:** the engineer drafts `plan.md` in the selected checkout from the
   brief — approach, file-level changes, risks, validation strategy, and
   sequencing — then reports `worker_done`. `plan.md` is a working artifact:
   keep it out of the deliverable commit and out of the reviewed implementation
   diff.
4. **Review the plan:** the manager reads `plan.md` read-only and invokes
   `adversarial-review` against it. Dispatch accepted findings back as a fresh
   Task and Dispatch; the engineer revises `plan.md` or defends it with
   evidence. Iterate until the manager accepts the plan. Before accepting, if
   the plan rests on a load-bearing premise — one whose falsity invalidates the
   plan rather than degrading it — that a single runnable check would settle and
   review has not already settled, dispatch that check first and accept on its
   result.
5. **Implement:** dispatch the agreed plan as a fresh Task and Dispatch to the
   same engineer terminal. The engineer implements, validates, and reports
   `worker_done` with evidence and modified paths.
6. **Review the implementation:** the manager invokes `adversarial-review`
   read-only against the engineer's diff and validation evidence. Dispatch
   accepted fixes or requests for stronger evidence back to the same engineer.
   If the delivery boundary integrates — merge or rebase — the engineer first
   prepares the complete integration candidate against the current target,
   including delivery-relevant untracked files, and this gate reviews that
   candidate rather than the pre-integration diff. A non-integrating boundary
   needs no second gate.
7. **Deliver:** after acceptance, summarize the result and validation and
   identify the engineer checkout. The manager approves; the engineer then
   carries out the agreed delivery boundary as a final Task and Dispatch,
   unless the brief names a different owner for that step. Finalize only while
   both the target head and the reviewed candidate are unchanged; if either
   moved, rebuild, re-validate, and return through step 6 when content or
   evidence changed. Commit-metadata changes do not count. Use native Orca
   status commands: keep the selected checkout's worktree `in-review` while the
   agreed integration step remains outstanding; mark it `completed` only when
   the agreed delivery boundary has been satisfied. The engineer removes
   `plan.md` from the checkout before delivery completes.

## Rounds, Context, and Convergence

- Use a fresh Task + Dispatch for the plan draft, every plan-review round, the
  implementation, and every code-review round. This creates clean lifecycle and
  provenance boundaries. The plan draft is the Dispatch created by
  `worker-start`, not a review round.
- Reuse the same engineer terminal throughout. Its model context persists
  across rounds; a fresh Dispatch does **not** create context isolation. After
  an accepted `worker_done`, transfer that exact terminal to the next round's
  Dispatch before acknowledging the Delivery — the manager's review sits
  inside that window — or account for it under Guardrails.
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

After the interview, re-engage the user only when a fixed workflow constraint
conflicts with the resolved engineer spec or an explicit user choice, or when
the agents cannot faithfully resolve a consequential, hard-to-reverse decision
with evidence. This includes technical decisions when choosing on the user's
behalf would exceed the manager's authority. This takes precedence over the
round-limit default. Do not ask the user about implementation details the
agents can settle.

## Guardrails

- From the first Dispatch onward, never edit the engineer's selected checkout
  from the manager session, including when it is the current worktree. Neither
  agent edits another worktree or `main` as a workaround.
- `input_accepted` is a send receipt, not proof the engineer took up the prompt.
  Never infer non-delivery from `tui-idle`, a wait timeout, missing terminal
  text, or an absent heartbeat — `tui-idle` reports idle mid-turn. Take uptake
  only from positive evidence attributable to the current Dispatch: its task in
  `worker-read`, its heartbeat, or post-dispatch output. If uptake stays
  ambiguous after a bounded acknowledgement request, fence the old Dispatch
  before any retry, or report the loop blocked. Never run two Dispatches for
  the same round.
- Account for the engineer terminal on every exit. After every accepted
  `worker_done`, reuse it immediately for the next Dispatch, record an explicit
  `worker-retain` at the user's request, or call `worker-release`; never
  silently skip cleanup. On a loop exit after a succeeded or failed
  `worker_done`, release it. For an exceptional externally created
  terminal, close it only after release proves it was retained solely because
  it is external or pre-existing and no active Dispatch owns it. Never
  substitute a close for `release_pending` or `release_unknown`, whose receipts
  govern recovery. On any exit with an unsettled Dispatch — including ambiguous
  uptake, an unresolved escalation, repeated failure, or a dead terminal —
  `worker-stop` the Dispatch and follow its receipt; never release. Resolve an
  escalation and continue to settlement whenever possible; stop only when
  ending the run. Use `worker-abandon` only when the receipt leaves the outcome
  unknown, and report that residual uncertainty rather than calling the loop
  clean.
- Wait through Orca's mailbox lifecycle; do not poll terminal input. Treat wait
  timeouts as checkpoints, not automatic worker failure.
- If a Dispatch fails three times or the engineer terminal dies, report the
  blocker to the user instead of repeatedly retrying.
- Do not claim fresh-context review, successful skill composition, or runtime
  completion unless each was actually tested.
