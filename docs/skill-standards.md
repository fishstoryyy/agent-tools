# Skill Standards

Skills in this repo should follow the Agent Skills folder model:

- A skill is a folder.
- The folder contains a required `SKILL.md`.
- `SKILL.md` contains YAML frontmatter with `name` and `description`.
- The `name` must match the folder name.
- Optional resource folders are `scripts/`, `references/`, and `assets/`.

## Authoring Guidelines

- Put trigger conditions in the `description`; it is the primary discovery signal.
- Keep `SKILL.md` focused on the core workflow.
- Use progressive disclosure: move long reference material into `references/` and tell agents when to read it.
- Add scripts only when deterministic reuse is valuable.
- Avoid extra documentation files inside individual skill folders unless they directly support the skill.

## Validation

Run:

```bash
npm run validate:skills
```

The local validator intentionally has no package dependencies so it can run in CI without setup beyond Node.js.
