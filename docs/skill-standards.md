# Skill Standards

Skills in this repo should follow the Agent Skills folder model:

- A skill is a folder.
- The folder contains a required `SKILL.md`.
- `SKILL.md` contains YAML frontmatter with `name` and `description`.
- The `name` must match the folder name.
- Every skill declares the same invocation policy for Claude Code and Codex:
  - Manual-only skills set `disable-model-invocation: true` in `SKILL.md` and
    `policy.allow_implicit_invocation: false` in `agents/openai.yaml`.
  - Implicitly invocable skills omit `disable-model-invocation` and set
    `policy.allow_implicit_invocation: true`.
- Every skill includes provider metadata in `agents/openai.yaml`.
- Optional resource folders are `scripts/`, `references/`, and `assets/`.

## Authoring Guidelines

- Put clear scope and trigger conditions in the `description`; skill pickers use it to help users choose the right skill.
- Keep `SKILL.md` focused on the core workflow.
- Use progressive disclosure: move long reference material into `references/` and tell agents when to read it.
- Add scripts only when deterministic reuse is valuable.
- Avoid extra documentation files inside individual skill folders unless they directly support the skill.

## Invocation Compatibility

- In Claude Code, invoke a skill with `/skill-name`.
- In Codex, mention a skill with `$skill-name` or choose it from `/skills`.
- OpenCode can discover these skills from `.agents/skills`, but may ignore
  provider-specific invocation metadata. A manual-only skill can therefore
  auto-invoke in OpenCode; do not rely on that metadata as an OpenCode safety
  boundary.

## Validation

Run:

```bash
npm run validate:skills
```

The local validator intentionally has no package dependencies so it can run in CI without setup beyond Node.js.
