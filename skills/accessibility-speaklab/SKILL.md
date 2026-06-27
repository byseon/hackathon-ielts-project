---
name: accessibility-speaklab
description: Use when building or reviewing UI for keyboard access, screen readers, focus management, color contrast, or timed interactions. Use for mock exam, practice, and video-heavy screens. Complements generic accessibility audits; not for SEO or copy tone.
---

# Accessibility — SpeakLab

## Workflow

1. Identify route/screen ID from `documentation/day-1-screens.md` or current file.
2. Walk the checklist in [checklist.md](checklist.md); mark pass / fail / needs manual check.
3. Fix failures in code before marking the task complete.
4. For full-page audits, recommend also running Lovable built-in `/accessibility`.

## Universal rules

- One `<h1>` per route; headings descend in order (no skipped levels)
- Landmarks: `<header>`, `<main>`, `<nav>` with `aria-label` when multiple nav regions exist
- Focus: visible ring on all interactive elements; logical tab order matches visual order
- Icon-only controls: `aria-label` describing action (e.g. "End speaking turn")
- Forms: `<label htmlFor>` or `aria-labelledby`; errors via `aria-describedby` + `role="alert"` on error text
- Color contrast: WCAG AA minimum (4.5:1 body text, 3:1 large text/UI components)
- Do not convey state by color alone

## SpeakLab-specific

### Timers and progress

- Prep timer (60s) and speak progress (2 min): visible numeric countdown, not bar alone
- Container: `role="timer"` or `aria-live="polite"` region announcing:
  - Prep started
  - 30 seconds remaining (prep)
  - Prep complete — start speaking
  - 30 seconds remaining (speak)
  - Time complete
- Progress bar: `aria-valuenow`, `aria-valuemin`, `aria-valuemax`, `aria-label="Speaking time remaining"`

### Video and recording

- Recording indicator: text + icon ("Recording" / "Not recording"), not red dot alone
- Examiner video: `aria-label="AI examiner video"`; decorative if no controls
- If autoplay: respect muted policy; provide user-initiated start where required

### Cue cards

- Cue content in semantic region: `<section aria-labelledby="cue-heading">`
- Collapsed cue in speak mode: expand control with `aria-expanded`

### Practice navigation

- Turn-based **Answer** / **End turn**: focus moves to primary action when phase changes
- Session complete: focus first heading or primary CTA on route change

### Motion

- Wrap non-essential animations in `@media (prefers-reduced-motion: reduce)` or Tailwind `motion-reduce:` variants

## Output format

Return a checklist table:

| Check | Status | Notes |
|-------|--------|-------|
| ... | pass / fail / manual | ... |

List code changes made for any fail items.
