# SpeakLab — Lovable project (live)

Created via Lovable MCP on 2026-06-27.

| Field | Value |
|-------|-------|
| **Project ID** | `0310155f-b8b5-4b53-8493-1f3f9e04411b` |
| **Display name** | Speak Lab AI |
| **Workspace** | Anna's Lovable (`amO74AohwnlH6IC4lMsE`) |
| **Editor** | https://lovable.dev/projects/0310155f-b8b5-4b53-8493-1f3f9e04411b |
| **Preview** | https://id-preview--0310155f-b8b5-4b53-8493-1f3f9e04411b.lovable.app |
| **Database** | Lovable Cloud (Supabase) — enabled |
| **Latest commit** | `445bc28df283cfc4229eef46c6bc1d89d10eb6f4` |

## Built by Lovable

- Marketing landing page at `/`
- Email/password auth: `/signup`, `/login`
- Protected routes: `/home`, `/onboarding`, `/mock`, `/practice`, `/progress`, `/session/preview`
- `profiles` table with RLS + auto-create on signup
- Day 1 home with TodayFocusCard and mock criteria data
- Teal-on-stone design system

## Your next steps

1. **Disable email confirmation** (for hackathon testing): Lovable → Cloud → Authentication
2. **Connect GitHub**: see [GITHUB_SETUP.md](./GITHUB_SETUP.md) — org admin installs app; you create `byseon/hackathon-ielts-project-new`
3. **Copy docs**: after GitHub sync, push `documentation/`, `skills/`, and `AGENTS.md` to `main` on the new repo
4. **Tavus**: next `send_message` — wire AI video examiner + Edge Function for `TAVUS_API_KEY`

## Test flow

1. Open preview URL → **Take your free mock**
2. Sign up → onboarding → mock placeholder
3. Log in → `/home` shows Day 1 plan
