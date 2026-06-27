# GitHub + Lovable sync (manual steps)

Lovable **cannot** link to an existing repo. It always **creates a new repo** when you connect.

## Repo strategy (recommended)

Keep both repos — no need to rename or delete the old one.

| Repo | Role |
|------|------|
| `byseon/hackathon-ielts-project` | Original scaffold + docs (archive / reference) |
| `byseon/hackathon-ielts-project-new` | **Lovable app** — two-way sync on `main` |

After Lovable connects, treat **`hackathon-ielts-project-new`** as the source of truth for the app. Copy or push `documentation/` and `skills/` into the new repo on `main`.

**Never** rename, move, or delete the Lovable-linked repo after setup.

---

## Roles

| Task | Who |
|------|-----|
| Install Lovable GitHub App on `byseon` | **Org admin** (byseon owner) |
| Connect `byseon` in Lovable workspace Git settings | **You** (workspace admin) — or admin if invited |
| Connect SpeakLab project → create `hackathon-ielts-project-new` | **You** (project admin) |
| Push docs / skills to `main` on the new repo | **You** (repo collaborator) |

If you are only an **outside collaborator** on the old repo and cannot see the `byseon` org in Lovable Git settings, ask the org admin to install the GitHub App. Optionally invite them to your Lovable workspace as admin to complete the project connect step.

---

## 1. Org admin — GitHub only (~5 min)

1. Install the [Lovable GitHub App](https://github.com/apps/lovable-dev) on the **`byseon`** org  
   - Grant **all repos** or at least `hackathon-ielts-project-new` once it exists  
2. **Do not** delete or rename `byseon/hackathon-ielts-project` — leave it as-is  
3. Add collaborators to the **new** repo after Lovable creates it (if needed)

### Paste-ready message for your admin

> We need Lovable two-way GitHub sync for SpeakLab under `byseon`.  
> **Lovable project:** https://lovable.dev/projects/0310155f-b8b5-4b53-8493-1f3f9e04411b  
> **New repo name (Lovable will create it):** `hackathon-ielts-project-new` on branch `main`  
> Please install https://github.com/apps/lovable-dev on the `byseon` org. No changes needed to the existing `hackathon-ielts-project` repo. Ping me when the app is installed.

---

## 2. Connect workspace to GitHub (you)

1. [lovable.dev](https://lovable.dev) → **Settings** → **Git** → **GitHub**
2. **Connect GitHub** → authorize OAuth (if not already)
3. Click **Connect** next to **`byseon`** (visible after the org admin installs the app)

---

## 3. Connect SpeakLab project

**Project:** [Speak Lab AI](https://lovable.dev/projects/0310155f-b8b5-4b53-8493-1f3f9e04411b)

1. Open the project → **Project settings** → **Git** → **GitHub**
2. Click **Connect** next to `byseon`
3. Name the new repo **`hackathon-ielts-project-new`**
4. Confirm sync on branch **`main`**

Lovable pushes the full app as the initial commit. Sync is bidirectional from that point.

---

## 4. Copy docs and skills into the new repo

After Lovable creates `byseon/hackathon-ielts-project-new`:

```bash
git clone git@github.com:byseon/hackathon-ielts-project-new.git
cd hackathon-ielts-project-new

# Copy from your local scaffold (adjust path if needed)
cp -R ../hackathon-ielts-project/documentation .
cp -R ../hackathon-ielts-project/skills .
cp ../hackathon-ielts-project/AGENTS.md .

git add documentation skills AGENTS.md
git commit -m "Add product docs and Lovable skills"
git push origin main
```

Lovable picks up pushes to the active branch (`main`) automatically.

### Import skills in Lovable UI

See [documentation/lovable-skills-setup.md](documentation/lovable-skills-setup.md) — use the `-new` repo URLs after the first push.

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `byseon` not listed in Lovable Git settings | Org admin must install the Lovable GitHub App; you may need org membership (not just repo collaborator) |
| Repo name already taken | Pick another name at connect time (e.g. `speaklab-app`); update this doc |
| Sync stopped | Repo was renamed/moved/deleted — restore original path or disconnect and reconnect (creates a **new** repo) |

## Reference

- [Lovable GitHub integration docs](https://docs.lovable.dev/integrations/github)
- Cannot import an existing GitHub repo into Lovable — export/sync from Lovable only
