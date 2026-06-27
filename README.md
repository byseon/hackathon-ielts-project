# SpeakLab (hackathon-ielts-project)

IELTS Speaking prep for English learners — AI video practice, personalized plans from mock exams.

## Stack

- React 19 + Vite + TypeScript + Tailwind CSS 4
- Supabase auth (Lovable Cloud compatible)
- Tavus CVI (planned)

## Quick start

```bash
cp .env.example .env
# Add Lovable Cloud / Supabase URL and publishable key from Cloud tab
npm install
npm run dev
```

Run [`supabase/migrations/001_profiles.sql`](supabase/migrations/001_profiles.sql) in Lovable Cloud SQL editor.

## Documentation

- [`documentation/flows.md`](documentation/flows.md) — product flows
- [`documentation/day-1-screens.md`](documentation/day-1-screens.md) — Day 1 UX
- [`documentation/launch-page.md`](documentation/launch-page.md) — marketing copy
- [`SETUP.md`](SETUP.md) — Lovable MCP + Cloud setup
- [`GITHUB_SETUP.md`](GITHUB_SETUP.md) — GitHub two-way sync (manual)

## Lovable MCP

Configured in `.cursor/mcp.json`. Reload Cursor and complete OAuth, then see [`lovable-mcp-prompts.md`](lovable-mcp-prompts.md).
