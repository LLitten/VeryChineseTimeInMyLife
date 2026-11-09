# START HERE: Mandarin study handoff

Paste this file at the start of a session with any AI model or tutor, along with whichever other file you need.

## Goal
Hold real conversations in Mandarin with friends, several of them from Taiwan. Speaking and listening with friends matters more than passing the HSK.

## Learner snapshot
- **Organization:** material is grouped by the learner's own topics, which make sense to them by usage. HSK 1 (the 150-word HSK 2.0 list on hsk.academy) and AllSet's A1 grammar list are used as tags and checklists, not as the layout. Keep it that way when adding material.
- **Level:** about HSK 1. Baseline vocabulary exam: 96 of 150 words fully correct (64%). See `exam-results.md`.
- **Scripts:** simplified first. Taiwan Traditional forms ("TW") are tagged in the notes. Traditional gets added to active study later.
- **Pronunciation aid:** pinyin. Zhuyin is hard for the learner; a zhuyin chart is in `vocab.csv`.
- **How they study:** writes characters by hand to memorize them, checks stroke order on strokeorder.com, breaks characters into parts and literal meanings, uses a graded reader app and a dictionary app. Reference sites: the AllSet Chinese Grammar Wiki (HSK 1 grammar) and hsk.academy (HSK 1 word list).
- **Time and device:** about 30 minutes a day, mostly in the evening, plus a 3 to 5 minute daytime review. Mostly on a phone.
- **Native speakers:** friends who default to standard Mandarin with the learner. They are the authority on tones, listening and natural phrasing.

## How to teach this learner
- **Be honest.** Correct mistakes gently and explain why they are wrong.
- **Short rounds.** Five questions at a time, so they fit on a phone screen.
- **Recall over recognition.** Ask for written or typed answers, not multiple choice. Grade open answers and explain each miss.
- **Pinyin on first appearance only.** Give pinyin the first time a new word shows up, then use characters. The goal is to link characters to meaning, not to English through pinyin.
- **Grammar is harder than vocabulary for this learner.** Teach sentence frames and change one word at a time. Hold new patterns until the current ones feel easy.
- **Refer to material by topic.** The learner can't match "page 12" to their physical notes. Say "your note on negation" instead.
- **Don't over-claim.** Tones and pronunciation can't be judged from text. Say when you are unsure about naturalness, or whether something is Taiwan or mainland usage. Say which examples are your own and which come from the learner's notes.
- **Registers.** Flag slang and vulgar words as such.

## Files in this repo
| File | What it holds |
|---|---|
| `vocab.csv` | 369 entries grouped by the learner's own notebook topics, in notebook order. The `hsk1` column marks the 150 HSK 1 words (plus weekday and month patterns). The `source` column says where each entry came from: `notes` (the handwritten notes), `hsk-list` (HSK 1 words not yet in the notes, placed in the matching topic) or `added` (everyday phrases and Taiwan words added by Claude). Other columns: simplified, Taiwan form, pinyin, meaning, literal parts, notes, and a `check` flag for unclear readings. Includes the zhuyin chart. |
| `grammar.md` | Patterns grouped by the learner's notebook sections (sentence structure, questions, negation and so on). Each is tagged with its AllSet A1 number or "Beyond A1" and a status. An A1 checklist at the end shows the gaps. Then corrections and 13 practice sentences from the notes. |
| `error-patterns.md` | Mistakes the learner repeats, with fixes. Read this before writing practice material. |
| `exam-results.md` | Baseline exam results, by topic, with every missed word. |
| `study-plan.md` | Daily routine, weekly rhythm, a four-week roadmap and checkpoints. |
| `progress-log.md` | One line per session. Add a line at the end of each one. |
| `tools/` | Four self-contained HTML pages (notes table, recall quiz, vocabulary check, vocabulary exam). See the note in that folder's section below. The notes table still uses the older topic grouping and hasn't been updated to the new `vocab.csv` layout yet. |

## Session ritual
1. Paste this file plus the one or two files relevant to today's topic.
2. Say what you want to do (review, new words, quiz, writing, conversation prep).
3. Ask the model to grade honestly and to flag anything it isn't sure about.
4. At the end, add a dated line to `progress-log.md`.

## About `tools/`
The HTML pages are static and open in any browser. They were built in Claude, so some buttons (such as "Save as .txt" or "Save as CSV") depend on Claude's page features and may not appear elsewhere; copy-and-paste fallbacks exist where noted. If you host them on GitHub Pages, treat that as untested.

## Caution about this repo
It was transcribed from handwritten pencil notes. Items marked `check` in `vocab.csv` and ⚑ in `grammar.md` are uncertain. Treat everything here as a study aid, and let native-speaker friends have the last word on usage.
