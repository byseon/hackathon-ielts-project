# SpeakLab accessibility checklist

Use for mock exam, practice, home, and marketing pages.

## Structure

- [ ] Single `<h1>` per route
- [ ] Heading levels do not skip (h1 → h2 → h3)
- [ ] `<main>` wraps primary content
- [ ] `<nav>` has accessible name (`aria-label="Main"` or visible text)

## Keyboard and focus

- [ ] All buttons, links, inputs reachable via Tab
- [ ] Focus indicator visible on all interactive elements
- [ ] No keyboard trap except intentional modals (with Escape to close)
- [ ] Modal/dialog: focus trapped inside; returns to trigger on close
- [ ] Skip link to main content on marketing page (optional but recommended)

## Forms and inputs

- [ ] Every input has associated label
- [ ] Error messages linked with `aria-describedby`
- [ ] Required fields marked (`required` or `aria-required`)

## Visual and motion

- [ ] Text contrast meets WCAG AA
- [ ] State not conveyed by color alone (recording, timer urgency, success/error)
- [ ] `prefers-reduced-motion` respected for animations

## Timers (practice screens)

- [ ] Countdown visible as text (not progress bar alone)
- [ ] `aria-live` announcements at phase changes
- [ ] Progress bar has `aria-valuenow` / min / max / label
- [ ] Auto-advance announces next phase to screen readers

## Video and media

- [ ] Recording state has text label
- [ ] Video region has descriptive accessible name
- [ ] Controls (if any) keyboard operable

## Cue cards

- [ ] Cue text readable by screen readers when expanded
- [ ] Collapse/expand control has `aria-expanded`
- [ ] Part 3 listen phase: question not shown visually during listen (per spec) — ensure screen reader timing matches UX intent

## CTAs

- [ ] Primary CTA descriptive (not "Click here")
- [ ] Touch targets ≥ 44×44px on mobile
- [ ] Loading/disabled buttons use `aria-busy` / `aria-disabled` appropriately

## Marketing page

- [ ] FAQ accordion: `aria-expanded` on triggers
- [ ] Decorative hero imagery marked `alt=""` or described if meaningful

## Manual checks (flag as "manual")

- [ ] Screen reader walkthrough of full mock flow
- [ ] Zoom to 200% — layout usable, no horizontal scroll on primary content
- [ ] Voice control / switch access (if targeting WCAG AAA goals)
