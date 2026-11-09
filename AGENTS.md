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
| `vocab.csv` | Every word and phrase (383 rows, including the zhuyin chart), grouped by the learner's notebook topics in notebook order. Columns are described below. |
| `grammar/` | Grammar lessons, one per notebook section, plus practice sentences from the notes. Same format as `lessons/`, with a level tag, a pattern box and `source:` lines per section. Checked against the AllSet Chinese Grammar Wiki, the learner's main reference. |
| `progress.md` | Everything personal: session log, exam results, mistakes to watch, the A1 grammar checklist with what's learned, corrections to the handwritten notes, and open questions. |
| `study-plan.md` | Daily routine, weekly rhythm, four-week roadmap and checkpoints. |
| `lessons/` | Lessons in Markdown, one per situation group plus Pronunciation. Each section lists its words (pulled from `vocab.csv`), short tips, example sentences and a "Try it" practice. Format is described at the top of `tools/build_topics.py`. |
| `index.html`, `tools/` | The website: a home page, the notes page (words and phrases only), recall quiz, vocabulary check and vocabulary exam. |
| `topics/` | Generated lesson and grammar pages. Don't edit by hand. |
| `tools/build_notes.py` | Regenerates the notes page's word list from `vocab.csv`, then the lesson and grammar pages (via `tools/build_topics.py`). Also defines the situation groups. |
| `tools/fill_zhuyin.py` | Fills in zhuyin for new `vocab.csv` rows. |

### `vocab.csv` columns
- `simplified`, `traditional_tw` (blank when the same as simplified), `pinyin`, `meaning`
- `zhuyin`: generated from the row's pinyin by `tools/fill_zhuyin.py` (needs `pip install pypinyin`), which fills empty cells only. Hand-set readings, such as Taiwan's 星期 xīngqí, live in that script's `OVERRIDES`.
- `topic`: the learner's notebook topic. **This is the organizing scheme; keep it.**
- `type`: verb, noun, adjective, measure word, time word, direction word, phrase, and so on.
- `use`: situations, separated by semicolons, for example `Drinks; Eating out & ordering`. Use only the names in `GROUPS` in `tools/build_notes.py` (the build stops on unknown names). To add a situation, add it there first.
- `parts`: literal meaning of each character. `note`: usage notes.
- `hsk1`: `yes` if the word is on the 150-word HSK 1 list (HSK 2.0, hsk.academy). Reference only: the learner isn't studying for the HSK exam, so the site doesn't filter by it.
- `source`: `notes` (handwritten notes), `hsk-list` (HSK 1 word not yet in the notes), or `added` (added by an AI; check with friends).
- `taught_by`: who taught the learner this word, for words learned from friends. "a friend" is a placeholder for the learner to fill in. The repo is public, so use a first name or nickname only. Shown on lesson word cards, in lesson source lines, and in the notes page's word details.
- `check`: `check` only if a fact itself is uncertain. Currently none are set.

## Rules for changing the repo
- **Keep the learner's organization.** Group by their notebook topics and sections. HSK 1 and AllSet A1 are tags and checklists, not the layout.
- **Mark where things came from.** New words get `source` = `added` unless they come from the learner. Every lesson section should have `source:` lines where a source exists: the AllSet article (with its URL) or other reputable source it was checked against, or "Your notes" when nothing else covers it. Mark examples taken from a source in their 4th field (`your notes`, `AllSet`); unmarked examples are understood to be written by the AI.
- **Keep notes plain.** Notes in `vocab.csv`, `lessons/` and `grammar/` are general reference: no "your note says…", quiz results or past mistakes. Anything personal (corrections to the handwritten notes, exam and quiz results, mistakes, what's been learned, open questions) goes in `progress.md`. When a handwritten note is wrong, write the correct version plainly and log the correction in `progress.md`.
- **Vocabulary is words and phrases only.** Keep each `note` to one short line (about 60 characters). Longer explanations, patterns and examples belong in a lesson.
- **Every word belongs in a lesson.** When adding a word to `vocab.csv`, add it to a lesson's `words:` line too; the build lists any word no lesson uses. Words a lesson introduces must be in `vocab.csv`.
- **Lessons stay short:** a few one-line tips per section, not paragraphs. Example sentences should mostly use words already in `vocab.csv`.
- **Yoyo Chinese** (https://yoyochinese.com/courses) is the learner's other source, and the notebook's grammar follows its Chinese Grammar Series. Lessons are videos; the lecture-notes PDF under each video is openly linked only for the free preview lessons (Grammar Series lessons 1–9: word order, negation, yes/no questions). Cite those with a `source:` line linking the lesson's notes page. Other Yoyo lessons are behind a login: point to them with a `see:` line only, and don't fetch their PDFs by guessing URLs. Don't commit Yoyo PDFs to this public repo.
- **Grammar follows AllSet.** The AllSet Chinese Grammar Wiki (https://resources.allsetlearning.com/chinese/grammar/Main_Page) is the learner's main reference. Check grammar rules and levels against it, and say so when the notes and AllSet disagree.
- **Rebuild the site data** after editing `vocab.csv`, `lessons/` or `grammar/`: `python3 tools/fill_zhuyin.py` (for new words), then `python3 tools/build_notes.py`. The lesson format is described at the top of `tools/build_topics.py`.
- **Publishing:** the site deploys from `main` with GitHub Pages, usually within a couple of minutes of a push. Pages must stay mobile-friendly and self-contained (no build step; Google Fonts is the only external resource).
- **Log sessions:** add a dated line to the session log in `progress.md` at the end of each study session.
- **The repo is public.** Don't add anything private about the learner or their friends.

## Session ritual for the learner
1. Point the model at this file, plus the one or two files relevant to today's topic.
2. Say what you want to do: review, new words, quiz, writing, or conversation prep.
3. Ask it to grade honestly and to flag anything it isn't sure about.
4. At the end, add a line to the session log in `progress.md`.

## Caution
Transcribed from handwritten pencil notes. Open questions about the notes are listed in `progress.md`. Treat everything as a study aid; native-speaker friends have the last word on usage.
