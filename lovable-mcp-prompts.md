# Lovable MCP prompts (run after Cursor reload + OAuth)

After reloading Cursor, ask the agent to run these via Lovable MCP, **or** paste equivalent prompts in Lovable chat.

## 1. Create project (if not using this repo import)

```
create_project(
  workspace_id: "<from list_workspaces>",
  description: "SpeakLab",
  initial_message: "Build SpeakLab — IELTS Speaking prep for English learners. Student-first, mobile-first. React + Vite + Tailwind + Lovable Cloud. Marketing landing at / with CTA Take your free mock."
)
```

## 2. Enable database

```
enable_database(project_id: "<project_id>")
```

## 3. Run profiles migration

```
query_database(project_id: "<project_id>", sql: "<contents of supabase/migrations/001_profiles.sql>")
```

## 4. Auth + pages (if starting fresh in Lovable)

```
send_message(project_id: "<project_id>", message: "Add email/password auth. Signup at /signup, login at /login. After signup go to /onboarding for target band and exam date, then /mock. Protect /home, /practice, /mock, /progress. Use profiles table with RLS.")
```

## 5. MVP from docs

```
send_message(project_id: "<project_id>", message: "Implement landing page per documentation/launch-page.md, Day 1 home per documentation/day-1-screens.md, flows per documentation/flows.md.")
```

This local repo already implements items 4–5 for import/sync via GitHub.
