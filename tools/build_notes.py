#!/usr/bin/env python3
"""Rebuild the data inside tools/mandarin-notes.html from vocab.csv and grammar.md.

Also rebuilds the topic pages in topics/ (see build_topics.py).

Run from the repo root after editing vocab.csv, grammar.md or guides/:

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
                      "When you're stuck", "Polite words", "On the phone"]),
    ("Food & drink", ["Drinks", "Food & flavors", "Eating out & ordering"]),
    ("Out & about", ["Transport", "Directions", "Places in town", "Shopping & money"]),
    ("Time", ["Clock & calendar", "Making plans", "Weather"]),
    ("Home & life", ["Daily routine", "Around the house", "School & work", "Animals & plants"]),
    ("Building blocks", ["Describing things", "Numbers & counting", "Grammar glue"]),
    ("Other", ["Strong language", "Pronunciation"]),
]
TYPE_ORDER = [
    "verb", "helping verb", "noun", "pronoun", "adjective", "adverb", "time word", "place",
    "direction word", "number", "measure word", "question word", "particle", "conjunction", "suffix",
    "phrase", "grammar pattern", "sentence", "sound",
]
# Which situations each grammar section belongs to (default: Grammar glue).
GRAMMAR_USES = {
    "Yes / no and other questions": ["Asking questions"],
    "Adverbs and describing": ["Describing things"],
    "Numbers, measure words, dates and time": ["Numbers & counting", "Clock & calendar"],
    "Location and \"there is\"": ["Directions"],
}
STATUS = {"✅": "✅ in your notes", "◐": "◐ partly in your notes", "○": "○ not learned yet"}


def vocab_entries():
    out = []
    with open(ROOT / "vocab.csv", encoding="utf8") as f:
        for r in csv.DictReader(f):
            out.append({
                "kind": "word", "s": r["simplified"], "t": r["traditional_tw"], "p": r["pinyin"], "z": r["zhuyin"],
                "m": r["meaning"], "topic": r["topic"], "type": r["type"],
                "uses": [u.strip() for u in r["use"].split(";") if u.strip()],
                "b": r["parts"], "n": r["note"], "hsk": r["hsk1"] == "yes", "src": r["source"],
                "flag": bool(r["check"]),
            })
    return out


def clean(md):
    """Strip simple Markdown so text reads plainly on the page."""
    md = re.sub(r"\*\*(.+?)\*\*", r"\1", md)
    md = re.sub(r"`(.+?)`", r"\1", md)
    md = re.sub(r"\*(.+?)\*", r"\1", md)
    return md.strip()


def grammar_entries():
    text = (ROOT / "grammar.md").read_text(encoding="utf8")
    entries, section, cur = [], None, None
    in_table = False

    def flush():
        if cur:
            entries.append(cur)

    for line in text.splitlines():
        if line.startswith("## AllSet A1 checklist") or line.startswith("## Corrections"):
            flush(); cur = None; section = None
            continue
        if line.startswith("## Practice sentences"):
            flush(); cur = None; section = "Practice sentences"; in_table = True
            continue
        if in_table:
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if len(cells) == 4 and cells[0] not in ("Chinese",) and not set(cells[0]) <= set("-"):
                entries.append({
                    "kind": "sentence", "s": cells[0], "t": "", "p": cells[1], "m": cells[2],
                    "topic": "Practice sentences", "type": "sentence", "uses": [], "b": "",
                    "n": cells[3], "hsk": False, "src": "notes", "flag": False,
                })
            continue
        m = re.match(r"^## \d+\. (.+)$", line)
        if m:
            flush(); cur = None; section = m.group(1).strip()
            continue
        m = re.match(r"^#### (.+)$", line)
        if m and section:
            flush()
            head = m.group(1)
            tag = re.search(r"`(.+?)`", head)
            sym = next((k for k in STATUS if k in head), "")
            title = re.sub(r"`.+?`", "", head)
            for k in list(STATUS) + ["⚑"]:
                title = title.replace(k, "")
            status = " · ".join(x for x in [STATUS.get(sym, ""), tag.group(1) if tag else ""] if x)
            cur = {
                "kind": "grammar", "s": title.strip(), "t": "", "p": "", "m": "", "n": "",
                "topic": "Grammar: " + section, "type": "grammar pattern",
                "uses": GRAMMAR_USES.get(section, ["Grammar glue"]), "b": "", "hsk": False,
                "src": "notes", "flag": "⚑" in head, "status": status, "extra": [],
            }
            continue
        if cur and line.startswith("- "):
            body = line[2:]
            if "⚑" in body:
                cur["flag"] = True
            lab = re.match(r"^(?:⚑ )?\*\*(.+?):\*\*\s*(.*)$", body)
            if lab and lab.group(1) in ("Pattern", "Use", "Rule") and not cur["m"]:
                cur["m"] = clean(lab.group(2))
            elif lab and lab.group(1) == "Example" and not cur["n"]:
                cur["n"] = clean(lab.group(2))
            else:
                cur["extra"].append(clean(body))
    flush()
    for e in entries:
        if e["kind"] == "grammar" and not e["m"] and e["extra"]:
            e["m"] = e["extra"].pop(0)
    return entries


def ordered(values, order):
    seen = list(dict.fromkeys(values))
    return [v for v in order if v in seen] + [v for v in seen if v not in order]


def main():
    entries = vocab_entries() + grammar_entries()
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
