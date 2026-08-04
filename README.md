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
    build-context-to-do-something/
      SKILL.md
      agents/openai.yaml
    context-handoff/
      SKILL.md
      agents/openai.yaml
    create-session-handoff/
      SKILL.md
      agents/openai.yaml
    grill-me-companion/
      SKILL.md
      agents/openai.yaml
    grill-the-goal/
      SKILL.md
      agents/openai.yaml
    grill-me-light/
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
  tools/
  templates/
  docs/
  scripts/
```

## Skills

| Skill | Description |
| --- | --- |
| [`adversarial-review`](skills/adversarial-review/SKILL.md) | Inline, evidence-grounded stress testing for plans, designs, and implementations. |
| [`build-context-to-do-something`](skills/build-context-to-do-something/SKILL.md) | Minimum-sufficient context prompts for capable fresh agents performing user-specified tasks. |
| [`context-handoff`](skills/context-handoff/SKILL.md) | Tight, self-contained prompts for handing work to a fresh agent or session. |
| [`create-session-handoff`](skills/create-session-handoff/SKILL.md) | Durable workspace handoffs for continuing active work in a fresh session. |
| [`grill-me-companion`](skills/grill-me-companion/SKILL.md) | Read-only coaching for understanding and steering a separate Claude Code or OMP session. |
| [`grill-the-goal`](skills/grill-the-goal/SKILL.md) | Goal-focused interviewing that produces decision-ready briefs by clarifying relevant context, actors, sources, outcomes, success evidence, tradeoffs, constraints, and unknowns without entering implementation planning. |
| [`grill-me-light`](skills/grill-me-light/SKILL.md) | Bounded plan grilling with a six-question default cap, recommendations, alignment brief, and handoff support. |
| [`orca-two-agent-loop`](skills/orca-two-agent-loop/SKILL.md) | Orca-native manager-engineer workflow with adversarial plan and implementation review. |
| [`prepare-adversarial-review`](skills/prepare-adversarial-review/SKILL.md) | Closed-loop review handoff with a context dossier, canonical Markdown report, and concise relay prompts. |
| [`prepare-adversarial-review-light`](skills/prepare-adversarial-review-light/SKILL.md) | Lightweight closed-loop handoff with concise prompts and a canonical Markdown review report. |

## Install

Install a skill from the published GitHub repo:

```bash
npx skills@latest add fishstoryyy/agent-tools --skill adversarial-review
npx skills@latest add fishstoryyy/agent-tools --skill build-context-to-do-something
npx skills@latest add fishstoryyy/agent-tools --skill context-handoff
npx skills@latest add fishstoryyy/agent-tools --skill create-session-handoff
npx skills@latest add fishstoryyy/agent-tools --skill grill-me-companion
npx skills@latest add fishstoryyy/agent-tools --skill grill-the-goal
npx skills@latest add fishstoryyy/agent-tools --skill grill-me-light
npx skills@latest add fishstoryyy/agent-tools --skill orca-two-agent-loop
npx skills@latest add fishstoryyy/agent-tools --skill prepare-adversarial-review
npx skills@latest add fishstoryyy/agent-tools --skill prepare-adversarial-review-light
```

To list available skills before installing:

```bash
npx skills@latest add fishstoryyy/agent-tools -l
```

Local CLI discovery can be tested with:

```bash
npx skills@latest add . -l
```

Published discovery and installation were verified on July 3, 2026. Re-verify them after each release.

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
