---
name: to-spec
description: Turn settled session decisions into a lean and coherent spec.md defining success while leaving implementation tactics open.
disable-model-invocation: true
---

# To Spec

Synthesize the current session into the smallest coherent specification that preserves the user's intended outcome and material requirements. Typically follows a confirmed interview recap; decisions settled elsewhere in the session also qualify.

## Gate readiness

Use the session as the primary source. Investigate only to verify a material fact or suspected contradiction. Clarify unresolved ambiguity only when it changes the intended outcome, scope, constraints, or what counts as success.

Include only explicitly settled requirements and implications that follow unambiguously from them. Do not promote suggestions, plausible assumptions, or illustrative examples into obligations. Leave other choices to the implementer.

## Create the artifact

Use the workspace's local date and a concise kebab-case slug for `docs/changes/YYYY-MM-DD-<slug>/spec.md`.

Use this envelope:

```markdown
# <Spec title>

- **Schema:** `to-spec/v1`

> This file is the contract guiding the work. Do not edit or commit it.
> Never satisfy a requirement technically while violating its intended outcome.
> Pausing should be rare. If strong evidence shows the agreed requirements must change, the user
> explicitly requests `update_goal(status="paused")`. Explain the
> evidence and proposed revision, then stop; the user decides and resumes the goal.

## Outcome

<The intended result.>

## Acceptance Criteria

- `AC-001` <Observable pass/fail condition.>
```

- Require only Outcome and Acceptance Criteria. Add concise Context, Scope, Non-goals, Settled Decisions, or Constraints and Dependencies between them when needed to interpret success or preserve a material boundary. Omit empty sections.
- Give criteria consecutive `AC-###` identifiers. Define observable success; specify evidence only when explicitly settled or necessary to define success. Otherwise leave proof methods open.
- Leave files, internal structures, algorithms, sequencing, commands, and test organization to the implementer unless explicitly settled as material requirements. Do not invent discovery scenarios, exception thresholds, or approval rules.

Draft the exact artifact in a temporary file named `spec.md` and validate it with
`python3 <skill-directory>/scripts/validate-spec.py <temporary-spec.md>`. Audit the substance for unsupported requirements and repetition; structural validation does not establish readiness. Write the validated bytes to the target and validate it again.

Finish by staging the artifact and reporting its path and successful validation.
