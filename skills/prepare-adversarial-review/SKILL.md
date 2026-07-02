---
name: prepare-adversarial-review
description: Create a proportional, high-fidelity Markdown dossier and concise ready-to-send launch prompt for either a fresh adversarial reviewer or a third-line audit agent. Use when the user wants a plan, implementation, analysis, strategy, design, research result, or other agent work prepared for independent review; asks for a review handoff or context pack; or wants a completed adversarial review prepared for an independent audit session.
---

# Prepare Adversarial Review

## Overview

Prepare an evidence-rich handoff that lets a fresh evaluator understand the relevant work quickly and assess it independently. Preserve operational context without turning the preparing agent's framing or self-critique into the evaluation agenda.

Produce two outputs:

1. A Markdown review dossier saved in the workspace.
2. A concise ready-to-send prompt that points the next agent to the dossier.

## Core Principles

- Optimize for transfer fidelity and operational continuity, not arbitrary brevity.
- Put all context, evidence, constraints, process instructions, and output expectations in the dossier. Treat it as the complete handoff artifact.
- Keep the launch prompt as a pointer, not a second handoff document. Do not repeat or summarize dossier content in it.
- Require the receiving evaluator to save the substantive report as Markdown. Treat that file, not the chat response, as the canonical review or audit artifact.
- Close the loop with a concise relay prompt that points the upstream agent to the report and asks it to respond or improve the work.
- Scale depth and structure to the complexity, risk, and context actually present. A short conversation or simple change should produce a short dossier.
- Treat every checklist and section list in this skill as a menu of considerations, not a quota.
- Omit inapplicable material without creating empty sections or inventing constraints, decisions, alternatives, risks, or verification.
- Use best judgment to emphasize what will materially help the next agent become effective.
- Aim to discover real defects, material risks, consequential omissions, and plausible failure modes, not to maximize the number of findings. Do not elevate personal taste, cosmetic nits, harmless deviations, or remote hypotheticals unless they create a meaningful problem.
- Treat the dossier as a map to evidence, not as evidence by itself.
- Separate verified facts, inferences, user constraints, prior decisions, and preparer concerns when those distinctions matter.
- Preserve immutable user constraints while allowing the receiving evaluator to challenge prior decisions.
- Prefer repository-relative paths and immutable identifiers; add absolute paths as same-workspace conveniences.
- Verify accessible references before listing them. Mark anything missing, stale, unverified, or inaccessible.
- Never include secrets, credentials, private data, or large copied artifacts when a safe reference is sufficient.
- Do not modify the work under review while preparing the dossier, except to create the requested dossier.
- Do not ask the user for information recoverable from the conversation, workspace, version control, commands, or linked artifacts.

## Choose the Handoff Stage

Infer the stage from context. Ask only when the intended recipient is genuinely ambiguous.

- **Second-line review:** Prepare the original work for an independent adversarial reviewer. The review will return to the original agent for response or remediation.
- **Third-line audit:** Prepare a completed adversarial review for an independent audit agent. Include the original work and prior dossier as underlying evidence so the auditor can assess the review's rigor, independence, coverage, fairness, and evidentiary support.

In audit mode, treat the completed review as the primary object under evaluation and the original work as necessary reference evidence. Adapt role labels throughout: reviewer becomes preparer, and auditor becomes receiving evaluator.

## Workflow

### 1. Fix the evaluation boundary

Identify:

- The exact plan, solution, implementation, analysis, claim, or completed review under evaluation.
- Its current state: proposed, partially implemented, completed, tested, or deployed.
- The version being reviewed: repository, branch, commit, worktree state, document version, dataset snapshot, or timestamp as applicable.
- What is in scope, out of scope, and explicitly deferred.

If the worktree is dirty, record that fact and identify the relevant diff. Do not silently treat `HEAD` as the reviewed version.

### 2. Reconstruct the decision record

Recover the context that materially shaped the work:

- User objective and success criteria.
- Requirements and preferences.
- Immutable constraints.
- Decisions made and their rationale.
- Alternatives considered or rejected and why.
- Assumptions, dependencies, and unresolved questions.
- Changes in direction during the session.

Classify genuine constraints separately from challengeable decisions. Prior agreement is not proof that a decision is sound.

### 3. Build and verify the evidence map

Inspect the available workspace and record the resources needed to review independently:

- Relevant files and directories.
- Repository root, remote, branch, commit, and relevant diffs.
- Plans, specifications, issues, pull requests, documentation, and external links.
- Tests, logs, commands, outputs, benchmarks, notebooks, reports, and generated artifacts.
- Data sources, schemas, sampling windows, configurations, dependencies, and environments.
- Prior verification and its exact results, including failures and skipped checks.

For each important resource, provide its role, locator, version or freshness, and accessibility. Use repository-relative paths first, then absolute paths when useful. Include a small essential excerpt only when the next agent may not be able to access the source and the excerpt is safe to reproduce.

Never imply that a command was run, a link was read, or a result was verified when it was not. Label recollection from conversation separately from inspected evidence.

### 4. Derive the evaluation mandate

Select only relevant concerns from a compact universal baseline:

- Correctness and internal consistency.
- Fidelity to requirements and constraints.
- Hidden assumptions and unsupported claims.
- Failure modes, boundary cases, and adverse conditions.
- Security, privacy, reliability, and operational risk where relevant.
- Reproducibility, provenance, and adequacy of verification.
- Simpler alternatives and unnecessary complexity.

Then derive domain-specific attack surfaces from the actual work when useful. Do not force every domain through a static checklist. Examples include:

- Quantitative research: lookahead and target leakage, survivorship or selection bias, overfitting, multiple testing, regime dependence, data provenance, costs and liquidity, robustness, and reproducibility.
- Software: behavioral regressions, error handling, concurrency, interfaces, state transitions, security, performance, maintainability, and missing tests.
- Infrastructure: blast radius, permissions, failure recovery, observability, idempotency, rollback, capacity, and configuration drift.
- Plans and designs: invalid premises, missing stakeholders, sequencing, feasibility, incentives, dependencies, and irreversible choices.
- Analysis and research: source quality, causal overreach, alternative explanations, sensitivity, missing counterevidence, and uncertainty.

For a third-line audit, consider whether the review was independent, sufficiently scoped, evidence-backed, reproducible, proportionate, fair to counterevidence, clear about limitations, and capable of surfacing material issues. Check for unsupported findings and consequential risks the review missed.

Phrase all suggested attack surfaces as optional starting points for independent investigation, not boundaries or conclusions the receiving agent should inherit. Explicitly invite the receiving agent to identify important risks outside the dossier's framing.

### 5. Write the dossier

Use a descriptive filename such as `reviews/<work-slug>-adversarial-review.md` for second-line review or `reviews/<review-slug>-audit.md` for third-line audit, unless the user specifies a path or the repository has an established convention. Create parent directories when needed.

Choose, combine, rename, or omit sections according to the situation. Do not add `N/A` placeholders. A simple review may need only an orientation, review object, evidence map, mandate, and output request. A complex review may benefit from the fuller menu below:

```markdown
# Evaluation Dossier: <work or review>

## Review Mandate
## Executive Orientation
## Review Object and Version
## Objectives and Acceptance Criteria
## Scope, Non-Goals, and Deferred Work
## Immutable Constraints
## Decisions and Rationale
## Alternatives Rejected
## Implementation or Solution Walkthrough
## Claims Requiring Verification
## Evidence and Resource Map
## Verification Already Performed
## Adaptive Threat Model
## Known Gaps and Access Limitations
## Independence Protocol
## Requested Evaluation Output
## Review Lifecycle and Third-Line Audit
## Preparer Self-Critique - Read Only After Independent Pass
```

Use tables where they improve scanability, especially for decisions, claims, resources, and verification. Include enough detail to prevent the reviewer from having to rediscover consequential context, but link to source artifacts instead of duplicating them wholesale.

### 6. Protect evaluator independence

In the dossier and launch prompt, instruct the receiving reviewer or auditor to:

1. Treat all summaries and rationales as claims to verify.
2. Inspect the primary evidence.
3. Begin with an independent assessment before reading the preparer's self-critique. For complex work, record an initial risk or audit map; for simple work, do not add ceremony solely to satisfy this step.
4. Avoid letting the dossier's threat model or self-critique narrow the evaluation surface or substitute for original investigation.
5. Respect immutable user constraints but challenge prior decisions when evidence warrants it.
6. Seek disconfirming evidence and distinguish defects from preferences.
7. Remain read-only unless the user separately authorizes repairs.

When meaningful self-critique exists, place it last and label it as potentially biased supplemental input. Include suspected weaknesses, uncertain reasoning, untested assumptions, and places where the preparer may have overfit to prior context, but do not present them as established findings. Omit this section when there is no useful self-critique rather than manufacturing one.

### 7. Specify an auditable output and return handoff

Require the receiving evaluator to produce two outputs:

1. A substantive Markdown report saved in the workspace.
2. A concise ready-to-send relay prompt for the upstream agent.

Use the repository's established artifact location when one exists. Otherwise, suggest a clear path such as `reviews/<work-slug>-review-report.md` for second-line review or `reviews/<review-slug>-audit-report.md` for third-line audit. The evaluator must verify that the file exists before responding.

For second-line review, state that the report will return to the original agent for response or remediation and will then be evaluated by a third-line audit agent. Request a findings-first report scaled to the work's complexity and risk. Use the following as guidance, not mandatory fields for trivial observations:

- Material findings ordered by severity and supported by precise references.
- Enough evidence, reasoning, impact, conditions, confidence, and verification or remediation detail to make each material finding actionable.
- Clear separation of observed facts, inferences, and unresolved suspicions.
- Relevant counterevidence or mitigating factors.
- Exact commands and material outputs when checks were performed.
- A proportionate coverage note identifying what was inspected, what was not, and meaningful access limitations.
- Open questions and residual risks when any remain.
- An explicit statement when no material issue is found, without inventing findings to appear adversarial.

Separate optional improvements from actual findings and omit trivial nits that would not meaningfully improve correctness, safety, reliability, maintainability, or fitness for purpose. The report must leave enough traceability for the original agent to respond point by point and for the audit agent to evaluate the review's rigor, independence, coverage, and evidentiary support.

For third-line audit, require an audit-first report that evaluates the completed review itself. Cover material omissions, unsupported or overstated findings, evidence quality, reproducibility, independence, scope, proportionality, treatment of counterevidence, and usefulness to the original agent. Distinguish defects in the review from newly discovered defects in the underlying work.

After saving the report, require the evaluator's chat response to contain only:

- The report path.
- A fenced relay prompt of two to four short sentences and no more than 100 words.

For second-line review, address the relay prompt to the original agent. Tell it to read the report, address each material finding, improve the work where warranted, verify the changes, and document evidence-backed disagreements. For third-line audit, address the relay prompt to the reviewed reviewer and tell it to read the audit report and strengthen or correct the review. Do not repeat the findings in the relay prompt.

Use these shapes:

```text
Read and act on <review report path>. Address each material finding, improve the work where warranted, verify the changes, and document any evidence-backed disagreement. Keep the report as the source of truth rather than relying on this prompt.
```

```text
Read and act on <audit report path>. Correct unsupported findings, investigate material omissions, and strengthen the review with traceable evidence. Keep the audit report as the source of truth rather than relying on this prompt.
```

### 8. Generate the launch prompt

Before generating the prompt, ensure the dossier itself contains everything the receiving agent needs to restore context, begin work, preserve independence, and produce the requested output. If the prompt seems to need substantive explanation, move that explanation into the dossier.

After saving the dossier, provide its path and a fenced, ready-to-send prompt. Default to two to four short sentences and no more than 100 words. Include only:

- The receiving role.
- The dossier path.
- An instruction to read and follow the dossier as the complete context and mandate.
- A brief instruction to work independently and inspect primary evidence.
- A brief instruction to save the report as Markdown and return its path plus a concise relay prompt.

Add access or environment setup only when the agent cannot reach the dossier without it. Do not restate the objective, decisions, evidence map, threat model, lifecycle, detailed review method, or output schema.

Use one of these shapes:

```text
Act as the independent second-line adversarial reviewer. Read and follow <dossier path>; it contains the complete context and mandate. Work independently and verify primary evidence. When finished, save the review as Markdown and reply only with its path and a concise prompt for the original agent.
```

```text
Act as the independent third-line audit agent. Read and follow <dossier path>; it contains the complete context and mandate. Audit independently and verify primary evidence. When finished, save the audit as Markdown and reply only with its path and a concise prompt for the reviewed agent.
```

Do not add a miniature dossier to the prompt.

## Completion Check

Before responding, verify that:

- The dossier exists at the stated path.
- The handoff stage, evaluation object, and relevant version are clear enough for the task.
- Important referenced paths and links are valid or clearly marked unverified.
- Facts and inferences are distinguishable; constraints, decisions, and self-critique are separated when they exist.
- Any suggested threat model fits the work without limiting independent investigation.
- Any self-critique appears last and cannot silently define the evaluation agenda.
- The requested output is useful to its recipient and auditable when applicable.
- The dossier requires the receiving evaluator to save a canonical Markdown report and verify that it exists.
- The dossier requires a concise relay prompt addressed to the correct upstream agent.
- The launch prompt references the correct dossier and workspace.
- The dossier is sufficient without supplemental context from the launch prompt.
- The launch prompt is concise and does not duplicate the dossier.

Apply these checks proportionally. Do not add content solely to satisfy a checklist item that is irrelevant to the actual handoff.

Return the dossier path followed by the ready-to-send prompt.
