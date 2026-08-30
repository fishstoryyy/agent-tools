# Agent Tools

[![Validate](https://github.com/fishstoryyy/agent-tools/actions/workflows/validate.yml/badge.svg)](https://github.com/fishstoryyy/agent-tools/actions/workflows/validate.yml)

Personal open-source toolkit for agent skills and other agentic tools.

## Repository Layout

```text
agent-tools/
  skills/
    adversarial-review/
      SKILL.md
      agents/openai.yaml
    budget-grill-me/
      SKILL.md
      agents/openai.yaml
    build-context-to-do-something/
      SKILL.md
      agents/openai.yaml
    context-handoff/
      SKILL.md
      agents/openai.yaml
    create-session-handoff/
      SKILL.md
      agents/openai.yaml
    explain-like-rookie/
      SKILL.md
      agents/openai.yaml
    grill-me-companion/
      SKILL.md
      agents/openai.yaml
    grill-me-full/
      SKILL.md
      agents/openai.yaml
    grill-the-goal/
      SKILL.md
      agents/openai.yaml
    grill-me-light/  # Intent and acceptance-contract grilling
      SKILL.md
      agents/openai.yaml
    grill-me-ten/
      SKILL.md
      agents/openai.yaml
    mastermind/
      SKILL.md
      agents/openai.yaml
    orca-two-agent-loop/
      SKILL.md
      agents/openai.yaml
    prepare-adversarial-review/
      SKILL.md
      agents/openai.yaml
    prepare-adversarial-review-light/
      SKILL.md
      agents/openai.yaml
    session-companion/
      SKILL.md
      agents/openai.yaml
    solidify/
      SKILL.md
      agents/openai.yaml
    teach-me/
      SKILL.md
      agents/openai.yaml
  tools/
  templates/
  docs/
  scripts/
```

## Skills

| Skill | Description |
| --- | --- |
| [`adversarial-review`](skills/adversarial-review/SKILL.md) | Inline, evidence-grounded stress testing for plans, designs, and implementations. |
| [`budget-grill-me`](skills/budget-grill-me/SKILL.md) | Budgeted interview (at most six questions) to sharpen the intent behind a prompt, plan, or design; ranks open decisions by expected value and stops early once nothing more would change what the agent does. |
| [`build-context-to-do-something`](skills/build-context-to-do-something/SKILL.md) | Minimum-sufficient context prompts for capable fresh agents performing user-specified tasks. |
| [`context-handoff`](skills/context-handoff/SKILL.md) | Tight, self-contained prompts for handing work to a fresh agent or session. |
| [`create-session-handoff`](skills/create-session-handoff/SKILL.md) | Durable workspace handoffs for continuing active work in a fresh session. |
| [`explain-like-rookie`](skills/explain-like-rookie/SKILL.md) | Source-verified, rookie-friendly explanations that pair claims with their practical significance and use concrete examples or a TL;DR when helpful. |
| [`grill-me-companion`](skills/grill-me-companion/SKILL.md) | Deprecated — superseded by [`session-companion`](skills/session-companion/SKILL.md). Read-only coaching for understanding and steering a separate Claude Code or OMP session. |
| [`grill-me-full`](skills/grill-me-full/SKILL.md) | Thorough, unbudgeted interview to sharpen a request, plan, design, or prompt intent; ranks open decisions by expected value and continues until the agent and user share the same understanding. |
| [`grill-the-goal`](skills/grill-the-goal/SKILL.md) | Goal-focused interviewing that produces decision-ready briefs by clarifying relevant context, actors, sources, outcomes, success evidence, tradeoffs, constraints, and unknowns without entering implementation planning. |
| [`grill-me-light`](skills/grill-me-light/SKILL.md) | Budgeted interview (at most ten questions) that aligns intent and defines an evidence-backed acceptance contract before execution, then maps each criterion to validation results. |
| [`grill-me-ten`](skills/grill-me-ten/SKILL.md) | Budgeted interview (at most ten questions) to sharpen a request, plan, design, or prompt intent; ranks open decisions by expected value and stops early once nothing more would change what the agent does. |
| [`mastermind`](skills/mastermind/SKILL.md) | Explicit-only investigative thought partnership that helps uncover the underlying long-term objective and choose the best-supported direction toward it, without closing detailed implementation decisions. |
| [`orca-two-agent-loop`](skills/orca-two-agent-loop/SKILL.md) | Orca-native manager-engineer workflow with adversarial plan and implementation review. |
| [`prepare-adversarial-review`](skills/prepare-adversarial-review/SKILL.md) | Closed-loop review handoff with a context dossier, canonical Markdown report, and concise relay prompts. |
| [`prepare-adversarial-review-light`](skills/prepare-adversarial-review-light/SKILL.md) | Lightweight closed-loop handoff with concise prompts and a canonical Markdown review report. |
| [`session-companion`](skills/session-companion/SKILL.md) | Read-only live coach for a separate Claude Code or OMP session: reconstructs the other conversation, orients you on each refresh, and helps you understand, challenge, and steer it without ever writing to the other session. |
| [`solidify`](skills/solidify/SKILL.md) | Evidence-led challenge of an articulated request, goal brief, plan, or design that resolves material tradeoffs and makes its goal and normative constraints decision-ready. |
| [`teach-me`](skills/teach-me/SKILL.md) | Evidence-grounded teaching that builds a deep, plain-language mental model, explains each claim's implications, and commits to judgments with honest caveats. |

## Install

Install a skill from the published GitHub repo:

```bash
npx skills@latest add fishstoryyy/agent-tools --skill adversarial-review
npx skills@latest add fishstoryyy/agent-tools --skill budget-grill-me
npx skills@latest add fishstoryyy/agent-tools --skill build-context-to-do-something
npx skills@latest add fishstoryyy/agent-tools --skill context-handoff
npx skills@latest add fishstoryyy/agent-tools --skill create-session-handoff
npx skills@latest add fishstoryyy/agent-tools --skill explain-like-rookie
# Deprecated — superseded by session-companion
npx skills@latest add fishstoryyy/agent-tools --skill grill-me-companion
npx skills@latest add fishstoryyy/agent-tools --skill grill-me-full
npx skills@latest add fishstoryyy/agent-tools --skill grill-the-goal
# Intent and acceptance-contract grilling (at most ten questions)
npx skills@latest add fishstoryyy/agent-tools --skill grill-me-light
npx skills@latest add fishstoryyy/agent-tools --skill grill-me-ten
npx skills@latest add fishstoryyy/agent-tools --skill mastermind
npx skills@latest add fishstoryyy/agent-tools --skill orca-two-agent-loop
npx skills@latest add fishstoryyy/agent-tools --skill prepare-adversarial-review
npx skills@latest add fishstoryyy/agent-tools --skill prepare-adversarial-review-light
npx skills@latest add fishstoryyy/agent-tools --skill session-companion
npx skills@latest add fishstoryyy/agent-tools --skill solidify
npx skills@latest add fishstoryyy/agent-tools --skill teach-me
```

To list available skills before installing:

```bash
npx skills@latest add fishstoryyy/agent-tools -l
```

Local CLI discovery can be tested with:

```bash
npx skills@latest add . -l
```

Published discovery and installation were verified on August 11, 2026 (12 skills, including `budget-grill-me` and `session-companion`). Re-verify them after each release.

### Local Development

To use this checkout as the live source for both Codex and Claude Code:

```bash
npm run link:skills
```

This safely backs up existing installations, links every repo skill into `~/.agents/skills` for Codex and `~/.claude/skills` for Claude Code, and detaches these development links from the global Skills CLI update lock. Dedicated entries with the same name under `~/.codex/skills` are reported but left untouched because their provenance is unknown. Edits under `skills/` then become available without reinstalling. Re-run the command after adding or removing a skill.

Check the links without changing anything:

```bash
npm run check:skill-links
```

Test the linking workflow in isolated temporary home directories:

```bash
npm run test:skill-links
```

## Validate

Run:

```bash
npm run validate:skills
```

This checks that every skill folder under `skills/` has a valid `SKILL.md`,
required frontmatter, matching folder/name values, aligned Claude Code and Codex
invocation policies, and valid resource folders.

## Release Checklist

See [`docs/release-checklist.md`](docs/release-checklist.md).

## Publishing

See [`docs/publish-to-github.md`](docs/publish-to-github.md) for the GitHub publish and install-verification flow.

## License

MIT. See [`LICENSE`](LICENSE).
