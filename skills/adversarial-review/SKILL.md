---
name: adversarial-review
description: Stress-test a plan, design, or implementation from first principles, identify its strongest plausible failure modes, and propose the cheapest falsification test for each. Use when the user explicitly asks for an adversarial review, stress test, first-principles critique, or asks where something would fail; also use when an active workflow assigns an adversarial review gate. Distinct from `prepare-adversarial-review`, which packages a handoff for a fresh reviewer; this skill performs the review inline.
---

# Adversarial Review

Find where the artifact is wrong before reality does. Review read-only unless
the user explicitly asks for fixes. Match depth to stakes: give a small,
reversible change a short pass; reserve the full apparatus for consequential or
hard-to-reverse work.

## Establish the Target

Identify the artifact, intended outcome, scope, constraints, and evidence that
would establish success. Separate checked evidence from inference. Do not attack
requirements or scope the user did not choose.

## Choose the Lens

For a **plan or design**:

1. Strip away analogies and conventional implementation choices.
2. List the irreducible facts and constraints. Label each **hard constraint**,
   **cost**, or **convention**.
3. Rebuild the smallest viable approach from those facts.
4. Compare it with the proposed approach; treat unnecessary convention as a
   deletion candidate, not an automatic defect.

For an **implementation**:

1. Establish the intended behavior and review scope.
2. Inspect the relevant diff, affected paths, tests, and validation evidence.
3. Trace likely failure paths through the changed behavior and its integration
   boundaries.
4. Use the deeper first-principles decomposition only when an architectural
   premise—not merely an implementation detail—is in doubt.

## Attack the Strongest Version

Find up to three strongest plausible failure modes. Hidden coupling, a wrong
premise, integration cost, hostile inputs, and missing validation are examples,
not a required checklist. One strong finding is better than three weak ones.

For each finding:

- State what breaks, when, and who notices.
- Mark it `evidence` when checked or `inference` when reasoned.
- Assign `P1` only if it can sink the result; use `P2` when recovery is practical.
- Propose the cheapest hostile-path test that would confirm or kill the concern
  before more effort is spent.

Attack the strongest reasonable interpretation, not a strawman. Search hard for
a meaningful failure, but accept that the correct verdict may be `ship`; never
manufacture objections for completeness.

## Output

```markdown
## Verdict
[ship | needs-attention | no-go] — one-sentence decision

## Irreducible Facts
- [fact] — hard constraint | cost | convention

## Attack Points
1. [P1|P2] [evidence|inference] [concrete failure]
   Falsification: [cheapest hostile-path test]

## What Survives
- [part that withstood review]

## Recommended Changes
- [change tied to an attack point]
```

Omit empty sections. Recommend changes; do not apply them unless asked.
