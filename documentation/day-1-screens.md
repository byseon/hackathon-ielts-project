# SpeakLab — Day 1 After First Mock (Screen List)

Working product name: **SpeakLab** (placeholder — swap when brand is chosen).

Concrete screen sequence for a student who completed **Mock #1** and is starting **Day 1** of their personalized plan.

---

## Context (example mock results)

| Metric | Value |
|--------|-------|
| Overall band | 5.5 |
| Weakest criterion | Lexical resource — 5.0 |
| Secondary focus | Fluency — 5.5 |
| Part weakness | Part 2 (runs short, loses coherence) |
| Mistake tags | Short Part 2, basic vocabulary, occasional long pauses |

Day 1 plan focus: **Lexical resource + Part 2 length** (Activity 1: Part 2 cue drill; Activity 2: Part 3 discussion linked to same topic).

---

## Screen sequence

| # | Screen ID | Purpose | Key UI elements | Primary CTA |
|---|-----------|---------|-----------------|-------------|
| 1 | `home_day1` | Orient + one clear action | Greeting, "Day 1 of your plan", TodayFocusCard, reason chip ("Weak vocabulary in Mock #1"), 4-criteria mini-bars, streak placeholder | **Start today's session** |
| 2 | `session_preview` | Set expectations | "12 min · 2 activities", focus badge (Lexical + Part 2), activity list with icons | **Begin** |
| 3 | `practice_part2_cue` | Activity 1 — Part 2 drill | Cue card (e.g. "Describe a place you like to visit"), 60s prep timer, notes area, examiner video (listening mode) | **Start speaking** (after prep) |
| 4 | `practice_part2_speak` | Activity 1 — speak turn | Cue card (collapsed/side), examiner video, 2-min progress bar (red → green), recording indicator | **End turn** (or auto at 2:00) |
| 5 | `feedback_part2` | Activity 1 feedback | Band estimate for turn, lexical highlights on transcript, 1–2 fixable items, "Improved version" snippet | **Next activity** |
| 6 | `practice_part3_discussion` | Activity 2 — Part 3 drill | Examiner asks 2 abstract follow-ups (linked to Part 2 topic), no text during listen, video dominant | **Answer** (turn-based) |
| 7 | `feedback_part3` | Activity 2 feedback | Fluency + lexical focus, linking-word suggestions, compare to Mock #1 weakness | **Finish session** |
| 8 | `session_complete` | Close the loop | "Day 1 complete", criteria touched today, tomorrow preview ("Part 1 rapid Q&A"), plan progress (1/5 sessions to next mock) | **Back to home** |
| 9 | `home_day1_updated` | Reinforce habit | Completed checkmark on today's card, "Tomorrow: Fluency · Part 1", optional "Explore practice" link, Progress tab hint | **See progress** (secondary) |

---

## Screen-by-screen detail

### 1. `home_day1`

**Header:** "Good morning, [Name]" / "Day 1 of your plan"

**TodayFocusCard (hero):**
- Title: "Build vocabulary for Part 2"
- Reason chip: `Because Mock #1: Lexical resource 5.0`
- Estimated time: ~12 min

**Secondary:** 4-criteria mini-bars (from Mock #1), muted until student opens Progress

**Nav:** Home (active), Practice, Mock, Progress

**Primary CTA:** Start today's session

---

### 2. `session_preview`

**Title:** Today's session

**Meta:** 12 min · 2 activities · Focus: Lexical resource + Part 2

**Activity list:**
1. Part 2 cue card — "Describe a place you like to visit" (~7 min)
2. Part 3 discussion — follow-ups on travel/places (~5 min)

**RecommendationReason:** "We picked these because your Part 2 answers were short and vocabulary was your lowest score in Mock #1."

**Primary CTA:** Begin

---

### 3. `practice_part2_cue`

**Layout:** ConversationShell — prep mode

**Cue card (full width):**
- Describe a place you like to visit
- You should say: where it is, how you know it, what you do there, and why you like it

**Prep timer:** 60 s countdown (prominent)

**Notes area:** Optional text field (mirrors real test paper)

**Examiner video:** Small, listening / neutral (not asking yet)

**Primary CTA:** Start speaking (enabled when prep ends or user skips remaining prep in practice mode)

---

### 4. `practice_part2_speak`

**Layout:** ConversationShell — speak mode

**Cue card:** Collapsed or sidebar (reference only)

**Examiner video:** Dominant; examiner nodding / listening

**2-min progress bar:** Red until ~1:30, green at 2:00 sweet spot

**Recording indicator:** Visible pulse / "Your turn"

**Primary CTA:** End turn (optional early exit); auto-advance at 2:00

---

### 5. `feedback_part2`

**Scores:** Turn-level estimate; highlight Lexical resource

**Transcript:** Full text with ums/pauses preserved; lexical issues highlighted (e.g. repeated "good", "nice", "thing")

**Fixable items (max 2):**
- "Try 'coastal town' instead of 'place by the sea'"
- "Use 'memorable' instead of 'good'"

**Improved version:** 2–3 sentence snippet + optional read-aloud

**Primary CTA:** Next activity

---

### 6. `practice_part3_discussion`

**Layout:** ConversationShell — interview mode

**Flow:** 2 questions, turn-based, linked to Part 2 topic (travel / places)

**Example questions (examiner audio only — no on-screen text during listen):**
1. "Why do you think some people prefer visiting new places rather than returning to familiar ones?"
2. "Do you think tourism has a positive or negative effect on local communities?"

**Primary CTA:** Answer (per turn; advances after student finishes)

---

### 7. `feedback_part3`

**Focus:** Fluency + lexical resource (linking words, topic vocabulary)

**Suggestions:**
- "Try opening with 'Well, I think…' or 'On the one hand…'"
- Highlight 1 fluency issue (e.g. long pause before "communities")

**Compare to Mock #1:** "Your vocabulary was stronger than in Mock #1 Part 3 — keep using topic-specific words."

**Primary CTA:** Finish session

---

### 8. `session_complete`

**Headline:** Day 1 complete

**Summary:**
- Worked on: Lexical resource, Part 2 length, Part 3 discussion
- Sessions until next mock: 1 / 5

**Tomorrow preview:** "Fluency · Part 1 rapid Q&A"

**Optional:** Share progress (future / parent email — not blocking)

**Primary CTA:** Back to home

---

### 9. `home_day1_updated`

**TodayFocusCard:** Completed checkmark; card collapsed or "Done for today"

**Tomorrow card (preview):** "Fluency · Part 1" — not yet tappable until next calendar day

**Secondary links:** Explore practice (self-directed by part/topic)

**Progress tab hint:** "See how today moved your scores" → Progress dashboard

**Primary CTA:** See progress (secondary; home is still default landing)

---

## Wireframe notes (all practice screens)

- **Mobile-first** — design for phone viewport first
- **Thumb-zone primary CTA** — fixed or sticky at bottom
- **Student copy** — plain English, L2-friendly (avoid idioms in UI chrome)
- **No shame framing** — "Your focus this week" not "You failed"
- **RecommendationReason** — visible on screens 1–2 (`Because Mock #1: vocabulary 5.0`)
- **Loading feedback** — transcript first, then scores, then deep suggestions

---

## Optional branches

### Skip / Explore (self-directed)

```
home_day1 → practice_by_part
```

- User chooses Part 1 / 2 / 3 or topic browse
- Not the default path; "Explore practice" link on screen 9
- Does not replace plan progress; optional extra practice

### Mid-session exit

```
Any practice screen → save progress → resume from session_preview
```

- Persist: activity index, partial transcript if mid-turn
- On return: "Continue where you left off" on `session_preview`

### Parent (Day 1)

- **No in-app parent screen** on Day 1
- Optional: email summary triggered after screen 8 (`session_complete`)
  - Includes: sessions completed, focus areas, time practiced
  - Read-only; student app unchanged

---

## Related docs

- [flows.md](./flows.md) — product loops and mock exam flow
- [launch-page.md](./launch-page.md) — marketing page and signup handoff
