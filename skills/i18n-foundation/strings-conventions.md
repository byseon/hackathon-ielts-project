# String key conventions

English-only for now. Structure keys so future locales can drop in without renaming.

## File layout

```
src/locales/en/
├── common.json      # shared: nav, auth, errors, generic CTAs
├── landing.json     # marketing page (documentation/launch-page.md)
├── home.json        # home_day1, home_day1_updated
├── session.json     # session_preview, session_complete
├── practice.json    # practice_part2_cue, practice_part2_speak, practice_part3_discussion
└── feedback.json    # feedback_part2, feedback_part3
```

## Key naming

Pattern: `{screenId}.{element}` or `{domain}.{element}`

| Screen ID | Namespace prefix | Example keys |
|-----------|------------------|--------------|
| `home_day1` | `home.day1.*` | `home.day1.greeting`, `home.day1.startSession` |
| `session_preview` | `session.preview.*` | `session.preview.title`, `session.preview.begin` |
| `practice_part2_cue` | `practice.part2.cue.*` | `practice.part2.cue.startSpeaking` |
| `practice_part2_speak` | `practice.part2.speak.*` | `practice.part2.speak.endTurn`, `practice.part2.speak.recording` |
| Landing `/` | `landing.*` | `landing.hero.headline`, `landing.hero.cta` |

Use camelCase for key segments after namespace: `startSession`, not `start-session`.

## Common keys (`common.json`)

```json
{
  "nav": {
    "home": "Home",
    "practice": "Practice",
    "mock": "Mock",
    "progress": "Progress"
  },
  "cta": {
    "takeFreeMock": "Take your free mock",
    "getStarted": "Get started"
  },
  "errors": {
    "generic": "Something went wrong. Please try again.",
    "network": "Check your connection and try again."
  }
}
```

## Interpolation examples

```json
{
  "home": {
    "day1": {
      "greeting": "Good morning, {{name}}",
      "planDay": "Day {{day}} of your plan",
      "reasonChip": "Because Mock #1: Lexical resource {{score}}"
    }
  },
  "session": {
    "preview": {
      "meta": "{{minutes}} min · {{count}} activities"
    }
  }
}
```

Component: `t('home.day1.greeting', { name })`

## Pluralization example

```json
{
  "session": {
    "preview": {
      "activityCount_one": "{{count}} activity",
      "activityCount_other": "{{count}} activities"
    }
  }
}
```

## Accessibility strings

Store `aria-label` copy in the same namespace with suffix `.ariaLabel`:

```json
{
  "practice": {
    "part2": {
      "speak": {
        "endTurn": "End turn",
        "endTurnAriaLabel": "End speaking turn and view feedback"
      }
    }
  }
}
```

## Screen copy sources

- Marketing: `documentation/launch-page.md` tables
- Day 1 flow: `documentation/day-1-screens.md` screen-by-screen detail
- Product CTAs: primary **Take your free mock**, secondary **Get started**

Do not invent placeholder lorem — use spec copy or realistic IELTS-adjacent copy.
