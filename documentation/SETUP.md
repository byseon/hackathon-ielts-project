# SpeakLab — Lovable setup checklist

## Live Lovable project

SpeakLab was created via Lovable MCP. See **[LOVABLE_PROJECT.md](./LOVABLE_PROJECT.md)** for links.

- **Editor:** https://lovable.dev/projects/0310155f-b8b5-4b53-8493-1f3f9e04411b
- **Preview:** https://id-preview--0310155f-b8b5-4b53-8493-1f3f9e04411b.lovable.app

## Step 1: Lovable MCP (done)

Lovable MCP is connected as `user-lovable` in Cursor (OAuth complete).

## Step 2: Connect GitHub (manual)

Lovable creates a **new** repo — the existing `byseon/hackathon-ielts-project` stays untouched.

1. **Org admin** installs [Lovable GitHub App](https://github.com/apps/lovable-dev) on `byseon` — see [GITHUB_SETUP.md](./GITHUB_SETUP.md)
2. Lovable → **Settings** → **Git** → **GitHub** → Connect `byseon`
3. SpeakLab project → **Project settings** → **Git** → **GitHub** → create **`hackathon-ielts-project-new`** on `main`

## Step 3: After GitHub is connected

Copy docs and skills into the new repo (full commands in [GITHUB_SETUP.md](./GITHUB_SETUP.md)):

```bash
git clone git@github.com:byseon/hackathon-ielts-project-new.git
cd hackathon-ielts-project-new
# copy documentation/, skills/, AGENTS.md from local scaffold → commit → push main
```

## Step 4: Cloud auth (optional for testing)

In Lovable **Cloud** → **Authentication**: disable **Confirm email** for faster hackathon testing.

## Step 5: RAI guardrails (responsive, accessibility, i18n)

1. Paste Knowledge snippets from [documentation/lovable-knowledge.md](documentation/lovable-knowledge.md) into Lovable Workspace + Project Knowledge.
2. Import skills from GitHub per [documentation/lovable-skills-setup.md](documentation/lovable-skills-setup.md) (use `-new` repo URLs).
3. Run the smoke test prompts in that doc to verify skills load.

Repo files (copy into `-new` after connect):

- [AGENTS.md](AGENTS.md) — always-on rules (Lovable reads from GitHub sync)
- [skills/](skills/) — `responsive-layout`, `accessibility-speaklab`, `i18n-foundation`
- [.cursor/skills/](.cursor/skills/) — Cursor copy of the same skills
