# Publish to GitHub

Use this guide after reviewing the local scaffold.

## 1. Authenticate GitHub CLI

The local `gh` CLI must be authenticated before creating or pushing the repo.

```bash
gh auth login -h github.com
gh auth status
```

## 2. Create the Public Repo

From the repo root:

```bash
gh repo create fishstoryyy/agent-tools --public --source=. --remote=origin --push
```

If you want a different owner or repo name, replace `fishstoryyy/agent-tools`.

## 3. Verify GitHub Actions

After pushing, open the repository Actions tab and confirm the `Validate` workflow passes.

## 4. Verify Skills CLI Discovery

List available skills from the published repo:

```bash
npx skills@latest add fishstoryyy/agent-tools -l
```

Expected result: `grill-me-light` appears as an available skill.

## 5. Verify Skills CLI Install

Install only `grill-me-light`:

```bash
npx skills@latest add fishstoryyy/agent-tools --skill grill-me-light
```

Then confirm the installed skill appears in your target agent.

## 6. Update Docs if Needed

If the verified command differs from the expected command, update:

- `README.md`
- `docs/release-checklist.md`
