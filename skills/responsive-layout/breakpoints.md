# SpeakLab responsive breakpoints reference

Tailwind defaults: `sm` 640px, `md` 768px, `lg` 1024px, `xl` 1280px.

Test at **375px** (iPhone SE), **768px** (tablet), **1280px** (desktop).

## Marketing launch page (`/`)

From `documentation/launch-page.md`:

| Section | 375px | 768px+ | 1280px+ |
|---------|-------|--------|---------|
| Header | Logo + compact CTA; no hamburger unless nav grows | Same | Optional wider nav links |
| Hero | Single column; CTA full width; visual below copy | Increased type scale | Two-column at `lg:` (copy left, mock frame right) |
| Social proof | Wrapped badge pills, centered | Single row or 2-row grid | Single row |
| How it works | Stacked steps (1→2→3) | 3-column grid at `md:` | Same |
| FAQ | Accordion full width | `max-w-2xl` centered | Same |
| Footer CTA | Sticky optional; full-width button | Centered button | Same |

Primary CTA **Take your free mock** must remain tappable without zoom (min 44×44px touch target).

## App shell (authenticated)

- Bottom tab nav: Home, Practice, Mock, Progress — fixed bottom, `md:` can move to side nav if added later
- `max-w-lg mx-auto` for focused practice content on large screens (readable line length)

## Day 1 screens

From `documentation/day-1-screens.md`:

### `home_day1`

- Greeting + plan day label: top stack
- `TodayFocusCard`: full width, primary CTA inside card or directly below
- 4-criteria mini-bars: 2×2 grid on mobile, 4-column at `sm:`

### `session_preview`

- Activity list: vertical stack with icons left, text right
- Meta line (12 min · 2 activities): wraps on narrow screens

### `practice_part2_cue` (ConversationShell — prep)

- Cue card: full width, readable font (`text-base sm:text-lg`)
- Prep timer: prominent, centered or top-right; must not overlap cue text
- Notes area: full width textarea
- Examiner video: below cue on mobile; max height ~30dvh so timer + notes stay visible

### `practice_part2_speak` (ConversationShell — speak)

- Video: dominant, min 40dvh on mobile
- Cue: collapsible `<details>` or icon toggle — not permanent sidebar on mobile
- Progress bar + recording indicator: fixed above bottom CTA bar
- Primary **End turn**: sticky bottom full width

### `practice_part3_discussion`

- Video full width; question text appears after listen phase (not during)
- **Answer** button: sticky bottom on mobile

### Feedback screens

- Transcript highlights: scrollable `max-h-60` region
- **Next activity** / **Finish session**: sticky bottom on mobile

### `session_complete` / `home_day1_updated`

- Celebration content centered; single primary CTA
