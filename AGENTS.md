# SpeakLab — Agent instructions

Always-on rules for Lovable, Cursor, and other Agent Skills tools working on this repo.

## Product context

SpeakLab is an IELTS Speaking prep app: AI video examiner, mock exams, personalized daily practice. Target users are English learners aged 18–30.

Primary specs live in `documentation/`:
- `flows.md` — product loops
- `launch-page.md` — marketing `/` page
- `day-1-screens.md` — post-mock Day 1 screen sequence

## Stack

- React 19 + TypeScript + Vite
- Tailwind CSS v4 (`@tailwindcss/vite`)
- React Router v7
- Supabase auth
- Prefer shadcn/ui when adding new UI primitives; match existing `@/components/*` patterns

## Non-negotiable baseline (every edit)

### Responsive layout

- Mobile-first: design for 375px width first, then scale up with `sm:` / `md:` / `lg:`
- Use fluid spacing (`p-4 sm:p-6`), `max-w-*` content wells, `min-h-dvh` for full-height layouts
- No fixed pixel widths on main content containers; avoid horizontal scroll at 375px
- `ConversationShell` screens (video + cue card): stack vertically on narrow viewports

### Accessibility

- Semantic HTML; one `<h1>` per route; logical heading order
- Every interactive control keyboard-reachable with visible focus ring
- Icon-only buttons need `aria-label`
- Timers and progress bars: visible text plus `aria-live="polite"` at key thresholds
- Video/recording state: text label, not color alone
- Respect `prefers-reduced-motion`

### Internationalization (English-only, i18n-ready)

- No hardcoded user-facing strings in JSX — use the project i18n hook (`t('key')`)
- English copy lives in `src/locales/en/*.json`
- Stable keys namespaced by screen ID (`home_day1`, `practice_part2_cue`, etc.)
- Dates/times via `Intl.DateTimeFormat`, not manual string concat
- Do not add non-English locales unless explicitly requested

## On-demand skills

Load these from `skills/` when the task matches (or invoke with `/skill-name` in Lovable):

| Skill | When |
|-------|------|
| `responsive-layout` | Pages, layouts, nav, marketing sections, breakpoints |
| `accessibility-speaklab` | Keyboard, screen readers, timers, video UI, mock/practice flows |
| `i18n-foundation` | User-facing copy, labels, errors, locale file structure |

For full-page accessibility audits, also use Lovable built-in `/accessibility`.

## Lovable setup

Paste snippets from `documentation/lovable-knowledge.md` into Workspace and Project Knowledge. Import skills per `documentation/lovable-skills-setup.md`.
