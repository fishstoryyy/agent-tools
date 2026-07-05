# Skill Standards

Skills in this repo should follow the Agent Skills folder model:

- A skill is a folder.
- The folder contains a required `SKILL.md`.
- `SKILL.md` contains YAML frontmatter with `name` and `description`.
- The `name` must match the folder name.
- Every skill sets `disable-model-invocation: true` in `SKILL.md` for manual-only Claude Code invocation.
- Every skill sets `policy.allow_implicit_invocation: false` in `agents/openai.yaml` for manual-only Codex invocation.
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
- OpenCode can discover these skills from `.agents/skills`, but currently ignores the provider-specific manual-only metadata. The skills remain usable there, but the model may invoke them automatically.

## Validation

Run:

```bash
npm run validate:skills
```

The local validator intentionally has no package dependencies so it can run in CI without setup beyond Node.js.
