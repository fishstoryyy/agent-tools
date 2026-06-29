# Agent Tools

[![Validate](https://github.com/fishstoryyy/agent-tools/actions/workflows/validate.yml/badge.svg)](https://github.com/fishstoryyy/agent-tools/actions/workflows/validate.yml)

Personal open-source toolkit for agent skills and other agentic tools.

This repo starts with `grill-me-light`, a bounded planning and alignment skill that helps an agent stress-test a plan without turning the conversation into an endless interview.

## Repository Layout

```text
agent-tools/
  skills/
    grill-me-light/
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

## Install

Install `grill-me-light` from the published GitHub repo:

```bash
npx skills@latest add fishstoryyy/agent-tools --skill grill-me-light
```

To list available skills before installing:

```bash
npx skills@latest add fishstoryyy/agent-tools -l
```

Local CLI discovery can be tested with:

```bash
npx skills@latest add . -l
```

Published discovery and installation were verified on June 29, 2026. Re-verify them after each release.

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
