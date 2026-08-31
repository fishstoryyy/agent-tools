# Goal Contract Schema

`goal/v1` is the repository-agnostic envelope for an accepted change contract. It defines the
implementation boundary without prescribing a plan. Keep the required headings in order, but use
whatever prose, lists, tables, code, references, or subordinate organization best expresses the
particular change.

## Canonical envelope

```markdown
# <Change Title>

- **Schema:** `goal/v1`
- **Starting commit:** `<full SHA>`

> **Execution:** This is the accepted outcome contract, not an implementation plan. Keep all
> contract text above Implementation Notes unchanged. The implementing agent owns every decision
> not explicitly constrained here and should choose the best means to satisfy every acceptance
> criterion. Only append an Implementation Note when a strategic deviation from the settled approach
> is absolutely unavoidable under the policy below.

## Desired Outcome

<What should become true and why the current state is insufficient.>

## Scope

### In scope

<Included outcomes, behaviors, surfaces, or change boundaries.>

### Non-goals

<Explicitly excluded outcomes or boundaries.>

## Settled Decisions and Constraints

<Only decisions, rationale, and constraints that materially bound an acceptable solution.>

## Acceptance Criteria

- `AC-001` <Observable condition>. **Evidence obligation:** <Required kind and strength of proof.>

## Unresolved Unknowns

- None.

## Implementation Notes

This section is initially empty and is the only mutable part of this file. Replace `- None.` with a
consecutive `IN-###` record only when reasonable investigation shows that compliance with a settled
decision is truly impossible. Routine discoveries, progress, and ordinary implementation choices do not belong here. A note should have an extremely high bar and may authorize only the narrowest necessary
amendment. It must keep the desired outcome and non-goals intact, explain why the amendment is
unavoidable, show that it does not materially reduce user value or verification strength, and specify
replacement evidence. 99% of the time this section will remain empty after the implementation, because the strategic decisions have been carefully settled beforehand.

- None.
```

## Acceptance evidence

Each `AC-###` must be observable and falsifiable. State the proof obligation at the level needed to
judge completion while preserving implementation freedom. Name an exact command, tool, artifact, or
reviewer only when an existing authority or genuine constraint makes that mechanism part of the
contract. The complete set of acceptance criteria is the contract's implementation stopping
condition.

## Unknowns

A material unknown is not allowed. Every remaining unknown must be non-blocking and state how or by
whom it will be resolved and the condition that requires escalation. Use `- None.` when none remain.

## Implementation-note records

The initial goal-only commit must contain `- None.`. During implementation, that marker may be
replaced only with consecutive records in this compact shape:

```markdown
- `IN-001`
  - **Affected decision:** <The settled decision that cannot be followed.>
  - **Why unavoidable:** <Evidence that compliance became impossible.>
  - **Alternatives attempted or ruled out:** <Reasonable compliant options investigated.>
  - **Minimal deviation:** <The narrowest exception taken.>
  - **Outcome protection:** <Why the desired outcome and non-goals remain intact and user value and verification strength are not materially reduced.>
  - **Verification evidence:** <Replacement evidence that the amended path satisfies the contract.>
```

Contract text above `Implementation Notes` remains unchanged. These records document and authorize
only unavoidable, evidence-backed deviations or narrow amendments permitted by the policy; they do
not silently rewrite the contract or redefine success.
