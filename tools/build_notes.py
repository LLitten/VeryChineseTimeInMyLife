#!/usr/bin/env python3
"""Rebuild the word list inside tools/mandarin-notes.html from vocab.csv.

The notes page holds words and phrases only (not grammar, and not the zhuyin
chart, whose rows have type "sound"). This script also rebuilds the lesson and
grammar pages in topics/ (see build_topics.py).

Run from the repo root after editing vocab.csv, lessons/ or grammar/:

    python3 tools/build_notes.py

Only the block between the DATA START and DATA END markers in the page is replaced.
"""
import csv
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PAGE = ROOT / "tools" / "mandarin-notes.html"

# Situations, grouped. vocab.csv's `use` column holds the situation names
# (several per word, separated by semicolons). The page shows the groups first.
GROUPS = [
    ("People", ["Greetings & goodbyes", "Introducing yourself", "Family & friends"]),
    ("Conversation", ["Reacting & agreeing", "Feelings & opinions", "Asking questions",
                      "When you're stuck", "Polite words", "On the phone", "Strong language"]),
    ("Food & drink", ["Drinks", "Food & flavors", "Eating out & ordering"]),
    ("Out & about", ["Transport", "Directions", "Places in town", "Shopping & money"]),
    ("Time", ["Clock & calendar", "Making plans", "Weather"]),
    ("Home & life", ["Daily routine", "Around the house", "School & work", "Animals & plants"]),
    ("Building blocks", ["Describing things", "Numbers & counting", "Grammar glue"]),
]
# Zhuyin chart rows (type "sound") use this situation. They appear in the
# Pronunciation lesson, not on the notes page.
SOUND_USE = "Pronunciation"
TYPE_ORDER = [
    "verb", "helping verb", "noun", "pronoun", "adjective", "adverb", "time word", "place",
    "direction word", "number", "measure word", "question word", "particle", "conjunction", "suffix",
    "phrase", "grammar pattern", "sentence", "sound",
]


def vocab_entries():
    out = []
    with open(ROOT / "vocab.csv", encoding="utf8") as f:
        for r in csv.DictReader(f):
            out.append({
                "kind": "word", "s": r["simplified"], "t": r["traditional_tw"], "p": r["pinyin"], "z": r["zhuyin"],
                "m": r["meaning"], "topic": r["topic"], "type": r["type"],
                "uses": [u.strip() for u in r["use"].split(";") if u.strip()],
                "b": r["parts"], "n": r["note"], "hsk": r["hsk1"] == "yes", "src": r["source"], "by": r.get("taught_by", ""),
                "flag": bool(r["check"]),
            })
    return out


def ordered(values, order):
    seen = list(dict.fromkeys(values))
    return [v for v in order if v in seen] + [v for v in seen if v not in order]


def main():
    entries = [e for e in vocab_entries() if e["type"] != "sound"]
    known = {u for _, subs in GROUPS for u in subs}
    unknown = sorted({u for e in entries for u in e["uses"]} - known)
    if unknown:
        raise SystemExit(f"Situations not listed in GROUPS: {unknown}")
    data = {
        "topics": list(dict.fromkeys(e["topic"] for e in entries)),
        "types": ordered([e["type"] for e in entries], TYPE_ORDER),
        "groups": [{"name": g, "uses": subs} for g, subs in GROUPS],
        "entries": entries,
    }
    page = PAGE.read_text(encoding="utf8")
    start = page.index("/* DATA START")
    start = page.index("\n", start) + 1
    end = page.index("/* DATA END */")
    blob = "var DATA = " + json.dumps(data, ensure_ascii=False, separators=(",", ":")) + ";\n"
    PAGE.write_text(page[:start] + blob + page[end:], encoding="utf8")
    kinds = {}
    for e in entries:
        kinds[e["kind"]] = kinds.get(e["kind"], 0) + 1
    print(f"Wrote {len(entries)} entries {kinds} to {PAGE.relative_to(ROOT)}")

    import build_topics  # topic pages share this data; build them too
    build_topics.main()


if __name__ == "__main__":
    main()
