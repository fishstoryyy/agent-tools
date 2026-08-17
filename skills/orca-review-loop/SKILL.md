---
name: orca-review-loop
description: Run an explicitly invoked Orca review loop over the invoking agent's completed work. The main agent keeps ownership of all edits, artifacts, validation, and the final response while two or three read-only reviewer agents independently invoke adversarial-review, challenge the work, and re-review repairs until no material finding remains. Use only when the user explicitly invokes orca-review-loop; honor any reviewer agents, models, thinking levels, shared or reviewer-specific focus, and other review notes in that invocation.
disable-model-invocation: true
---

# Orca Review Loop

Act as the main agent. Review a concrete candidate you already completed; do not
use this workflow to delegate implementation or to review work that does not yet
exist.

This skill defines review policy, not Orca mechanics. Confirm that `orca-cli`
and `adversarial-review` are discoverable. Use `orca-cli` to resolve the correct
Orca executable, then fetch and follow the version-matched guides. Replace
`<ORCA>` with the resolved executable; never run the placeholder literally.

```bash
<ORCA> skills get orchestration
<ORCA> skills get orca-cli
```

The fetched guides own command syntax, receipts, structured messaging,
settlement, retry, and cleanup. Favor native Orca operations throughout.

## Contract

- **Main agent:** owns the work under review, every repair, validation, the
  review packet and findings record, orchestration, and the final user response.
- **Reviewers:** inspect only. They may run genuinely non-mutating checks, but
  never edit the checkout or packet. They propose any check that could write,
  generate files, or contend with another reviewer; the main agent runs it.
- Use the current worktree or folder so reviewers see the completed candidate.
  Do not create reviewer worktrees merely for isolation.
- Review only the declared target. Preserve and exclude unrelated staged,
  unstaged, and untracked work.
- Reviewer questions go to the main agent. Only the main agent may ask the user
  for a missing decision.

If there is no review-ready candidate, stop before provisioning reviewers and
ask the user to invoke the skill after the work exists.

## Resolve the Panel

Accept exactly two or three reviewers. If the user provides no panel, use two
fresh OMP reviewers with native defaults. Interpret reviewer descriptions
semantically: explicit agent, model, and thinking or effort values apply to that
reviewer; omitted values use that agent's native defaults. Do not infer values
from unrelated configuration.

Pass requested launch preferences only through paths supported by the fetched
guides and verify the effective receipt. Follow the guide's recovery path when
Orca does not honor them. Never substitute a different configuration silently;
if the requested panel remains unavailable, ask the user to choose an explicit
alternative or native defaults.

Give every reviewer the same review target and rubric unless the user assigns
reviewer-specific focuses. User review notes augment the review; they do not
weaken `adversarial-review`.

## Prepare the Review

Create a minimal temporary directory outside the repository. Keep a main-owned
review packet and findings record there. Include only what reviewers need:

- the user's request, intended outcome, constraints, and review focus;
- the exact target and scope, including relevant paths or artifacts;
- the completed candidate and intended user-facing response, or references to
  them when they already exist;
- checked validation evidence, material claims, and known limitations.

Do not copy secrets or unnecessary sensitive data. Prefer scoped references to
existing files. If safe access cannot establish enough evidence, record and
disclose the limitation.

Keep each injected task short and point it to the packet. Large multiline
injections are more likely to land without submission. Create every independent
review task, then start all reviewers in parallel before waiting. Give each
reviewer one long-lived Task and Dispatch for the entire loop.

The task must require the reviewer to:

1. make its first act a Dispatch-scoped `status` message that says `accepted`
   or `rejected` and cites both Task and Dispatch IDs;
2. remain filesystem-read-only and invoke `adversarial-review` against the
   packet and current target;
3. report every substantive review result through Dispatch-scoped `status`, not
   only through `worker_done`;
4. keep the Dispatch open and wait through the Orca mailbox for structured
   follow-ups; and
5. emit a final `ship` verdict through `status` before calling `worker_done`.

Do not expose peer findings until all independent first passes arrive.

## Review and Repair

1. Collect each independent `adversarial-review` result. A valid pass may return
   `ship`; never require manufactured findings.
2. Merge material findings into the record without erasing attribution or
   disagreement. Share that record with every reviewer through structured
   Dispatch messaging; reviewers do not message each other directly.
3. For each finding, repair the work or answer with evidence. Ask the originating
   reviewer to re-evaluate a rejected finding. If disagreement persists, run the
   cheapest decisive falsification test before escalating.
4. Validate every repair, update the packet and record, then ask all reviewers
   to re-check resolved findings, changed areas, and likely regressions. Do not
   mechanically repeat analysis of unaffected areas.
5. Before final approval, every reviewer inspects the complete current target,
   shared record, validation evidence, and intended response. Convergence
   requires a current `ship` verdict from every panel seat with no
   unresolved P1 or P2 finding. Non-material preferences may remain.

The independent first pass does not count toward the limit. Allow at most three
main-agent repair and re-review rounds; a round that reveals a regression still
counts. A material change after every reviewer says `ship` invalidates
convergence and requires re-review within the same limit.

If a reviewer still refuses `ship` after the limit, never call the result
converged. The main agent may close a reversible disagreement only with decisive
evidence and must report `closed without unanimous convergence` plus the
dispute. Ask the user about any consequential or inconclusive unresolved issue.

## Delivery Reliability

An injected task and its lifecycle capability can arrive separately. The
reviewer's first-act acceptance proves both are live; rejection exposes the
failure before settlement.

Never treat input-side state as proof of uptake: `input_accepted`, prompt text
in scrollback or a composer, TUI idle, and a running terminal can all be green
while no turn runs. Count only output-side evidence attributable to the current
Dispatch, such as an assistant turn, tool use, context consumption, or a
received message.

Require first contact within roughly one minute. If no turn started, triage
before repair:

- An empty composer means the injection was swallowed. Fence the old Dispatch
  and relaunch through the fetched guide's structured recovery path.
- A full composer means the injection landed but was not submitted. Send only
  the submit keystroke, with no new prompt text. Re-sending the task would
  re-author the payload and can discard its lifecycle capability.

When a structured delivery fails, repair or resend it structurally. Never drop
to raw terminal input for a task or follow-up whose Dispatch structure matters.
Treat later work wait timeouts as checkpoints, not failures.

If a reviewer session fails irrecoverably before leaving a current substantive
result, replace it under the fetched guide with the full packet and findings
record; require a complete pass from the replacement and disclose the
substitution. If its current result is already durable in `status`, preserve the
work and use the guide only to settle or clean up the broken lifecycle. Do not
leave duplicate Dispatches for one panel seat.

## Finish

Settle every Dispatch and account for every reviewer terminal under the fetched
guides. On a non-converged exit, stop unsettled Dispatches through the guide
rather than manufacturing `worker_done`.

Report the resolved reviewer configurations, material findings and repairs,
validation performed, reviewer replacements or evidence limitations, and one
of: `converged`, `closed without unanimous convergence`, or `blocked`.
Do not expose orchestration transcripts or operational noise.

After settlement, remove the temporary review directory unless the user asked
to retain it. If retained, report its path.
