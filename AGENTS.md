# Repository Agent Instructions

## Protect the Working Tree

- Run `git status --short --untracked-files=all` before making changes and again before handing off.
- Preserve unrelated staged and unstaged work. Do not stage, unstage, commit, or otherwise alter it unless the user explicitly asks.
- Keep generated installation artifacts out of this repository. Skill propagation must not create a project-local `.agents/` tree or `skills-lock.json`.

## Required Workflow for Skill Changes

Whenever a task changes any file under `skills/<skill-name>/`, propagate that exact skill to the user's local agent installations before considering the task complete.

1. Identify every changed skill by folder name.
2. Validate the repository skills:

   ```bash
   npm run validate:skills
   ```

3. From the repository root, install each changed skill globally and non-interactively with explicit scope and targets:

   ```bash
   npx skills@latest add . \
     --skill <skill-name> \
     --global \
     --agent universal \
     --agent codex \
     --agent opencode \
     --agent claude-code \
     --yes
   ```

   Run the command separately for each changed skill. Never use `--all`, omit `--skill`, or omit `--global`.

4. Verify the installed content against the source. At minimum, compare the complete skill directories:

   ```bash
   diff -qr "skills/<skill-name>" "$HOME/.agents/skills/<skill-name>"
   diff -qr "skills/<skill-name>" "$HOME/.claude/skills/<skill-name>"
   ```

   The Skills CLI currently uses `~/.agents/skills/<skill-name>` as the universal installation for Agents, Codex, and OpenCode, and links Claude Code to the same canonical copy. Treat the CLI's installation summary as authoritative: if it reports different paths, verify those paths instead. Confirm symlink targets with `readlink` or `realpath` where applicable.

5. Confirm that propagation did not modify the repository:

   ```bash
   git status --short --untracked-files=all
   ```

   If the propagation command created project-local `.agents/` or `skills-lock.json`, stop. Remove only the artifacts created by the current command, verify the working tree again, and do not stage them.

6. In the handoff, report the changed skill, validation result, installed paths, and content-comparison result. Distinguish file installation from runtime verification; do not claim that an agent successfully discovered or invoked the skill unless that was tested in a fresh agent session.

## Skills CLI Safety

- Do not run `npx skills@latest add . --help`; the CLI can interpret it as an installation. Use `npx skills@latest --help` for help.
- Never run a project-scoped install when the intent is to update the user's local agents.
- Always scope propagation to the exact skill changed. Do not reinstall unrelated skills.
