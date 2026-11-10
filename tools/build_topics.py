#!/usr/bin/env python3
"""Build the textbook pages in topics/ from lessons/*.md, grammar/*.md and vocab.csv.

Normally run through tools/build_notes.py, which calls this at the end:

    python3 tools/build_notes.py

Pages built:
  topics/index.html        search, plus every topic with direct links to its sections
  topics/<topic>.html      one page per lesson file (lesson-<name>.html for lessons/,
                           grammar-<name>.html for grammar/). Contents at the top; each
                           "## Section" is a section of the page, laid out like an AllSet
                           Chinese Grammar Wiki article, with jump links to its parts.

Lesson format (lessons/ and grammar/ use the same one). Keep it short: no long paragraphs.
  # Title
  summary: one line for the chapter list and the top of the chapter page
  related: Lesson title; Grammar: <grammar lesson title>   (links, separated by semicolons)
  see: Yoyo course, Unit n: Title | URL; ...   "Also covered in Yoyo Chinese" links
  ## Section heading                a section of the topic page (linkable: <topic>.html#<slug>)
  tag: A1 #2                        level (grammar)
  pattern: Subject + 不 + verb       the structure, shown in a box (grammar)
  words: 早上, 晚上, 中午            key words, pulled from vocab.csv by exact `simplified`
                                    (for a word listed twice, add its type: 听 [measure word])
  - A short tip                     the first tip is the section's intro; the rest are notes.
                                    Tips containing ❌ go under "Watch out". (**bold**, `code` work)
  ### Examples
  - 中文 | pinyin | English | from    an example; the optional 4th part says where it's from
                                    (e.g. "your notes", "AllSet"); unmarked examples are Claude's
  - A: 中文 | pinyin | English        a line of dialogue (speaker before the colon)
  ### Try it
  - try: English prompt | 中文 | pinyin     answer stays hidden until tapped
  source: AllSet: Article title | https://...   a source for the section (URL optional)
  Any other line is a short paragraph, used as the intro.

The build stops if a lesson names a word that isn't in vocab.csv, and lists
vocab.csv words that no lesson uses.
"""
import html
import json
import re
import unicodedata

import build_notes as bn

ROOT = bn.ROOT
OUT = ROOT / "topics"
LESSONS = ROOT / "lessons"
GRAMMAR = ROOT / "grammar"
SOURCE_LABEL = {"notes": "your notes", "hsk-list": "HSK 1 list", "added": "added by Claude"}
CJK = r"[㄀-ㄯ一-鿿]"


# ---------------------------------------------------------------- helpers
def esc(s):
    return html.escape(s or "", quote=True)


def inline(s):
    s = esc(s)
    s = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", s)
    s = re.sub(r"`(.+?)`", r"<code>\1</code>", s)
    s = s.replace("❌", '<span class="bad" aria-label="wrong">✗</span>')
    return s


def slug(s):
    s = s.lower().replace("&", "and")
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-") or "section"


def plain(s):
    return "".join(c for c in unicodedata.normalize("NFD", s or "") if unicodedata.category(c) != "Mn").lower()


def size_class(s):
    n = len(re.findall(CJK, s or ""))
    return " l" if n >= 5 else " m" if n >= 4 else ""


def level_of(tag):
    if not tag:
        return ""
    m = re.match(r"(A1|A2|B1|B2)", tag)
    return m.group(1) if m else "Beyond A1"


def highlight(zh, keys):
    """Bold the key words inside an example sentence, as AllSet does."""
    if not keys:
        return esc(zh)
    pat = "|".join(re.escape(k) for k in sorted(keys, key=len, reverse=True))
    out, last = [], 0
    for m in re.finditer(pat, zh):
        out.append(esc(zh[last:m.start()]))
        out.append(f'<b class="kw">{esc(m.group())}</b>')
        last = m.end()
    out.append(esc(zh[last:]))
    return "".join(out)


# ---------------------------------------------------------------- parsing
def parse_lesson(path, prefix):
    name = re.sub(r"^\d+-", "", path.stem)
    L = {"title": name, "summary": "", "related": [], "see": [], "file": f"{prefix}-{name}.html",
         "base": f"{prefix}-{name}", "sections": [], "kind": prefix}
    sec = None
    for raw in path.read_text(encoding="utf8").splitlines():
        st = raw.strip()
        if not st:
            continue
        if st.startswith("# "):
            L["title"] = st[2:].strip()
        elif st.startswith("summary:") and sec is None:
            L["summary"] = st[8:].strip()
        elif st.startswith("related:") and sec is None:
            L["related"] = [x.strip() for x in st[8:].split(";") if x.strip()]
        elif st.startswith("see:") and sec is None:
            for item in st[4:].split(";"):
                label, _, url = item.partition("|")
                if label.strip():
                    L["see"].append((label.strip(), url.strip()))
        elif st.startswith("## "):
            sec = {"title": st[3:].strip(), "tag": "", "pattern": "", "intro": [], "words": [], "tips": [],
                   "examples": [], "try": [], "sources": []}
            L["sections"].append(sec)
        elif sec is None or st.startswith("### "):
            continue
        elif st.startswith("tag:"):
            sec["tag"] = st[4:].strip()
        elif st.startswith("pattern:"):
            sec["pattern"] = st[8:].strip()
        elif st.startswith("source:"):
            label, _, url = st[7:].partition("|")
            sec["sources"].append((label.strip(), url.strip()))
        elif st.startswith("words:"):
            sec["words"] += [w.strip() for w in st[6:].split(",") if w.strip()]
        elif st.startswith("- try:"):
            parts = [x.strip() for x in st[6:].split("|")] + ["", ""]
            sec["try"].append(parts[:3])
        elif st.startswith("- "):
            body = st[2:]
            m = re.match(r"^([A-Za-z][\w ]{0,11}):\s*(.+)$", body)
            if m and "|" in m.group(2):
                sec["examples"].append((m.group(1), [x.strip() for x in m.group(2).split("|")] + ["", "", ""]))
            elif "|" in body:
                sec["examples"].append((None, [x.strip() for x in body.split("|")] + ["", "", ""]))
            else:
                sec["tips"].append(body)
        else:
            sec["intro"].append(st)
    return L


def load(folder, prefix):
    files = sorted(folder.glob("*.md"), key=lambda p: int(re.match(r"\d+", p.stem).group()))
    return [parse_lesson(p, prefix) for p in files]


# ---------------------------------------------------------------- page shell
CSS = """
:root {
  --bg: #edf1f5; --surface: #ffffff; --ink: #16222e; --muted: #5a6978; --line: #cbd5df;
  --accent: #1d6f8a; --accent-soft: #dcecf2; --accent-ink: #ffffff; --bad: #b3261e; --good: #2e7d32;
  --serif: "Noto Serif SC", "Songti SC", "STSong", "SimSun", serif;
  --serif-tc: "Noto Serif TC", "Songti TC", "PMingLiU", "Noto Serif SC", serif;
  --sans: system-ui, -apple-system, "Segoe UI", "PingFang SC", "Microsoft YaHei", sans-serif;
}
@media (prefers-color-scheme: dark) {
  :root:not([data-theme="light"]) {
    --bg: #0f1820; --surface: #17232e; --ink: #e6edf3; --muted: #94a3b2; --line: #2b3b49;
    --accent: #5bb3d0; --accent-soft: #1b3644; --accent-ink: #0b1620; --bad: #ff8a80; --good: #81c784;
  }
}
:root[data-theme="dark"] {
  --bg: #0f1820; --surface: #17232e; --ink: #e6edf3; --muted: #94a3b2; --line: #2b3b49;
  --accent: #5bb3d0; --accent-soft: #1b3644; --accent-ink: #0b1620; --bad: #ff8a80; --good: #81c784;
}
* { box-sizing: border-box; }
body { margin: 0; background: var(--bg); color: var(--ink); font-family: var(--sans); font-size: 16px; line-height: 1.55; -webkit-text-size-adjust: 100%; }
main { max-width: 700px; margin: 0 auto; padding: calc(10px + env(safe-area-inset-top, 0px)) 16px calc(40px + env(safe-area-inset-bottom, 0px)); }
a { color: var(--accent); }
a:focus-visible, button:focus-visible, input:focus-visible, select:focus-visible, .peekable:focus-visible { outline: 3px solid var(--accent); outline-offset: 2px; }
.top { display: flex; flex-wrap: wrap; gap: 6px 12px; align-items: center; justify-content: space-between; font-size: 14px; color: var(--muted); }
.crumbs a { color: var(--muted); text-decoration: none; }
.crumbs a:hover { color: var(--accent); }
.mini { display: flex; flex: 1 1 180px; max-width: 260px; }
.mini input { width: 100%; min-height: 36px; padding: 4px 12px; font: inherit; font-size: 14px; color: var(--ink); background: var(--surface); border: 1.5px solid var(--line); border-radius: 18px; }
h1 { font-size: 27px; line-height: 1.2; margin: 14px 0 6px; }
h2 { font-size: 20px; margin: 30px 0 8px; padding-bottom: 4px; border-bottom: 2px solid var(--line); }
h3 { font-size: 16px; margin: 20px 0 6px; }
p { margin: 8px 0; }
code { font-size: 0.9em; }
.lead { margin: 0 0 12px; color: var(--muted); }
.intro { font-size: 17px; }
.zh, .zhi { font-family: var(--serif); }
.kw { color: var(--accent); }
.bad { color: var(--bad); font-weight: 700; }
/* fact box, like AllSet's */
.facts { display: grid; grid-template-columns: auto 1fr; gap: 4px 12px; margin: 10px 0 14px; padding: 10px 14px; font-size: 14px; background: var(--surface); border: 1.5px solid var(--line); border-radius: 12px; }
.facts dt { color: var(--muted); font-weight: 700; }
.facts dd { margin: 0; }
.chip { display: inline-block; margin: 0 4px 4px 0; padding: 1px 9px; font-size: 13px; text-decoration: none; color: var(--accent); border: 1px solid var(--accent); border-radius: 12px; }
.chip.lv { color: var(--muted); border-color: var(--line); }
.toc { margin: 6px 0 0; padding: 8px 14px 8px 32px; font-size: 14px; background: var(--surface); border: 1.5px solid var(--line); border-radius: 12px; }
.toc li { margin: 2px 0; }
.toggles { display: flex; flex-wrap: wrap; gap: 6px; position: sticky; top: 0; z-index: 5; margin: 10px -16px 0; padding: 8px 16px; background: var(--bg); }
.tg { appearance: none; min-height: 34px; padding: 4px 12px; font: inherit; font-size: 14px; color: var(--muted); background: none; border: 1.5px dashed var(--line); border-radius: 17px; cursor: pointer; }
.tg[aria-pressed="true"] { color: var(--ink); background: var(--surface); border-style: solid; border-color: var(--accent); }
.structure { margin: 8px 0; padding: 12px 16px; font-size: 18px; font-weight: 600; text-align: center; background: var(--surface); border: 1.5px solid var(--line); border-left: 5px solid var(--accent); border-radius: 10px; }
.structure .zhi { font-weight: 700; }
/* key words table */
.words { display: grid; gap: 0; background: var(--surface); border: 1.5px solid var(--line); border-radius: 12px; overflow: hidden; }
.row { display: grid; grid-template-columns: minmax(0, 1fr) minmax(0, 1fr) minmax(0, 1.3fr); gap: 10px; align-items: center; padding: 8px 12px; border-top: 1px solid var(--line); }
.row:first-child { border-top: 0; }
.no-tw .row { grid-template-columns: minmax(0, 1fr) minmax(0, 1.5fr); }
.no-tw .c-tw { display: none; }
.row .zh { display: block; font-weight: 700; font-size: 22px; line-height: 1.2; overflow-wrap: anywhere; }
.c-tw .zh { font-family: var(--serif-tc); }
.zh.same { color: var(--muted); font-weight: 500; }
.zh.m { font-size: 19px; } .zh.l { font-size: 16px; }
.py, .zy { display: block; font-size: 14px; color: var(--muted); overflow-wrap: anywhere; }
.zy { font-family: var(--serif-tc); }
.mean { font-size: 15px; }
.note, .from { display: block; font-size: 13px; color: var(--muted); }
.from { font-style: italic; }
/* examples, stacked like AllSet */
.examples { margin: 6px 0; padding: 0; list-style: none; }
.examples li { padding: 8px 0 8px 12px; border-left: 3px solid var(--accent-soft); margin: 6px 0; }
.examples .zhi { display: block; font-size: 19px; line-height: 1.4; }
.examples .mean { display: block; }
.who { display: inline-grid; place-items: center; width: 24px; height: 24px; margin-right: 6px; border-radius: 50%; background: var(--accent-soft); color: var(--accent); font: 700 13px var(--sans); vertical-align: 3px; }
.notes, .watch { margin: 6px 0; padding-left: 20px; }
.notes li, .watch li { margin: 4px 0; }
.watch { list-style: none; padding: 10px 14px; background: var(--surface); border: 1.5px solid var(--line); border-left: 5px solid var(--bad); border-radius: 10px; }
.hide-p .peekable:not(.peek) .py,
.hide-z .peekable:not(.peek) .zy,
.hide-m .peekable:not(.peek) .mean { filter: blur(7px); }
.peekable { cursor: pointer; }
.try { display: block; margin: 6px 0; padding: 10px 12px; background: var(--surface); border: 1.5px dashed var(--accent); border-radius: 12px; }
.try .q { display: block; font-weight: 600; }
.try .ans { display: block; margin-top: 4px; filter: blur(8px); }
.try.peek .ans { filter: none; }
.try .zhi { font-size: 19px; }
.try .pyx { display: block; font-size: 14px; color: var(--muted); }
.try .hint { display: block; font-size: 12px; color: var(--muted); }
.try.peek .hint { display: none; }
.refs { margin: 6px 0; padding-left: 20px; font-size: 14px; }
.refs li { margin: 3px 0; }
.cards { display: grid; gap: 8px; }
.card { display: block; padding: 12px 14px; color: var(--ink); text-decoration: none; background: var(--surface); border: 1.5px solid var(--line); border-radius: 12px; }
.card:hover { border-color: var(--accent); }
.card b { display: block; }
.card .sub { display: block; margin-top: 2px; font-size: 14px; color: var(--muted); }
.card .tags { display: block; margin-top: 6px; }
.card .tags span { display: inline-block; margin: 0 4px 2px 0; padding: 0 8px; font-size: 12px; color: var(--muted); border: 1px solid var(--line); border-radius: 10px; }
.pager { display: flex; justify-content: space-between; gap: 12px; margin-top: 30px; font-size: 15px; }
.pager a { max-width: 48%; }
.foot { margin-top: 30px; font-size: 13px; color: var(--muted); }
/* search page */
.search { display: block; width: 100%; min-height: 48px; padding: 10px 14px; font: inherit; font-size: 17px; color: var(--ink); background: var(--surface); border: 1.5px solid var(--line); border-radius: 12px; }
.filters { display: flex; flex-wrap: wrap; gap: 6px; margin: 10px 0 0; }
.fbtn { appearance: none; min-height: 34px; padding: 4px 12px; font: inherit; font-size: 14px; color: var(--ink); background: var(--surface); border: 1.5px solid var(--line); border-radius: 17px; cursor: pointer; }
.fbtn[aria-pressed="true"] { color: var(--accent-ink); background: var(--accent); border-color: var(--accent); }
.sel { min-height: 34px; padding: 4px 10px; font: inherit; font-size: 14px; color: var(--ink); background: var(--surface); border: 1.5px solid var(--line); border-radius: 17px; }
.count { margin: 12px 0 6px; font-size: 14px; color: var(--muted); }
.chapter-list { margin: 4px 0 0; padding-left: 20px; font-size: 14px; }
.contents { margin: 8px 0; padding: 10px 14px; background: var(--surface); border: 1.5px solid var(--line); border-radius: 12px; }
.contents ol { margin: 4px 0 0; padding-left: 22px; }
.contents li { margin: 3px 0; }
.lvl { margin-left: 4px; padding: 0 7px; font-size: 12px; color: var(--muted); border: 1px solid var(--line); border-radius: 9px; }
.sect { margin-top: 34px; scroll-margin-top: 56px; }
.sect h2 { font-size: 22px; border-bottom: 3px solid var(--accent); }
.sect h3 { scroll-margin-top: 56px; margin: 18px 0 6px; padding-bottom: 2px; font-size: 15px; letter-spacing: 0.03em; text-transform: uppercase; color: var(--muted); border-bottom: 1px solid var(--line); }
.jump { display: flex; flex-wrap: wrap; gap: 4px 12px; margin: 8px 0 0; font-size: 14px; }
.totop { margin: 14px 0 0; font-size: 14px; text-align: right; }
.card .ttl { font-weight: 700; text-decoration: none; }
.card .secs { display: block; margin-top: 6px; font-size: 14px; line-height: 1.7; }
#contents { scroll-margin-top: 56px; }
"""

TOGGLE_JS = """
(function () {
  var KEY = "topic-view";
  var view = { p: true, z: true, m: true, tw: true };
  try { var s = JSON.parse(localStorage.getItem(KEY) || "{}"); for (var k in view) if (k in s) view[k] = s[k]; } catch (e) {}
  var main = document.querySelector("main");
  function apply() {
    main.classList.toggle("hide-p", !view.p);
    main.classList.toggle("hide-z", !view.z);
    main.classList.toggle("hide-m", !view.m);
    main.classList.toggle("no-tw", !view.tw);
  }
  var box = document.getElementById("toggles");
  if (box) {
    [["p", "Pinyin"], ["z", "Zhuyin"], ["m", "Meaning"], ["tw", "TW column"]].forEach(function (t) {
      if (box.dataset.skip && box.dataset.skip.indexOf(t[0]) !== -1) return;
      var b = document.createElement("button");
      b.type = "button"; b.className = "tg"; b.textContent = t[1];
      b.setAttribute("aria-pressed", String(view[t[0]]));
      b.addEventListener("click", function () {
        view[t[0]] = !view[t[0]];
        b.setAttribute("aria-pressed", String(view[t[0]]));
        try { localStorage.setItem(KEY, JSON.stringify(view)); } catch (e) {}
        apply();
      });
      box.appendChild(b);
    });
  }
  document.addEventListener("click", function (ev) {
    var r = ev.target.closest(".peekable");
    if (r) r.classList.toggle("peek");
  });
  document.addEventListener("keydown", function (ev) {
    if ((ev.key === "Enter" || ev.key === " ") && ev.target.classList && ev.target.classList.contains("peekable")) {
      ev.preventDefault(); ev.target.classList.toggle("peek");
    }
  });
  apply();
})();
"""

MINI_SEARCH = ('<form class="mini" action="index.html" role="search"><input type="search" name="q" '
               'placeholder="Search lessons" aria-label="Search lessons"></form>')


def page(title, crumbs, body, toggles=True, skip="", script="", search=True):
    tg = f'<div class="toggles" id="toggles" data-skip="{skip}" aria-label="Show or hide"></div>' if toggles else ""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{esc(title)}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Noto+Serif+SC:wght@500;700&family=Noto+Serif+TC:wght@500;700&display=swap" rel="stylesheet">
<style>{CSS}</style>
</head>
<body>
<main>
<div class="top"><nav class="crumbs" aria-label="Breadcrumb">{crumbs}</nav>{MINI_SEARCH if search else ""}</div>
{tg}
{body}
<p class="foot">Built from handwritten notes. Tips and unmarked examples were written by Claude; each article lists its sources. Native-speaker friends have the last word on usage.</p>
</main>
<script>{TOGGLE_JS}{script}</script>
</body>
</html>
"""


# ---------------------------------------------------------------- pieces
def word_row(e):
    tw = e["t"] or e["s"]
    same = "" if e["t"] else " same"
    note = f'<span class="note">{esc(e["n"])}</span>' if e["n"] else ""
    if e.get("by"):
        note += f'<span class="from">from {esc(e["by"])}</span>'
    if e["type"] == "sound":
        tw_cell = '<span class="c-tw"></span>'
    else:
        zy = f'<span class="zy">{esc(e["z"])}</span>' if e.get("z") else ""
        tw_cell = f'<span class="c-tw"><span class="zh{size_class(tw)}{same}" lang="zh-Hant-TW">{esc(tw)}</span>{zy}</span>'
    return (f'<div class="row peekable" tabindex="0">'
            f'<span><span class="zh{size_class(e["s"])}" lang="zh-Hans">{esc(e["s"])}</span><span class="py">{esc(e["p"])}</span></span>'
            f'{tw_cell}<span><span class="mean">{esc(e["m"])}</span>{note}</span></div>')


def example_li(who, parts, keys):
    zh, py, en, src = parts[:4]
    w = f'<span class="who" aria-label="Speaker {esc(who)}">{esc(who)}</span>' if who else ""
    src = f'<span class="from">{esc(src)}</span>' if src else ""
    return (f'<li class="peekable" tabindex="0"><span class="zhi" lang="zh-Hans">{w}{highlight(zh, keys)}</span>'
            f'<span class="py">{esc(py)}</span><span class="mean">{esc(en)}</span>{src}</li>')


def try_card(prompt, zh, py):
    return (f'<div class="try peekable" tabindex="0" aria-label="Practice: {esc(prompt)}. Tap to show the answer.">'
            f'<span class="q">{esc(prompt)}</span>'
            f'<span class="ans"><span class="zhi" lang="zh-Hans">{esc(zh)}</span><span class="pyx">{esc(py)}</span></span>'
            f'<span class="hint">Say it, then tap to check</span></div>')


def structure_html(pattern):
    return re.sub(r"(%s+)" % CJK, r'<span class="zhi">\1</span>', inline(pattern))


# ---------------------------------------------------------------- sections
def make_articles(chapter, word_by_s):
    """One entry per "## Section"; each is a section of its chapter's page."""
    arts, seen = [], set()
    for i, s in enumerate(chapter["sections"], 1):
        words = [word_by_s[w] for w in s["words"]]
        watch = [t for t in s["tips"] if "❌" in t]
        tips = [t for t in s["tips"] if "❌" not in t]
        if s["intro"]:
            intro, notes = " ".join(s["intro"]), tips
        elif tips:
            intro, notes = tips[0], tips[1:]
        else:
            intro, notes = "", []
        level = level_of(s["tag"])
        counts = {}
        for w in words:
            for u in w["uses"]:
                if u != bn.SOUND_USE:
                    counts[u] = counts.get(u, 0) + 1
        ranked = sorted(counts, key=lambda u: -counts[u])
        # tag a situation only if it fits at least two of the words (or it's the main one)
        uses = [u for k, u in enumerate(ranked) if k == 0 or counts[u] >= 2]
        keys = set()
        if s["pattern"]:
            keys.update(re.findall(CJK + "+", s["pattern"]))
        for w in words:
            k = re.sub(r"[？?…!！。]", "", w["s"])
            if re.search(CJK, k):
                keys.add(k)
        keywords = sorted(keys, key=lambda k: (len(k), k))[:8]
        tags = (["Grammar"] if chapter["kind"] == "grammar" else ["Vocabulary"]) + ([level] if level else []) + uses[:4]
        anchor = slug(s["title"])
        if anchor in seen:
            anchor = f"{anchor}-{i}"
        seen.add(anchor)
        text = " ".join([s["title"], chapter["title"], s["pattern"], intro, " ".join(s["tips"]), " ".join(tags)]
                        + [" ".join([w["s"], w["t"], w["p"], w["m"], w["n"]]) for w in words]
                        + [" ".join(p[:3]) for _, p in s["examples"]])
        arts.append({"sec": s, "n": i, "title": s["title"], "anchor": anchor, "file": f'{chapter["file"]}#{anchor}',
                     "chapter": chapter, "words": words, "intro": intro, "notes": notes, "watch": watch,
                     "level": level, "uses": uses, "keys": keys, "keywords": keywords, "tags": tags,
                     "search": plain(text)})
    return arts


def sources_items(a):
    s, words = a["sec"], a["words"]
    items = []
    if words:
        counts = {}
        for w in words:
            k = f'from {w["by"]}' if w.get("by") else SOURCE_LABEL.get(w["src"], w["src"])
            counts[k] = counts.get(k, 0) + 1
        items.append("Words: " + ", ".join(f"{k} ({n})" for k, n in counts.items()))
    for label, url in s["sources"]:
        items.append(f'<a href="{esc(url)}" target="_blank" rel="noopener">{esc(label)}</a>' if url else esc(label))
    if s["tips"] or s["examples"] or s["try"]:
        items.append("Wording and unmarked examples: Claude" if s["sources"] else "Tips and unmarked examples: Claude")
    return items


def render_section(a):
    """One topic section, laid out like an AllSet article, on its chapter's page."""
    s, an = a["sec"], a["anchor"]
    out = [f'<section class="sect" id="{an}"><h2>{a["n"]}. {esc(a["title"])}</h2>']
    facts = []
    if a["level"]:
        facts.append(f'<dt>Level</dt><dd><span class="chip lv">{esc(s["tag"])}</span></dd>')
    if a["uses"]:
        facts.append("<dt>Used for</dt><dd>" + "".join(
            f'<a class="chip" href="index.html?tag={esc(u)}">{esc(u)}</a>' for u in a["uses"]) + "</dd>")
    if a["keywords"]:
        facts.append('<dt>Keywords</dt><dd><span class="zhi">' + "、".join(esc(k) for k in a["keywords"]) + "</span></dd>")
    if facts:
        out.append('<dl class="facts">' + "".join(facts) + "</dl>")
    if a["intro"]:
        out.append(f'<p class="intro">{inline(a["intro"])}</p>')
    parts = []
    if s["pattern"]:
        parts.append(("structure", "Structure"))
    if a["words"]:
        parts.append(("words", "Key words"))
    if s["examples"]:
        parts.append(("examples", "Dialogue" if any(w for w, _ in s["examples"]) else "Examples"))
    if a["notes"]:
        parts.append(("notes", "Notes"))
    if a["watch"]:
        parts.append(("watch", "Watch out"))
    if s["try"]:
        parts.append(("practice", "Practice"))
    parts.append(("sources", "Sources"))
    out.append('<nav class="jump" aria-label="In this section">' + " ".join(
        f'<a href="#{an}-{k}">{esc(t)}</a>' for k, t in parts) + "</nav>")
    titles = dict(parts)
    if s["pattern"]:
        out.append(f'<h3 id="{an}-structure">Structure</h3><div class="structure">{structure_html(s["pattern"])}</div>')
    if a["words"]:
        out.append(f'<h3 id="{an}-words">Key words</h3><div class="words">' + "".join(word_row(w) for w in a["words"]) + "</div>")
    if s["examples"]:
        out.append(f'<h3 id="{an}-examples">{titles["examples"]}</h3><ul class="examples">'
                   + "".join(example_li(w, p, a["keys"]) for w, p in s["examples"]) + "</ul>")
    if a["notes"]:
        out.append(f'<h3 id="{an}-notes">Notes</h3><ul class="notes">' + "".join(f"<li>{inline(t)}</li>" for t in a["notes"]) + "</ul>")
    if a["watch"]:
        out.append(f'<h3 id="{an}-watch">Watch out</h3><ul class="watch">' + "".join(f"<li>{inline(t)}</li>" for t in a["watch"]) + "</ul>")
    if s["try"]:
        out.append(f'<h3 id="{an}-practice">Practice</h3>' + "".join(try_card(*t) for t in s["try"]))
    out.append(f'<h3 id="{an}-sources">Sources</h3><ul class="refs">' + "".join(f"<li>{x}</li>" for x in sources_items(a)) + "</ul>")
    out.append('<p class="totop"><a href="#contents">↑ Contents</a></p></section>')
    return "\n".join(out)


def render_chapter(ch, arts, by_title, i, group, label):
    out = [f"<h1>{esc(ch['title'])}</h1>"]
    if ch["summary"]:
        out.append(f'<p class="intro">{esc(ch["summary"])}</p>')
    out.append(f'<p class="lead">{label} {i + 1} of {len(group)}. Jump to a section, or read top to bottom.</p>')
    out.append('<nav id="contents" class="contents" aria-label="Contents"><b>Contents</b><ol>' + "".join(
        f'<li><a href="#{a["anchor"]}">{esc(a["title"])}</a>'
        + (f' <span class="lvl">{esc(a["level"])}</span>' if a["level"] else "") + "</li>" for a in arts)
        + "</ol></nav>")
    out += [render_section(a) for a in arts]
    rel = []
    for n in ch["related"]:
        key = n[9:] if n.startswith("Grammar: ") else n
        if key not in by_title:
            raise SystemExit(f"Unknown related link in {ch['title']}: {n}")
        r = by_title[key]
        rel.append(f'<li><a href="{r["file"]}">{"Grammar" if r["kind"] == "grammar" else "Lesson"}: {esc(r["title"])}</a>'
                   f' <span class="note" style="display:inline">{esc(r["summary"])}</span></li>')
    tail = []
    if rel:
        tail.append('<h3>Related topics</h3><ul class="refs">' + "".join(rel) + "</ul>")
    if ch["see"]:
        tail.append('<h3>Also covered in Yoyo Chinese</h3><ul class="refs">' + "".join(
            f'<li><a href="{esc(u)}" target="_blank" rel="noopener">{esc(l)}</a></li>' for l, u in ch["see"]) + "</ul>")
    if tail:
        out.append('<section class="sect" id="see-also"><h2>See also</h2>' + "".join(tail) + "</section>")
    prev = f'<a href="{group[i-1]["file"]}">← {esc(group[i-1]["title"])}</a>' if i else '<a href="index.html">← All topics</a>'
    nxt = f'<a href="{group[i+1]["file"]}">{esc(group[i+1]["title"])} →</a>' if i + 1 < len(group) else '<a href="index.html">All topics →</a>'
    out.append(f'<nav class="pager">{prev}{nxt}</nav>')
    return "\n".join(out)


SEARCH_JS = """
(function () {
  var IDX = %s;
  function plain(s) { return (s || "").normalize("NFD").replace(/[\\u0300-\\u036f]/g, "").toLowerCase(); }
  var q = document.getElementById("q"), out = document.getElementById("results"), count = document.getElementById("count");
  var browse = document.getElementById("browse"), sit = document.getElementById("sit");
  var state = { kind: "", level: "", tag: "" };
  var params = new URLSearchParams(location.search);
  q.value = params.get("q") || "";
  if (params.get("tag")) state.tag = params.get("tag");
  sit.value = state.tag;
  document.querySelectorAll(".fbtn").forEach(function (b) {
    b.addEventListener("click", function () {
      var k = b.dataset.k, v = b.dataset.v;
      state[k] = state[k] === v ? "" : v;
      document.querySelectorAll('.fbtn[data-k="' + k + '"]').forEach(function (x) { x.setAttribute("aria-pressed", String(state[k] === x.dataset.v)); });
      run();
    });
  });
  sit.addEventListener("change", function () { state.tag = sit.value; run(); });
  q.addEventListener("input", run);
  function el(t, c, x) { var e = document.createElement(t); if (c) e.className = c; if (x !== undefined) e.textContent = x; return e; }
  function run() {
    var terms = plain(q.value).split(/\\s+/).filter(Boolean);
    var any = terms.length || state.kind || state.level || state.tag;
    browse.hidden = !!any; out.hidden = !any; count.hidden = !any;
    var url = new URL(location.href);
    url.searchParams.delete("q"); url.searchParams.delete("tag");
    if (q.value.trim()) url.searchParams.set("q", q.value.trim());
    if (state.tag) url.searchParams.set("tag", state.tag);
    history.replaceState(null, "", url);
    if (!any) return;
    var hits = IDX.filter(function (a) {
      if (state.kind && a.kind !== state.kind) return false;
      if (state.level && a.level !== state.level) return false;
      if (state.tag && a.tags.indexOf(state.tag) === -1) return false;
      return terms.every(function (t) { return a.x.indexOf(t) !== -1; });
    });
    hits.sort(function (a, b) {
      function score(z) { var s = 0, t = plain(z.t); terms.forEach(function (w) { if (t.indexOf(w) !== -1) s += 2; if (plain(z.tags.join(" ")).indexOf(w) !== -1) s += 1; }); return s; }
      return score(b) - score(a);
    });
    count.textContent = hits.length + (hits.length === 1 ? " article" : " articles");
    out.innerHTML = "";
    hits.forEach(function (a) {
      var c = el("a", "card"); c.href = a.u;
      c.appendChild(el("b", "", a.t));
      c.appendChild(el("span", "sub", a.c + " · " + a.i));
      var tg = el("span", "tags");
      a.tags.forEach(function (t) { tg.appendChild(el("span", "", t)); });
      c.appendChild(tg);
      out.appendChild(c);
    });
    if (!hits.length) out.appendChild(el("p", "lead", "Nothing found. Try fewer words, English or pinyin without tones, or clear a filter."));
  }
  run();
})();
"""


def render_index(lessons, grammar, arts_by_chapter, all_arts):
    uses = []
    for a in all_arts:
        for u in a["uses"]:
            if u not in uses:
                uses.append(u)
    order = [u for _, subs in bn.GROUPS for u in subs]
    uses.sort(key=lambda u: order.index(u) if u in order else 99)
    levels = [lv for lv in ("A1", "A2", "B1", "Beyond A1") if any(a["level"] == lv for a in all_arts)]
    idx = [{"t": a["title"], "u": a["file"], "c": a["chapter"]["title"], "i": re.sub(r"\*\*|`", "", a["intro"]),
            "kind": "Grammar" if a["chapter"]["kind"] == "grammar" else "Vocabulary", "level": a["level"],
            "tags": a["tags"], "x": a["search"]} for a in all_arts]

    def topics(group):
        return "".join(
            f'<div class="card"><a class="ttl" href="{ch["file"]}">{i}. {esc(ch["title"])}</a>'
            f'<span class="sub">{esc(ch["summary"])}</span><span class="secs">'
            + " · ".join(f'<a href="{a["file"]}">{esc(a["title"])}</a>' for a in arts_by_chapter[ch["file"]])
            + "</span></div>"
            for i, ch in enumerate(group, 1))
    body = ('<h1>Lessons</h1><p class="lead">A small textbook built from your notes. Each topic is one page, '
            'with sections laid out like the AllSet Chinese Grammar Wiki. Tap a section to go straight to it.</p>'
            '<input id="q" class="search" type="search" placeholder="Search: a topic, tag, word, pinyin or English" '
            'aria-label="Search lessons" autocomplete="off" autocapitalize="off" spellcheck="false">'
            '<div class="filters" role="group" aria-label="Filters">'
            '<button type="button" class="fbtn" data-k="kind" data-v="Vocabulary" aria-pressed="false">Vocabulary</button>'
            '<button type="button" class="fbtn" data-k="kind" data-v="Grammar" aria-pressed="false">Grammar</button>'
            + "".join(f'<button type="button" class="fbtn" data-k="level" data-v="{lv}" aria-pressed="false">{lv}</button>' for lv in levels)
            + '<select id="sit" class="sel" aria-label="Situation tag"><option value="">Any situation</option>'
            + "".join(f'<option value="{esc(u)}">{esc(u)}</option>' for u in uses) + "</select></div>"
            '<p id="count" class="count" aria-live="polite" hidden></p><div id="results" class="cards" hidden></div>'
            '<div id="browse">'
            f'<h2>Vocabulary</h2><div class="cards">{topics(lessons)}</div>'
            '<h2>Grammar</h2><p class="lead">Checked against the <a href="https://resources.allsetlearning.com/chinese/grammar/Main_Page" '
            'target="_blank" rel="noopener">AllSet Chinese Grammar Wiki</a>. Levels are AllSet\'s.</p>'
            f'<div class="cards">{topics(grammar)}</div></div>')
    script = SEARCH_JS % json.dumps(idx, ensure_ascii=False, separators=(",", ":"))
    return page("Mandarin lessons", '<a href="../index.html">← All tools</a>', body, toggles=False, script=script, search=False)


# ---------------------------------------------------------------- main
def main():
    vocab = bn.vocab_entries()
    word_by_s = {}
    for w in vocab:
        word_by_s.setdefault(w["s"], w)
        word_by_s[f'{w["s"]} [{w["type"]}]'] = w  # for words listed twice, e.g. 听 [measure word]
    lessons = load(LESSONS, "lesson")
    grammar = load(GRAMMAR, "grammar")
    everything = lessons + grammar
    by_title = {L["title"]: L for L in everything}

    missing = sorted({w for L in everything for s in L["sections"] for w in s["words"] if w not in word_by_s})
    if missing:
        raise SystemExit(f"Lessons name words that aren't in vocab.csv: {missing}")
    used = {id(word_by_s[w]) for L in everything for s in L["sections"] for w in s["words"]}
    unused = [w["s"] for w in vocab if id(w) not in used]

    OUT.mkdir(exist_ok=True)
    for old in OUT.glob("*.html"):
        old.unlink()

    arts_by_chapter, all_arts = {}, []
    for L in everything:
        arts_by_chapter[L["file"]] = make_articles(L, word_by_s)
        all_arts += arts_by_chapter[L["file"]]

    crumbs = '<a href="../index.html">All tools</a> › <a href="index.html">Lessons</a>'
    for group, label in ((lessons, "Vocabulary topic"), (grammar, "Grammar topic")):
        for i, ch in enumerate(group):
            arts = arts_by_chapter[ch["file"]]
            has_words = any(a["words"] for a in arts)
            (OUT / ch["file"]).write_text(page(f"{ch['title']} · Mandarin lessons", crumbs,
                                               render_chapter(ch, arts, by_title, i, group, label),
                                               skip="" if has_words else "ztw"), encoding="utf8")

    (OUT / "index.html").write_text(render_index(lessons, grammar, arts_by_chapter, all_arts), encoding="utf8")
    print(f"Wrote {len(lessons)} vocabulary and {len(grammar)} grammar topic pages ({len(all_arts)} sections), and topics/index.html")
    if unused:
        print(f"Not in any lesson yet ({len(unused)}): {' '.join(unused)}")


if __name__ == "__main__":
    main()
