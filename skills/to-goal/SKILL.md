---
name: to-goal
description: Serve as a decision-readiness gate and synthesize the current session into a decision-complete artifact to guide implementation.
disable-model-invocation: true
---

# To Goal

Turn the current session context into a decision-complete contract for the implementer. This is a synthesis and readiness gate, not another grilling interview.

## Gate readiness

Treat the current session context as the primary source. Perform only targeted investigation when needed to verify a material fact or suspected contradiction.

If any of intended outcome, scope, non-goals, settled strategic decisions, technical and nontechnical constraints or dependencies, and acceptance criteria remain unclear or there are ambiguities that could cause the implementer to make material assumptions on behalf of the user, return to the user for clarification.

## Create the artifact

Use the workspace's local date and a concise kebab-case slug to target `docs/changes/YYYY-MM-DD-<slug>/goal.md`.

Draft the exact artifact in a temporary location named `goal.md`, validate it with
`python3 <skill-directory>/scripts/validate-goal.py <temporary-goal.md>`, then write the validated
bytes to the target and validate the target again.

Validation establishes conformance to the envelope, not semantic readiness; audit the substance
yourself.

Use this exact envelope:

```markdown
# <Goal title>

- **Schema:** `to-goal/v1`

## Context

## Intended Outcome

## Scope

## Non-goals

## Settled Decisions

## Constraints and Dependencies

## Acceptance Criteria

- `AC-001` <Observable pass/fail condition>. **Evidence:** <Proportionate proof obligation.>
```

Keep the artifact self-contained and proportionate to the task:

- Explain the relevant current state and why the change matters, without replaying the conversation.
- Include only outcomes and boundaries that constrain an acceptable solution. Use `- None.` when a required boundary section genuinely has no material content.
- Record rationale only when it is needed to interpret a settled decision correctly.
- Give acceptance criteria unique, consecutive `AC-###` identifiers. Make each criterion observable and falsifiable, and state the kind and strength of evidence needed to judge it.
- Preserve the implementing agent's tactical freedom. Do not prescribe files, internal structures, algorithms, work sequence, commands, or test organization unless the session explicitly settled them as material requirements.

Treat `goal.md` as read-only during implementation. Leave uncommitted. Finish by reporting the artifact path and successful validation.
