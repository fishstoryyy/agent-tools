# Release Checklist

Use this checklist before publishing a new skill or repo release.

## Repository

- [ ] Authenticate GitHub CLI with `gh auth login -h github.com`.
- [ ] Confirm the repo is public.
- [ ] Confirm `README.md` explains the repo purpose and skill list.
- [ ] Confirm `LICENSE` is present.
- [ ] Confirm GitHub Actions validation passes.
- [ ] Confirm no private notes, local paths, or secrets are committed.

## Skill

- [ ] Confirm the skill folder is under `skills/<skill-name>/`.
- [ ] Confirm `SKILL.md` frontmatter has `name` and `description`.
- [ ] Confirm `name` matches the folder name.
- [ ] Confirm `description` clearly states when to use the skill.
- [ ] Confirm optional resource folders are only `scripts/`, `references/`, and `assets/`.
- [ ] Confirm `npm run validate:skills` passes.

## Install Verification

- [ ] Publish or push the repo to GitHub.
- [ ] List published skills with `npx skills@latest add fishstoryyy/agent-tools -l`.
- [ ] Test the install command with `npx skills@latest add fishstoryyy/agent-tools --skill grill-me-light`.
- [ ] Record the verified install command in `README.md`.
- [ ] Confirm the installed skill appears with the expected name and description.
- [ ] Run a small usage test for the installed skill.

## Release Notes

- [ ] Summarize what changed.
- [ ] Note the verified install command.
- [ ] Note any known limitations or follow-up work.
