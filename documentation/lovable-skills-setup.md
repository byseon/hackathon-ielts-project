# Lovable skills — import and smoke test

After pushing `skills/` to GitHub, complete these steps in [lovable.dev](https://lovable.dev).

## Import skills from GitHub

**Settings → Skills → Add → Import from GitHub**

Import each skill subdirectory (replace branch if not `main`):

| Skill | GitHub URL |
|-------|------------|
| responsive-layout | `https://github.com/byseon/hackathon-ielts-project/tree/main/skills/responsive-layout` |
| accessibility-speaklab | `https://github.com/byseon/hackathon-ielts-project/tree/main/skills/accessibility-speaklab` |
| i18n-foundation | `https://github.com/byseon/hackathon-ielts-project/tree/main/skills/i18n-foundation` |

For each imported skill:

1. Confirm **Automatic use** is enabled (default).
2. Open skill preview and verify bundled files appear (`breakpoints.md`, `checklist.md`, `strings-conventions.md`).

### Re-sync after edits

GitHub import does not auto-update. After changing skills in the repo:

1. Push to `main`
2. **Settings → Skills** → open skill → re-import from GitHub, or Download old → Upload ZIP from local `skills/` folder

Alternative: **Add → Upload ZIP** — zip each `skills/<name>/` folder locally.

---

## Paste Knowledge

Copy snippets from [lovable-knowledge.md](lovable-knowledge.md) into:

- Workspace Knowledge (workspace settings)
- Project Knowledge (SpeakLab project settings)

---

## Smoke test checklist

Run these in Lovable chat after import. Explicit slash commands verify skills load before relying on auto-match.

### Test 1 — Launch page hero (responsive + i18n)

```
/responsive-layout /i18n-foundation Implement the launch page hero section per documentation/launch-page.md. Use i18n keys under landing.hero.*. Verify layout at 375px, 768px, and 1280px.
```

**Pass if:**

- [ ] Hero stacks on mobile; no horizontal scroll at 375px
- [ ] Copy uses `t()` keys, not hardcoded strings in JSX
- [ ] Primary CTA meets touch target size

### Test 2 — home_day1 (responsive + i18n)

```
/responsive-layout /i18n-foundation Build home_day1 from documentation/day-1-screens.md with TodayFocusCard and bottom nav. Namespace keys under home.day1.*
```

**Pass if:**

- [ ] TodayFocusCard full width on mobile
- [ ] Primary CTA visible without excessive scroll
- [ ] Nav labels from i18n common.nav.*

### Test 3 — practice timer a11y

```
/accessibility-speaklab Review practice_part2_speak timer, progress bar, and recording indicator. Fix any checklist failures.
```

**Pass if:**

- [ ] Agent returns pass/fail checklist table
- [ ] Progress bar has aria-valuenow/min/max
- [ ] Recording state has text label
- [ ] aria-live announcements documented or implemented

### Test 4 — Auto-match (no slash)

```
Add the social proof strip to the landing page following the spec in documentation/launch-page.md.
```

**Pass if:**

- [ ] responsive-layout and/or i18n-foundation skill tags appear in chat (hover skill tag to confirm)
- [ ] Or output reflects mobile-first layout and i18n keys without explicit slash

### Test 5 — Built-in accessibility (optional)

```
/accessibility Run a full accessibility pass on the landing page.
```

Use alongside `accessibility-speaklab` for SpeakLab-specific timer/video rules.

---

## Cursor parity

The same skills are copied to `.cursor/skills/` in this repo. Cursor loads them when descriptions match; invoke by name in chat when needed.

Source of truth remains `skills/` at repo root — re-copy to `.cursor/skills/` after skill edits:

```bash
cd hackathon-ielts-project
rm -rf .cursor/skills
cp -R skills .cursor/skills
```
