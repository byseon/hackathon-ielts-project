---
name: responsive-layout
description: Use when creating or editing pages, layouts, navigation, or marketing sections. Use when the user mentions mobile, tablet, desktop, breakpoints, or responsive behavior. Not for copy-only or backend changes.
---

# Responsive layout

## Workflow

1. Identify the screen or section (check `documentation/day-1-screens.md` or `documentation/launch-page.md` for screen IDs).
2. Implement mobile layout first (375px), then add `sm:` / `md:` / `lg:` enhancements.
3. Verify at **375px**, **768px**, and **1280px** before marking complete.
4. Report any horizontal scroll or clipped CTAs as blockers.

## Rules

- Single column on mobile; side-by-side only from `md:` or `lg:` when content allows
- Primary CTAs: full-width on mobile (`w-full sm:w-auto`) or sticky bottom bar for practice flows
- Content wells: `mx-auto max-w-4xl px-4` (marketing) or `max-w-lg` (focused practice screens)
- Use `min-h-dvh` for full-viewport shells, not `min-h-screen` alone
- Fluid spacing: `gap-4 sm:gap-6`, `py-8 sm:py-12`
- Images/video: `aspect-video w-full max-h-[50dvh] object-cover` in conversation layouts
- Bottom nav (`AppShell`): safe-area padding `pb-[env(safe-area-inset-bottom)]`

## SpeakLab patterns

| Pattern | Mobile | Tablet+ |
|---------|--------|---------|
| Launch hero | Stacked headline → subhead → CTA → visual | Visual beside copy at `lg:` |
| Social proof strip | Wrap badges, centered | Single row |
| `ConversationShell` prep | Cue card full width, video below or compact top | Video + cue side-by-side at `lg:` only |
| `ConversationShell` speak | Video dominant full width; cue collapsed/accordion | Cue in sidebar at `md:` |
| Home `TodayFocusCard` | Full-width hero card, CTA below | Same; optional wider max-width |

For per-screen layout notes, see [breakpoints.md](breakpoints.md).

## Avoid

- Fixed widths like `w-[400px]` on containers
- Horizontal scroll caused by padding + `100vw`
- Hiding primary CTAs below the fold on 375px without sticky fallback
- Side-by-side video + cue card below `md:` breakpoint

## Output format

When reviewing or building, list:
- Viewports checked (375 / 768 / 1280)
- Layout decisions per breakpoint
- Any remaining risks
