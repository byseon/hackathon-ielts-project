# SpeakLab — Lovable setup checklist

## Step 1: Reload Cursor (required once)

Lovable MCP was added to `~/.cursor/mcp.json` and `.cursor/mcp.json`.

1. **Cmd+Shift+P** → **Reload Window**
2. On first Lovable MCP use, complete **OAuth** in the browser

## Step 2: Connect GitHub (you — manual)

Lovable cannot link an existing repo via API. Do this in [lovable.dev](https://lovable.dev):

1. Delete or rename empty `byseon/hackathon-ielts-project` on GitHub if it blocks creation
2. Lovable → **Settings** → **Git** → **GitHub** → Connect + install app on `byseon`
3. Open SpeakLab project → **Project settings** → **Git** → **GitHub** → Connect → create `hackathon-ielts-project`
4. Confirm two-way sync on `main`

## Step 3: After GitHub is connected

```bash
git clone git@github.com:byseon/hackathon-ielts-project.git
cd hackathon-ielts-project
# documentation/ is already in this repo — push if needed
git push origin main
```

## Step 4: Cloud auth (optional for testing)

In Lovable **Cloud** → **Authentication**: disable **Confirm email** for faster hackathon testing.

## Step 5: RAI guardrails (responsive, accessibility, i18n)

1. Paste Knowledge snippets from [documentation/lovable-knowledge.md](documentation/lovable-knowledge.md) into Lovable Workspace + Project Knowledge.
2. Import skills from GitHub per [documentation/lovable-skills-setup.md](documentation/lovable-skills-setup.md).
3. Run the smoke test prompts in that doc to verify skills load.

Repo files:

- [AGENTS.md](AGENTS.md) — always-on rules (Lovable reads from GitHub sync)
- [skills/](skills/) — `responsive-layout`, `accessibility-speaklab`, `i18n-foundation`
- [.cursor/skills/](.cursor/skills/) — Cursor copy of the same skills
