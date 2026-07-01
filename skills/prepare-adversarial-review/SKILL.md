---
name: prepare-adversarial-review
description: Create a high-fidelity Markdown review dossier and ready-to-send launch prompt that transfer session context, decisions, artifacts, evidence, and an adaptive review mandate to a fresh independent adversarial reviewer. Use when the user wants a plan, implementation, analysis, strategy, design, research result, or other agent work prepared for second-line review; asks for a review handoff or context pack; or wants the current context-rich agent to brief a separate reviewer whose work may later be audited.
---

# Prepare Adversarial Review

## Overview

Prepare an evidence-rich handoff that lets a fresh reviewer understand the work quickly and challenge it independently. Preserve operational context without turning the original agent's framing or self-critique into the review agenda.

Produce two outputs:

1. A Markdown review dossier saved in the workspace.
2. A ready-to-send prompt that launches the adversarial review in a fresh session.

## Core Principles

- Optimize for transfer fidelity and operational continuity, not arbitrary brevity.
- Treat the dossier as a map to evidence, not as evidence by itself.
- Separate verified facts, inferences, user constraints, prior decisions, and author concerns.
- Preserve immutable user constraints while allowing the reviewer to challenge prior decisions.
- Prefer repository-relative paths and immutable identifiers; add absolute paths as same-workspace conveniences.
- Verify accessible references before listing them. Mark anything missing, stale, unverified, or inaccessible.
- Never include secrets, credentials, private data, or large copied artifacts when a safe reference is sufficient.
- Do not modify the work under review while preparing the dossier, except to create the requested dossier.
- Do not ask the user for information recoverable from the conversation, workspace, version control, commands, or linked artifacts.

## Workflow

### 1. Fix the review boundary

Identify:

- The exact plan, solution, implementation, analysis, or claim under review.
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

### 4. Derive the review mandate

Create a compact universal review baseline:

- Correctness and internal consistency.
- Fidelity to requirements and constraints.
- Hidden assumptions and unsupported claims.
- Failure modes, boundary cases, and adverse conditions.
- Security, privacy, reliability, and operational risk where relevant.
- Reproducibility, provenance, and adequacy of verification.
- Simpler alternatives and unnecessary complexity.

Then derive domain-specific attack surfaces from the actual work. Do not force every domain through a static checklist. Examples include:

- Quantitative research: lookahead and target leakage, survivorship or selection bias, overfitting, multiple testing, regime dependence, data provenance, costs and liquidity, robustness, and reproducibility.
- Software: behavioral regressions, error handling, concurrency, interfaces, state transitions, security, performance, maintainability, and missing tests.
- Infrastructure: blast radius, permissions, failure recovery, observability, idempotency, rollback, capacity, and configuration drift.
- Plans and designs: invalid premises, missing stakeholders, sequencing, feasibility, incentives, dependencies, and irreversible choices.
- Analysis and research: source quality, causal overreach, alternative explanations, sensitivity, missing counterevidence, and uncertainty.

Phrase these as areas requiring independent investigation, not conclusions the reviewer should inherit.

### 5. Write the dossier

Use a descriptive filename such as `reviews/<work-slug>-adversarial-review.md` unless the user specifies a path or the repository has an established convention. Create parent directories when needed.

Use this structure, adapting sections only when they are genuinely inapplicable:

```markdown
# Adversarial Review Dossier: <work>

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
## Required Reviewer Output
## Review Lifecycle and Third-Line Audit
## Author Self-Critique - Read Only After Independent Pass
```

Use tables where they improve scanability, especially for decisions, claims, resources, and verification. Include enough detail to prevent the reviewer from having to rediscover consequential context, but link to source artifacts instead of duplicating them wholesale.

### 6. Protect reviewer independence

In the dossier and launch prompt, instruct the reviewer to:

1. Treat all summaries and rationales as claims to verify.
2. Inspect the primary evidence.
3. Form and record an independent risk map before reading the author self-critique.
4. Avoid letting the self-critique narrow the review surface or substitute for original investigation.
5. Respect immutable user constraints but challenge prior decisions when evidence warrants it.
6. Seek disconfirming evidence and distinguish defects from preferences.
7. Remain read-only unless the user separately authorizes repairs.

Place the author self-critique last. Label it as potentially biased supplemental input. Include suspected weaknesses, uncertain reasoning, untested assumptions, and places where the author may have overfit to the conversation, but do not present them as established findings.

### 7. Specify an auditable reviewer output

State that the review will return to the original agent for response or remediation and will then be evaluated by a third-line audit agent. Require the reviewer to produce a findings-first report with:

- Findings ordered by severity and supported by precise references.
- For each finding: claim, evidence, reasoning, impact, conditions, confidence, and a concrete verification or remediation path.
- Clear separation of observed facts, inferences, and unresolved suspicions.
- Counterevidence or mitigating factors that were considered.
- Exact commands and material outputs from checks performed.
- A coverage ledger of artifacts inspected, checks run, areas not reviewed, and access limitations.
- Open questions and residual risks.
- An explicit statement when no material issue is found, without inventing findings to appear adversarial.

The report must leave enough traceability for the original agent to respond point by point and for the audit agent to evaluate the review's rigor, independence, coverage, and evidentiary support.

### 8. Generate the launch prompt

After saving the dossier, provide its path and a fenced, ready-to-send prompt. Tailor the prompt to the review object and include:

- The dossier path and repository or workspace root.
- An instruction to read the dossier and inspect primary evidence.
- The read-only, evidence-seeking mandate.
- The independent-risk-map requirement before reading the self-critique.
- The distinction between immutable constraints and challengeable decisions.
- The required findings-first, auditable output.
- Notice that the review returns to the original agent and will undergo third-line audit.
- Any environment setup or first commands needed to begin.

Use this shape:

```text
Act as the independent second-line adversarial reviewer for <work>.

Start by reading <dossier path>. The relevant workspace is <root>.
Treat the dossier as a context and evidence map, not as authoritative analysis.

<tailored investigation and independence instructions>

Your review will be returned to the original agent for response and then audited by a third-line agent. Produce an evidence-backed, findings-first report with a complete coverage ledger. Do not modify the reviewed work.
```

Do not merely tell the reviewer to "review thoroughly." Give enough operational direction to begin immediately.

## Completion Check

Before responding, verify that:

- The dossier exists at the stated path.
- The review object and version are unambiguous.
- Important paths and links are valid or clearly marked unverified.
- Facts, inferences, constraints, decisions, and self-critique are distinguishable.
- The adaptive threat model fits the work.
- The self-critique appears last and cannot silently define the review agenda.
- The reviewer output is actionable by the original agent and auditable by the third line.
- The launch prompt references the correct dossier and workspace.

Return the dossier path followed by the ready-to-send prompt.
