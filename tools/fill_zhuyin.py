#!/usr/bin/env python3
"""Fill the zhuyin column of vocab.csv for rows where it is empty.

Needs the pypinyin package (pip install pypinyin). Run from the repo root:

    python3 tools/fill_zhuyin.py

The zhuyin is converted from the row's own pinyin, syllable by syllable, so the
two always agree (including tone changes such as 不 bú and neutral tones).
pypinyin is only used to know how many syllables each character has. Rows in
OVERRIDES are set by hand, for example where Taiwan's reading differs.
Existing zhuyin values are never overwritten, so hand corrections stay.
"""
import csv
import re
from pathlib import Path

import unicodedata

from pypinyin import Style, pinyin
from pypinyin.contrib.tone_convert import to_tone
from pypinyin.style.bopomofo import BopomofoConverter

BOPOMOFO = BopomofoConverter()

ROOT = Path(__file__).resolve().parent.parent
CSV = ROOT / "vocab.csv"

# Readings the library gets wrong for this file, or where Taiwan differs.
OVERRIDES = {
    "女儿": "ㄋㄩˇ ㄦˊ",
    "哪里 / 哪儿": "ㄋㄚˇ ㄌㄧˇ / ㄋㄚˇㄦ",
    "谁": "ㄕㄟˊ",
    "一点儿": "ㄧ ㄉㄧㄢˇㄦ",
    "地": "˙ㄉㄜ",
    "得": "ㄉㄟˇ",
    "星期": "ㄒㄧㄥ ㄑㄧˊ",
    "星期天": "ㄒㄧㄥ ㄑㄧˊ ㄊㄧㄢ",
    "星期一 – 星期六": "ㄒㄧㄥ ㄑㄧˊ ㄧ – ㄒㄧㄥ ㄑㄧˊ ㄌㄧㄡˋ",
}


TONES = {"\u0304": "1", "\u0301": "2", "\u030c": "3", "\u0300": "4"}


def letters(py):
    """Split pinyin into (letter, tone) pairs, dropping spaces and punctuation."""
    out = []
    for ch in unicodedata.normalize("NFD", py.lower()):
        if ch in TONES and out:
            out[-1][1] = TONES[ch]
        elif ch == "\u0308" and out:
            out[-1][0] = "v"
        elif "a" <= ch <= "z":
            out.append([ch, ""])
    return out


def mark(zy):
    """Put the neutral-tone dot in front of the syllable, as zhuyin is written."""
    return "˙" + zy.replace("˙", "") if "˙" in zy else zy


def to_zhuyin(hanzi, py):
    lets = letters(py)
    pos, out = 0, []
    for ch in hanzi:
        if not ("\u4e00" <= ch <= "\u9fff"):
            if ch.strip():
                out.append(ch)
            continue
        cands = pinyin(ch, style=Style.NORMAL, heteronym=True)[0]
        cands = sorted({c.replace("ü", "v") for c in cands}, key=len, reverse=True)
        here = "".join(l for l, _ in lets[pos:pos + 8])
        want = next((c for c in cands if here.startswith(c)), None)
        if want is None:
            raise ValueError(f"{hanzi}: pinyin '{py}' doesn't match any reading of {ch} {cands}")
        got = lets[pos:pos + len(want)]
        pos += len(want)
        tone = next((t for _, t in got if t), "")
        syl = to_tone(want + tone) if tone else want.replace("v", "ü")
        out.append(mark(BOPOMOFO.to_bopomofo(syl)))
    if pos != len(lets):
        raise ValueError(f"{hanzi}: leftover pinyin in '{py}'")
    text = " ".join(out)
    return re.sub(r"\s+([？?…，,！!])", r"\1", text)


def main():
    rows = list(csv.DictReader(open(CSV, encoding="utf8")))
    cols = list(rows[0].keys())
    if "zhuyin" not in cols:
        cols.insert(cols.index("pinyin") + 1, "zhuyin")
    filled = 0
    for r in rows:
        r.setdefault("zhuyin", "")
        if r["zhuyin"] or r["type"] == "sound":
            continue
        s = r["simplified"]
        r["zhuyin"] = OVERRIDES.get(s) or to_zhuyin(s, r["pinyin"])
        filled += 1
    with open(CSV, "w", encoding="utf8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    print(f"Filled zhuyin for {filled} rows")


if __name__ == "__main__":
    main()
