# GitHub + Lovable sync (manual steps)

Lovable **cannot** link to an existing repo via API. Complete these steps in the browser.

## 1. Prepare GitHub

If `byseon/hackathon-ielts-project` already exists with unrelated history:

- **Option A:** Delete the empty/old repo on GitHub (Settings → Delete)
- **Option B:** Rename it to `hackathon-ielts-project-old`

This repo now contains the SpeakLab app scaffold. After Lovable connects, you can merge or replace as needed.

## 2. Connect workspace to GitHub

1. [lovable.dev](https://lovable.dev) → **Settings** → **Git** → **GitHub**
2. **Connect GitHub** → authorize OAuth
3. **Add organizations** → install **Lovable GitHub App** on `byseon`

## 3. Connect SpeakLab project

1. Open your Lovable project → **Project settings** → **Git** → **GitHub**
2. Click **Connect** next to `byseon`
3. Name the new repo `hackathon-ielts-project`
4. Confirm sync on branch `main`

## 4. Sync this codebase

After Lovable creates the repo:

```bash
git remote add lovable git@github.com:byseon/hackathon-ielts-project.git  # if needed
git checkout main || git checkout -b main
git pull lovable main --allow-unrelated-histories  # if Lovable pushed first
git push origin main
```

**Never** rename, move, or delete the Lovable-linked repo after setup.

## 5. Import existing repo into Lovable instead

If you prefer to keep this repo as source of truth:

1. Push this code to `byseon/hackathon-ielts-project` (already done or in progress)
2. In Lovable, create project and connect GitHub — Lovable will overwrite with its generated code OR you sync via push to `main`
3. Lovable picks up pushes to the active branch automatically
