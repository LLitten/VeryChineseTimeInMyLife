# START HERE: Mandarin study handoff

Paste this file at the start of a session with any AI model or tutor, along with whichever other file you need.

## Goal
Hold real conversations in Mandarin with friends, several of them from Taiwan. Speaking and listening with friends matters more than passing the HSK.

## Learner snapshot
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
| `vocab.csv` | 322 entries: 282 from the learner's handwritten notes, plus 40 everyday phrases and Taiwan words added by Claude (topics marked "(added)"). Columns: simplified, Taiwan form, pinyin, meaning, topic, literal parts, notes, and a `check` flag for unclear readings. Includes the zhuyin chart. |
| `grammar.md` | 38 grammar patterns with corrections, plus 13 practice sentences from the notes. |
| `error-patterns.md` | Mistakes the learner repeats, with fixes. Read this before writing practice material. |
| `exam-results.md` | Baseline exam results, by topic, with every missed word. |
| `study-plan.md` | Daily routine, weekly rhythm, a four-week roadmap and checkpoints. |
| `progress-log.md` | One line per session. Add a line at the end of each one. |
| `tools/` | Four self-contained HTML pages (notes table, recall quiz, vocabulary check, vocabulary exam). See the note in that folder's section below. |

## Session ritual
1. Paste this file plus the one or two files relevant to today's topic.
2. Say what you want to do (review, new words, quiz, writing, conversation prep).
3. Ask the model to grade honestly and to flag anything it isn't sure about.
4. At the end, add a dated line to `progress-log.md`.

## About `tools/`
The HTML pages are static and open in any browser. They were built in Claude, so some buttons (such as "Save as .txt" or "Save as CSV") depend on Claude's page features and may not appear elsewhere; copy-and-paste fallbacks exist where noted. If you host them on GitHub Pages, treat that as untested.

## Caution about this repo
It was transcribed from handwritten pencil notes. Items marked `check` in `vocab.csv` and ⚑ in `grammar.md` are uncertain. Treat everything here as a study aid, and let native-speaker friends have the last word on usage.
