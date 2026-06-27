# Lovable Knowledge snippets

Copy each block into Lovable **Settings → Knowledge**. Keep under 10,000 characters each.

Repo source of truth: [AGENTS.md](../AGENTS.md)

---

## Workspace Knowledge

Paste into **Settings → Knowledge** (workspace level). Applies to all projects in the workspace.

```text
Coding and UI standards
- Mobile-first: design for 375px first; scale with Tailwind sm/md/lg breakpoints.
- Use Tailwind CSS v4 for styling; prefer shadcn/ui for new components when available.
- No fixed pixel widths on main content containers; avoid horizontal scroll at 375px.
- Semantic HTML; every interactive control keyboard-reachable with visible focus ring.
- All user-facing strings go through i18n (t('key')); English copy in src/locales/en/*.json — no hardcoded JSX strings.
- Dates and times via Intl.DateTimeFormat, not manual string concatenation.
- Do not add console.log in production paths.
- TypeScript strict; prefer named exports.

Responsive
- min-h-dvh for full-height layouts; fluid spacing (p-4 sm:p-6); max-w-* content wells.
- Primary CTAs full-width on mobile or sticky bottom in practice flows.

Accessibility baseline
- One h1 per route; logical heading order.
- Icon-only buttons need aria-label.
- Timers/progress: visible text plus aria-live announcements at key thresholds.
- Respect prefers-reduced-motion.

Internationalization
- English-only UI for now; structure must be i18n-ready.
- Do not add non-English locales unless explicitly requested.
```

---

## Project Knowledge (SpeakLab)

Paste into **Project settings → Knowledge** for the SpeakLab project.

```text
Product
SpeakLab — IELTS Speaking prep with AI video examiner, mock exams, and personalized daily practice. Users: English learners 18–30.

Specs (in repo documentation/)
- flows.md — acquisition, onboarding, daily loop, periodic mocks
- launch-page.md — marketing / page copy and section order
- day-1-screens.md — screen IDs and UI after Mock #1 (home_day1, session_preview, practice_part2_cue, etc.)

Key flows
- Marketing launch page → signup → goal setup → first mock → personalized plan → daily practice loop
- ConversationShell: video examiner + cue card; stack vertically on mobile

Project-specific RAI
- ConversationShell must not break on short viewports (video + cue card stack below md).
- Prep timer (60s) and speak progress (2 min): visible countdown + screen reader updates.
- Recording state: text label, not color alone.
- Primary CTA: "Take your free mock". Secondary: "Get started".

Skills in repo (import from GitHub)
- skills/responsive-layout — layouts and breakpoints
- skills/accessibility-speaklab — timers, video, practice a11y
- skills/i18n-foundation — locale keys and English-only structure

Stack: React 19, Vite, Tailwind v4, React Router, Supabase auth.
```
