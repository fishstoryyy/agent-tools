# Skills

Each folder in this directory is an installable agent skill.

Skill folders must:

- Use lowercase hyphen-case names.
- Contain a `SKILL.md` file.
- Set `name` in frontmatter to the folder name.
- Include a clear `description` that explains what the skill does and when to use it.
- Keep core instructions in `SKILL.md` and move large optional context into `references/`.

Run `npm run validate:skills` from the repo root before publishing changes.
