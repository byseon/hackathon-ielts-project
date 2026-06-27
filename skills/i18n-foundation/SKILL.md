---
name: i18n-foundation
description: Use when adding user-facing copy, labels, buttons, errors, or empty states. Use when setting up or extending localization structure. English-only content for now; do not add new languages unless explicitly requested.
---

# i18n foundation (English-only)

## Workflow

1. If i18n is not set up, scaffold per **First-time setup** below.
2. For new UI, add keys to locale JSON first, then reference via `t()` in components.
3. Match key conventions in [strings-conventions.md](strings-conventions.md).
4. Do not add non-English locale files unless the user explicitly requests translation.

## First-time setup

If the project has no i18n yet:

1. Add `i18next`, `react-i18next`, and `i18next-browser-languagedetector` (or use existing project pattern if already present).
2. Create `src/locales/en/common.json` and `src/locales/en/landing.json` (split by domain).
3. Initialize in `src/lib/i18n.ts` and wrap app in `I18nextProvider` / import in `main.tsx`.
4. Default language: `en` only; disable fallback to missing keys in dev (log warnings instead).

Prefer extending an existing i18n setup over introducing a second library.

## Rules

- **No hardcoded user-facing strings in JSX** — use `const { t } = useTranslation('namespace')` and `t('key')`
- English strings live only in `src/locales/en/*.json`
- Keys: stable, dot-separated, namespaced by screen ID from docs (`home_day1.greeting`, `practice_part2_cue.startSpeaking`)
- Interpolation: `t('session.meta', { minutes: 12, count: 2 })` — not template literals in JSX
- Pluralization: i18n plural keys (`key_one`, `key_other`) for counts
- Dates/times: `Intl.DateTimeFormat` or i18n date helpers — never `"Day " + n + " of your plan"` in components
- Attributes: `t('key')` for `aria-label`, `placeholder`, `title` where user-facing
- Marketing copy from `documentation/launch-page.md`: keys under `landing.*`
- Day 1 screens from `documentation/day-1-screens.md`: keys under screen ID namespace

## Adding copy for a screen

1. List all user-visible strings (headings, body, CTAs, chips, errors, empty states).
2. Add keys to appropriate JSON file.
3. Replace inline strings in component.
4. Verify no remaining hardcoded strings in that file (grep for quoted English in JSX).

## Avoid

- Splitting sentences across multiple keys in ways that break translation later
- Concatenating translated fragments in JSX
- Embedding HTML in JSON unless using `Trans` component with stable markup
- Creating `locales/es/` or other locales without explicit request

## Output format

When adding copy, report:
- Namespace/file updated
- New keys added (list)
- Components updated
