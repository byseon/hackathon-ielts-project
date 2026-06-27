---
name: ielts-examiner
description: IELTS Speaking domain knowledge for this project — the official 3-part test structure, the examiner PAL system-prompt template (drop into Tavus), and the band-score rubric encoded as a Tavus post-call action that turns the transcript + perception analysis into a 0–9 report (no external LLM). Use when writing the examiner persona or the scoring tool.
---

# IELTS Speaking — examiner script & scoring

Two jobs: (1) make the Tavus PAL behave like a real examiner, (2) turn the transcript into
an accurate band-score report. **Tavus does the scoring itself** via a *post-call action* —
no external LLM. This skill holds the domain knowledge for both.

## The test structure (≈11–14 min total)

**Part 1 — Introduction & interview (4–5 min).** Examiner confirms identity, then asks
short questions on familiar topics (home, hometown, work/studies, hobbies, food, weather,
daily routine). 2–3 topic areas, a few questions each. Goal: warm up, assess everyday
fluency.

**Part 2 — Long turn / cue card (3–4 min).** Examiner gives a cue card with a topic and
3–4 bullet points to cover. Candidate gets **1 minute to prepare** (may take notes), then
speaks **1–2 minutes** uninterrupted. Examiner then asks 1–2 short rounding-off questions.
Goal: sustained monologue.

Example cue card:
> *Describe a skill you would like to learn. You should say: what the skill is; why you
> want to learn it; how you would learn it; and explain how this skill would help you.*

**Part 3 — Two-way discussion (4–5 min).** Abstract, opinion-based questions thematically
linked to Part 2 (e.g. if Part 2 was a skill → "How has the way people learn skills
changed?", "Should schools teach more practical skills?"). Examiner probes, asks for
justification. Goal: discuss abstract ideas, develop and defend opinions.

## Examiner behavior rules (encode these in the PAL system prompt)

- Stay strictly in examiner role. Be warm, neutral, professional. Never teach, correct,
  hint, or give feedback **during** the test — that happens after.
- Ask one question at a time. Listen fully; use natural turn-taking, not interruptions.
- Keep your own turns short — the **candidate** should do ~80% of the talking.
- Follow the part structure in order for whichever parts are selected. Manage time.
- Part 2: read the cue card aloud, invite up to a minute of prep, and have the candidate
  begin when ready (pause-driven — the examiner stays silent and does NOT count a timer).
  Let them speak uninterrupted, allowing thinking pauses; ask the rounding-off question only
  once they have clearly finished.
- Part 3: ask follow-ups that push for reasons, examples, comparisons.
- At the end: thank the candidate and close. Do NOT announce scores in the call.

## PAL system-prompt template (paste into Tavus `system_prompt`)

This is the live prompt on PAL `pea55f8508c2` (≈640 tokens). It's deliberately prescriptive —
listing concrete example questions — so a fast LLM (`tavus-gemini-2.5-flash`) reliably runs the
IELTS script instead of drifting into open chat. **Lesson learned:** a loose "ask some questions
about familiar topics" prompt let the examiner wander off-script; naming actual questions fixed it.

```
You are Emma, a warm, professional, certified IELTS Speaking examiner running an official
mock Speaking test. You ASSESS only - never teach, correct, hint, give feedback, or break
character during the test.

Conduct ONLY the parts named in the conversational context, in order (Part 1, then Part 2,
then Part 3). If multiple parts are named, run them as ONE continuous test. If none are
named, run all three.

STYLE: Speak naturally and CONCISELY. Ask exactly ONE question or give ONE instruction per
turn, then STOP and listen. Keep your turns short - the candidate should talk about 80% of
the time. Never ask two questions at once. Never lecture or explain at length.

PART 1 - Interview (about 4 minutes): Greet briefly, confirm the candidate's name, then ask
everyday questions ONE at a time across 2-3 of these topics, with short follow-ups:
- Home: 'Do you live in a house or an apartment?', 'What is your favourite room?'
- Work or study: 'Do you work or are you a student?', 'What do you enjoy most about it?'
- Free time: 'What do you like to do in your free time?', 'How did you get into that?'
- Daily life: 'How do you usually start your day?'
Ask about 8 short questions in total, then move on.

PART 2 - Long turn (3-4 minutes): Tell the candidate you will give them a topic to talk
about for one to two minutes. Display the cue card on the Magic Canvas AND read it aloud.
Then say: 'You have up to a minute to prepare and make notes. Begin speaking whenever you are
ready.' Then STAY COMPLETELY SILENT - do not speak again until the candidate starts talking.
While they speak, do NOT interrupt; allow pauses for thinking and wait for them to continue.
When they have clearly finished and stop speaking, ask ONE brief rounding-off question.
CUE CARD: 'Describe a skill you would like to learn. You should say: what the skill is; why
you want to learn it; how you would learn it; and explain how this skill would help you.'

PART 3 - Discussion (about 4 minutes): Ask abstract, opinion-based questions linked to
learning and skills, ONE at a time, probing for reasons and examples:
- 'How has the way people learn new skills changed over the years?'
- 'Should schools focus more on practical skills or academic knowledge? Why?'
- 'Do you think some skills are becoming less important because of technology?'
- 'Is it better to learn a skill alone or with a teacher?'
Ask 4-5 questions with short follow-ups.

CLOSING: Thank the candidate and end politely. Do NOT give any score, feedback, or
correction at any point.
```

The conversation also sends a per-part `custom_greeting` (e.g. *"Hello, I'm Emma, and I'll be
your examiner for today's IELTS Speaking test. To begin, could you tell me your full name,
please?"*) so the very first line establishes the exam.

Pass which parts to run via the conversation's `conversational_context`, e.g.
`"Run Part 2 only."` or `"Run Parts 1, 2 and 3 as one continuous test."` — see the
**tavus-cvi** skill.

## The four assessment criteria (each scored 0–9)

1. **Fluency & Coherence (FC)** — speaks at length without effort; logical flow; discourse
   markers; minimal hesitation/self-correction/repetition.
2. **Lexical Resource (LR)** — range and precision of vocabulary; collocation, idiom,
   paraphrase; appropriacy.
3. **Grammatical Range & Accuracy (GRA)** — variety of structures (simple + complex);
   correctness; error frequency and whether errors impede meaning.
4. **Pronunciation (P)** — intelligibility; stress, rhythm, intonation; range of features.
   ⚠️ From a text transcript you have NO audio — score P conservatively and say so; lean on
   FC/LR/GRA. Enable Tavus word-level STT if you want a real signal.

**Overall band** = average of the four, rounded to the nearest **0.5** (e.g. 6.25→6.5,
6.1→6.0). Bands are 0–9; whole or half bands only.

Quick band anchors: **5** = modest, frequent errors but generally conveys meaning · **6** =
competent, some errors, generally effective · **7** = good operational command, occasional
errors · **8** = very good, rare errors, well-developed responses.

## Scoring = a Tavus post-call action (Tavus is the judge)

**We do NOT call OpenAI or Claude.** Tavus scores the test itself. A *post-call action* is a
Tavus tool (`trigger_type: post_call`) attached to the examiner PAL. When the call ends,
Tavus reads the **transcript + the Raven perception analysis** and uses its own LLM to fill
the tool's arguments — which we've defined to *be* the band-score report — then POSTs that
JSON to our Supabase `score` endpoint. The rubric lives entirely in the tool's `description`
and per-field `description`s (descriptions are the biggest quality lever). See the
**tavus-cvi** skill for the API mechanics.

**Already created live** (2026-06-27): tool `submit_ielts_assessment` = `t4efc3c554914`,
attached to PAL `pea55f8508c2`. Raven-1 perception is enabled on the PAL with end-of-call
queries about the candidate's confidence/composure/delivery, which feed Fluency &
Pronunciation. The tool's `delivery.api.url` is a placeholder — patch it to the deployed
`score` URL (see CLAUDE.md / lovable skill).

**Why this is better here:** zero external keys (no 401 risk), maximal "use of Tavus" for
Technical Execution, and the perception/delivery signal gives Pronunciation & Fluency a real
basis that a text transcript can't.

The report it POSTs is **flat JSON** (chosen for reliable AI-fill — no nested objects):
```
{
  "overall_band": 6.5,
  "fc_band": 6, "fc_evidence": "...", "fc_improvement": "...",
  "lr_band": 7, "lr_evidence": "...", "lr_improvement": "...",
  "gra_band": 6, "gra_evidence": "...", "gra_improvement": "...",
  "pron_band": 6, "pron_evidence": "...", "pron_improvement": "...",
  "summary": "...",
  "action_1": "...", "action_2": "...", "action_3": "..."
}
```
The `score` edge function just upserts this into the `reports` table keyed by
`conversation_id` (Tavus also sends `conversation_id` context). The report-card UI reads it.
The rubric text (band anchors, "quote the candidate's words," conservative pronunciation
note) is baked into the tool — see the live tool body in the **tavus-cvi** skill.

**Tuning the judge:** edit the tool, not an edge function — `PATCH /v2/tools/t4efc3c554914`
to refine any field `description` (e.g. stricter anchors). No redeploy.

**Optional richer rubric (fallback only):** if the post-call fill ever feels too shallow for
the demo, you *can* additionally run the transcript through an external LLM in the `score`
function (OpenAI `gpt-5.4` / Anthropic Claude) using the four-criteria rubric above. Not the
plan — Tavus-native scoring is the story. Only reach for it if the live fill underwhelms.
