# Agent Tools

[![Validate](https://github.com/fishstoryyy/agent-tools/actions/workflows/validate.yml/badge.svg)](https://github.com/fishstoryyy/agent-tools/actions/workflows/validate.yml)

Personal open-source toolkit for agent skills and other agentic tools.

## Repository Layout

```text
agent-tools/
  skills/
    grill-me-light/
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
| [`grill-me-light`](skills/grill-me-light/SKILL.md) | Bounded plan grilling with a five-question default cap, recommendations, alignment brief, and handoff support. |
| [`prepare-adversarial-review`](skills/prepare-adversarial-review/SKILL.md) | Closed-loop review handoff with a context dossier, canonical Markdown report, and concise relay prompts. |
| [`prepare-adversarial-review-light`](skills/prepare-adversarial-review-light/SKILL.md) | Lightweight context handoff and launch prompt for independent adversarial review or third-line audit. |

## Install

Install a skill from the published GitHub repo:

```bash
npx skills@latest add fishstoryyy/agent-tools --skill grill-me-light
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

Published discovery and installation were verified on June 30, 2026. Re-verify them after each release.

## Validate

Run:

```bash
npm run validate:skills
```

This checks that every skill folder under `skills/` has a valid `SKILL.md`, required frontmatter, matching folder/name values, and valid optional resource folders.

## Release Checklist

See [`docs/release-checklist.md`](docs/release-checklist.md).

## Publishing

See [`docs/publish-to-github.md`](docs/publish-to-github.md) for the GitHub publish and install-verification flow.

## License

MIT. See [`LICENSE`](LICENSE).
