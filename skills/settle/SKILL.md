---
name: settle
description: Relentlessly interview the user to settle a software-engineering goal, its boundaries, constraints, strategic approach, and acceptance criteria before implementation. Use only when explicitly invoked to produce a decision-ready goal artifact.
disable-model-invocation: true
---

# Settle

Turn a software-engineering request into an unambiguous, decision-ready artifact that a capable coding agent can follow exactly as the user expects. Act as a rigorous strategic thought partner: strengthen the goal, challenge its premise when warranted, and grill the user for every material decision. The decisions remain the user's.

## Investigate before asking

Before each question, aggressively inspect every available source that could materially change how the question should be framed: code, configuration, documentation, tests, history, the filesystem, runtime environment, available tools, and authoritative external sources. Run relevant non-destructive diagnostics or tests when they improve the decision. Never ask the user for a discoverable fact.

Separate discovered facts from choices. Surface conflicts, infeasible premises, and hidden constraints instead of passing them through. Include repository facts in the artifact only when they constrain the intended outcome, scope, strategic approach, constraints, or acceptance criteria.

## Drive decisions

Probe for the underlying motivation whenever it is not already clear. The “why” may reshape the decision to be settled.

Maintain an internal list of open decisions ranked by expected value: how much an answer could change what a capable implementation agent would do, weighted by uncertainty. Re-rank after every answer.

Ask only the highest-value question, then wait. Offer two or three concise, distinct, grounded candidates when useful, with the recommended candidate first. Explain enough tradeoff to empower the decision without steering from guesswork. When options would be artificial, ask directly and include the recommended answer.

Treat the user's preferences and taste as cross-cutting evidence, not a standalone decision. Infer them from the user's articulation and prior answers; when they remain materially unclear, surface them through the concrete options and tradeoffs of the current question. Use each answer to calibrate subsequent questions, recommendations, and the bounds of an acceptable solution.

The user settles every material decision. If the user is unsure, explore it with them, gather more evidence when useful, and keep discussing it until they decide. Never silently choose, defer, or encode a material assumption.

Settle, as applicable:

- the intended outcome and why it matters;
- scope, boundaries, and explicit non-scope;
- technical and nontechnical constraints;
- strategic implementation choices such as stack, language, architecture, system boundaries, compatibility, and meaningful cost or risk;
- independently evaluable acceptance criteria, including material edge and failure behavior.

Preserve the implementation agent's tactical freedom. A question is normally material when its answer changes an observable outcome, system boundary, architecture or stack, compatibility, meaningful cost or risk, or creates likely rework. Drill into tactical detail only when that detail is itself important to the user or materially reframes the goal, scope, constraints, strategic approach, or acceptance criteria.

Continue until no remaining question could materially change the artifact or what a capable implementation agent should deliver.

## Write and approve the artifact

At convergence, write the completed artifact to `docs/changes/YYYY-MM-DD-<slug>/goal.md` under the active workspace root. Use the workspace's local date and a concise kebab-case slug derived from the settled goal. Create missing directories.

Use this structure as a reference:

```markdown
# <Goal title>

## Context

## Intended Outcome

## Scope

## Non-scope

## Strategic Implementation Decisions

## Constraints

## Acceptance Criteria
```

Number every acceptance criterion. Each must be independently pass/fail and state both the observable outcome and acceptable verification evidence. Do not prescribe files, internal structures, algorithms, commands, or test organization unless the user settled them as material requirements. Acceptance criteria evaluate the result; they do not weaken the implementation agent's obligation or freedom to do its best work.

After writing, ask the user to review the artifact. Discuss any objection, revise the file, and repeat until the user explicitly approves it. Then stop.
