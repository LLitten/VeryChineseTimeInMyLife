# AGENTS.md

Instructions for any AI model, agent or tutor working with this repo. It holds one learner's Mandarin notes, transcribed from handwritten pages, plus study tools published at **https://llitten.github.io/VeryChineseTimeInMyLife/**.

## Goal
Hold real conversations in Mandarin with friends, several of them from Taiwan. Speaking and listening with friends matters more than passing the HSK.

## The learner
- **Level:** about HSK 1. Baseline vocabulary exam: 96 of 150 (64%). Details in `progress.md`.
- **Scripts:** simplified first. Taiwan Traditional forms ("TW") are noted for recognition; active study of Traditional comes later.
- **Pronunciation aid:** pinyin. Zhuyin is hard for the learner; a chart is in `vocab.csv`.
- **How they study:** writes characters by hand, checks stroke order on strokeorder.com, breaks characters into parts and literal meanings, uses a graded reader app and a dictionary app. Reference sites: the AllSet Chinese Grammar Wiki and hsk.academy.
- **Time and device:** about 30 minutes a day, mostly in the evening, plus a 3 to 5 minute daytime review. Mostly on a phone.
- **Native speakers:** friends who default to standard Mandarin with the learner. They are the authority on tones, listening and natural phrasing.

## How to teach
- **Be honest.** Correct mistakes gently and explain why they are wrong.
- **Short rounds.** Five questions at a time, so they fit on a phone screen.
- **Recall over recognition.** Ask for typed or written answers, not multiple choice. Grade open answers and explain each miss.
- **Pinyin on first appearance only.** Then use characters, to link characters to meaning rather than to English through pinyin.
- **Grammar is harder than vocabulary.** Teach sentence frames and change one word at a time. Hold new patterns until the current ones feel easy.
- **Refer to material by topic,** not page numbers: "your note on negation."
- **Read `progress.md` before writing practice material.** It lists the mistakes this learner repeats.
- **Don't over-claim.** Tones and pronunciation can't be judged from text. Say when you're unsure about naturalness or about Taiwan vs mainland usage. Say which examples are yours and which come from the learner's notes.
- **Registers.** Flag slang and vulgar words as such.

## Files
| File | What it holds |
|---|---|
| `vocab.csv` | Every word and phrase (369 rows), grouped by the learner's notebook topics in notebook order. Columns are described below. |
| `grammar.md` | Grammar grouped by the learner's notebook sections. Each pattern has a status (✅ in notes, ◐ partly, ○ not learned) and an AllSet tag (`A1 #n` or `Beyond A1`). Ends with an A1 checklist, corrections to the notes, and 13 practice sentences from the notes. |
| `progress.md` | Session log, baseline exam results, and the mistakes to watch for. |
| `study-plan.md` | Daily routine, weekly rhythm, four-week roadmap and checkpoints. |
| `index.html`, `tools/` | The website: a home page and four pages (notes, recall quiz, vocabulary check, vocabulary exam). |
| `tools/build_notes.py` | Regenerates the notes page's data from `vocab.csv` and `grammar.md`. |

### `vocab.csv` columns
- `simplified`, `traditional_tw`, `pinyin`, `meaning`
- `topic`: the learner's notebook topic. **This is the organizing scheme; keep it.**
- `type`: verb, noun, adjective, measure word, time word, direction word, phrase, and so on.
- `use`: situations, separated by semicolons, for example `Food & drink; Shopping & money`. Reuse the existing situation names (the list is in `tools/build_notes.py`).
- `parts`: literal meaning of each character. `note`: usage notes.
- `hsk1`: `yes` if the word is on the 150-word HSK 1 list (HSK 2.0, hsk.academy).
- `source`: `notes` (handwritten notes), `hsk-list` (HSK 1 word not yet in the notes), or `added` (added by an AI; check with friends).
- `check`: `check` if a reading was unclear or the note may be wrong.

## Rules for changing the repo
- **Keep the learner's organization.** Group by their notebook topics and sections. HSK 1 and AllSet A1 are tags and checklists, not the layout.
- **Mark where things came from.** New words get `source` = `added` unless they come from the learner. Examples you write in `grammar.md` must not be marked *(your notes)*.
- **Flag, don't silently fix.** When a note from the learner is wrong, keep it recognizable, state the correction, and mark it (⚑ in `grammar.md`, or `check` / a note in `vocab.csv`).
- **Rebuild the site data** after editing `vocab.csv` or `grammar.md`: `python3 tools/build_notes.py`. The page can't parse other formats, so keep `grammar.md`'s heading structure (`## n. Section`, `#### Pattern` with status and tag, `- **Label:** text` bullets).
- **Publishing:** the site deploys from `main` with GitHub Pages, usually within a couple of minutes of a push. Pages must stay mobile-friendly and self-contained (no build step; Google Fonts is the only external resource).
- **Log sessions:** add a dated line to the session log in `progress.md` at the end of each study session.
- **The repo is public.** Don't add anything private about the learner or their friends.

## Session ritual for the learner
1. Point the model at this file, plus the one or two files relevant to today's topic.
2. Say what you want to do: review, new words, quiz, writing, or conversation prep.
3. Ask it to grade honestly and to flag anything it isn't sure about.
4. At the end, add a line to the session log in `progress.md`.

## Caution
Transcribed from handwritten pencil notes. Items marked `check` in `vocab.csv` and ⚑ in `grammar.md` are uncertain. Treat everything as a study aid; native-speaker friends have the last word on usage.
