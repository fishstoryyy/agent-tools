---
name: solidify
description: Finalize an articulated software change through evidence-led challenge, resolve every material goal and normative implementation ambiguity, then create a validated goal contract and goal-only Git commit ready for Codex Goal mode. Use after goal discovery or whenever a change needs an implementation-ready contract; do not use for tactical planning or implementation.
disable-model-invocation: true
---

# Solidify

Turn the user's current articulation into an accepted, implementation-ready change contract. The
goal-only commit—not completion of an upstream interview—is the phase boundary. Reuse sound prior
decisions, including a `grill-the-goal` brief when one exists, but own every remaining readiness gap.

## Resolve the contract

1. Inspect the repository and other available evidence before forming important opinions. Find
   discoverable facts yourself and combine them with relevant domain knowledge.
2. Expose unsupported assumptions, contradictions, implications, and material tradeoffs. Resolve
   both goal-level gaps and normative implementation choices when they constrain an acceptable
   solution. Do not repeat settled discovery unless evidence puts it in doubt.
3. Rank open decisions by how much their answers could change the contract, weighted by uncertainty.
   Ask the highest-value question first, one decision per turn, and reassess after every answer.
   Offer two or three distinct options with the recommended option first when that aids judgment.
4. Preserve implementation freedom. Settle architecture, ownership boundaries, compatibility,
   migration commitments, risk and permission limits, and verification obligations only when they
   materially bound success. Do not produce a file-by-file plan, task sequence, or tactical design.

Do not end the inquiry while a material concern remains. A material concern is any unresolved issue
that could change the desired outcome, scope, non-goals, hard constraints, acceptable solution space,
or acceptance evidence. Investigating and resolving it is Solidify's responsibility. A factual
unknown may survive only when it cannot block safe progress and the contract states how it will be
resolved and when it must be escalated.

Every completed invocation produces the contract and commit below; do not apply a task-size
threshold.

## Draft and confirm

1. Read [the goal contract schema](references/goal-schema.md) completely.
2. Inspect `HEAD`, the index, and the working tree. Preserve all unrelated staged, unstaged, and
   untracked work. Stop with a precise explanation if relevant implementation has already begun
   without an accepted contract or the target path already exists.
3. Record the full current `HEAD`, derive a concise kebab-case change identity, and target only
   `docs/changes/YYYY-MM-DD-<slug>/goal.md`.
4. Synthesize a self-contained `goal/v1` contract. Include only material decisions and constraints.
   Make every acceptance criterion observable and state the required kind and strength of evidence,
   while leaving the exact proof mechanism to the implementing agent unless an authoritative process
   or genuine constraint fixes it.
5. Validate the exact draft outside the target path with
   `python3 <skill-directory>/scripts/validate-goal.py <temporary-goal.md>`. Structural success does
   not establish semantic readiness; audit the substance yourself against the standard above.
6. Present the exact validated draft, target path, validation result, and intended commit message as
   the single final recap. Ask for explicit confirmation and wait. If the user changes a decision,
   resume the inquiry rather than patching around it.

Do not create the target file or commit before that confirmation.

## Materialize the boundary

1. Confirm that `HEAD` still matches the approved draft's starting commit. If it changed, inspect the
   delta, refresh the contract, revalidate it, and obtain confirmation again.
2. Write the exact approved bytes to the new target path and validate it again.
3. Stage the target and use a path-limited commit so unrelated index entries remain untouched. Follow
   the repository's commit-message conventions; when none exist, use
   `docs(goal): add <change identity>`.
4. Verify that the new commit contains exactly `goal.md`, that its committed bytes match the approved
   draft, and that unrelated working-tree and index state was preserved. Do not rewrite history or
   attempt destructive recovery if a hook or concurrent change violates an invariant; report the
   exact state.
5. Announce only the committed artifact path and commit SHA, plus that it is ready for Goal mode.
   Do not generate a Goal-mode prompt, activate a goal, or start implementation.
