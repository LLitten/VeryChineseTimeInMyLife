#!/usr/bin/env python3
"""Build the lesson pages in topics/ from lessons/*.md, grammar/*.md and vocab.csv.

Normally run through tools/build_notes.py, which calls this at the end:

    python3 tools/build_notes.py

Pages built:
  topics/index.html               list of vocabulary and grammar lessons
  topics/lesson-<name>.html       one per lessons/<n>-<name>.md (vocabulary), in number order
  topics/grammar-<name>.html      one per grammar/<n>-<name>.md, in number order

Lesson format (lessons/ and grammar/ use the same one). Keep it short: no long paragraphs.
  # Title
  summary: one line for the index and the top of the page
  related: Lesson title; Grammar: <grammar lesson title>   (links, separated by semicolons)
  see: Yoyo course, Unit n: Title | URL; ...   "Also covered in Yoyo Chinese" links (videos; content not checked)
  ## Section heading
  tag: A1 #2                      level badge (grammar)
  pattern: Subject + 不 + verb     the structure, shown in a box (grammar)
  words: 早上, 晚上, 中午          word cards, pulled from vocab.csv by exact `simplified`
                                  (for a word listed twice, add its type: 听 [measure word])
  - A short tip                   tips (**bold** and `code` work)
  ### Examples
  - 中文 | pinyin | English | from  an example; the optional 4th part says where it's from
                                  (e.g. "your notes", "AllSet"); unmarked examples are Claude's
  - A: 中文 | pinyin | English      a line of dialogue (speaker before the colon)
  ### Try it
  - try: English prompt | 中文 | pinyin     answer stays hidden until tapped
  source: AllSet: Article title | https://...   a source line for the section (URL optional)
  Any other line is a short paragraph.

The build stops if a lesson names a word that isn't in vocab.csv, and lists
vocab.csv words that no lesson uses.
"""
import html
import re
from pathlib import Path

import build_notes as bn

ROOT = bn.ROOT
OUT = ROOT / "topics"
LESSONS = ROOT / "lessons"
GRAMMAR = ROOT / "grammar"


def esc(s):
    return html.escape(s or "", quote=True)


def inline(s):
    s = esc(s)
    s = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", s)
    s = re.sub(r"`(.+?)`", r"<code>\1</code>", s)
    return s


def slug(s):
    s = s.lower().replace("&", "and")
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")



CSS = """
:root {
  --bg: #edf1f5; --surface: #ffffff; --ink: #16222e; --muted: #5a6978; --line: #cbd5df;
  --accent: #1d6f8a; --accent-soft: #dcecf2; --accent-ink: #ffffff;
  --serif: "Noto Serif SC", "Songti SC", "STSong", "SimSun", serif;
  --serif-tc: "Noto Serif TC", "Songti TC", "PMingLiU", "Noto Serif SC", serif;
  --sans: system-ui, -apple-system, "Segoe UI", "PingFang SC", "Microsoft YaHei", sans-serif;
}
@media (prefers-color-scheme: dark) {
  :root:not([data-theme="light"]) {
    --bg: #0f1820; --surface: #17232e; --ink: #e6edf3; --muted: #94a3b2; --line: #2b3b49;
    --accent: #5bb3d0; --accent-soft: #1b3644; --accent-ink: #0b1620;
  }
}
:root[data-theme="dark"] {
  --bg: #0f1820; --surface: #17232e; --ink: #e6edf3; --muted: #94a3b2; --line: #2b3b49;
  --accent: #5bb3d0; --accent-soft: #1b3644; --accent-ink: #0b1620;
}
* { box-sizing: border-box; }
body { margin: 0; background: var(--bg); color: var(--ink); font-family: var(--sans); font-size: 16px; line-height: 1.45; -webkit-text-size-adjust: 100%; }
main { max-width: 680px; margin: 0 auto; padding: calc(10px + env(safe-area-inset-top, 0px)) 16px calc(40px + env(safe-area-inset-bottom, 0px)); }
.crumbs { font-size: 14px; color: var(--muted); }
.crumbs a { color: var(--muted); text-decoration: none; }
.crumbs a:hover, .crumbs a:focus-visible { color: var(--accent); }
h1 { font-size: 26px; line-height: 1.2; margin: 10px 0 6px; }
.lead { margin: 0 0 14px; color: var(--muted); }
h2 { font-size: 19px; margin: 28px 0 8px; }
h2 small { font-size: 14px; font-weight: 400; color: var(--muted); margin-left: 6px; }
h3 { font-size: 16px; margin: 0 0 4px; }
p { margin: 8px 0; }
a { color: var(--accent); }
code { font-size: 0.9em; }
.toggles { display: flex; flex-wrap: wrap; gap: 6px; margin: 10px 0 4px; position: sticky; top: 0; z-index: 5; padding: 8px 0; background: var(--bg); }
.tg { appearance: none; min-height: 36px; padding: 5px 12px; font: inherit; font-size: 14px; color: var(--muted); background: none; border: 1.5px dashed var(--line); border-radius: 18px; cursor: pointer; }
.tg[aria-pressed="true"] { color: var(--ink); background: var(--surface); border-style: solid; border-color: var(--accent); }
.tg:focus-visible, .row:focus-visible, a:focus-visible { outline: 3px solid var(--accent); outline-offset: 2px; }
.list { display: grid; gap: 6px; }
.row { display: grid; grid-template-columns: minmax(0, 1fr) minmax(0, 1fr) minmax(0, 1.2fr); gap: 10px; align-items: center; padding: 10px; background: var(--surface); border: 1.5px solid var(--line); border-radius: 12px; }
.no-tw .row { grid-template-columns: minmax(0, 1fr) minmax(0, 1.4fr); }
.no-tw .c-tw { display: none; }
.zh { display: block; font-family: var(--serif); font-weight: 700; font-size: 24px; line-height: 1.2; overflow-wrap: anywhere; }
.c-tw .zh { font-family: var(--serif-tc); }
.zh.same { color: var(--muted); font-weight: 500; }
.zh.m { font-size: 20px; } .zh.l { font-size: 17px; }
.py, .zy { display: block; margin-top: 3px; font-size: 15px; color: var(--muted); overflow-wrap: anywhere; }
.zy { font-family: var(--serif-tc); }
.mean { font-size: 15px; }
.note { display: block; margin-top: 4px; font-size: 13px; color: var(--muted); }
.phrase { display: block; padding: 10px 12px; background: var(--surface); border: 1.5px solid var(--line); border-radius: 12px; }
.phrase .zh { font-size: 21px; }
.phrase .mean { display: block; margin-top: 3px; }
.dlg { display: grid; grid-template-columns: 30px minmax(0, 1fr); gap: 10px; padding: 10px 12px; background: var(--surface); border: 1.5px solid var(--line); border-radius: 12px; }
.who { display: grid; place-items: center; width: 30px; height: 30px; border-radius: 50%; background: var(--accent-soft); color: var(--accent); font-weight: 700; font-size: 14px; }
.dlg .zh { font-size: 19px; }
.dlg .mean { display: block; margin-top: 3px; }
.hide-p .row:not(.peek) .py, .hide-p .phrase:not(.peek) .py, .hide-p .dlg:not(.peek) .py,
.hide-z .row:not(.peek) .zy,
.hide-m .row:not(.peek) .mean, .hide-m .phrase:not(.peek) .mean, .hide-m .dlg:not(.peek) .mean { filter: blur(7px); }
.peekable { cursor: pointer; }
.pat { padding: 12px 14px; background: var(--surface); border: 1.5px solid var(--line); border-radius: 12px; margin-top: 8px; }
.tag { display: inline-block; margin-left: 4px; padding: 1px 8px; font-size: 12px; font-weight: 400; color: var(--muted); border: 1px solid var(--line); border-radius: 9px; vertical-align: 2px; }
.ex { font-family: var(--serif); font-size: 17px; }
.pat ul { margin: 6px 0 0; padding-left: 18px; }
.cards { display: grid; gap: 8px; }
.card { display: block; padding: 12px 14px; color: var(--ink); text-decoration: none; background: var(--surface); border: 1.5px solid var(--line); border-radius: 12px; }
.card:hover { border-color: var(--accent); }
.card b { display: block; }
.card span { display: block; margin-top: 2px; font-size: 14px; color: var(--muted); }
.subnav { display: flex; flex-wrap: wrap; gap: 6px; margin: 6px 0 0; padding: 0; list-style: none; }
.subnav a { display: inline-block; padding: 4px 11px; font-size: 14px; text-decoration: none; border: 1px solid var(--line); border-radius: 15px; background: var(--surface); }
.pager { display: flex; justify-content: space-between; gap: 12px; margin-top: 28px; font-size: 15px; }
.foot { margin-top: 28px; font-size: 13px; color: var(--muted); }
.lesson { margin-top: 30px; padding-top: 4px; border-top: 2px solid var(--line); scroll-margin-top: 60px; }
.lesson h2 { margin-top: 14px; }
.lesson h3 { margin: 18px 0 8px; font-size: 13px; font-weight: 700; letter-spacing: 0.04em; text-transform: uppercase; color: var(--muted); }
.tips { margin-top: 14px; padding: 2px 14px 10px; background: var(--accent-soft); border-radius: 12px; }
.tips ul { margin: 0; padding-left: 18px; }
.tips li { margin-top: 5px; }
.try { display: block; padding: 10px 12px; background: var(--surface); border: 1.5px dashed var(--accent); border-radius: 12px; cursor: pointer; }
.try .q { display: block; font-weight: 600; }
.try .ans { display: block; margin-top: 4px; filter: blur(8px); }
.try.peek .ans { filter: none; }
.try .zh { font-size: 20px; }
.try .pyx { display: block; font-size: 15px; color: var(--muted); }
.try .hint { display: block; margin-top: 4px; font-size: 12px; color: var(--muted); }
.try.peek .hint { display: none; }
.subnav li a { color: var(--accent); }
.pattern { margin: 10px 0 0; padding: 10px 14px; font-weight: 600; background: var(--surface); border-left: 4px solid var(--accent); border-radius: 8px; }
.from { display: block; margin-top: 4px; font-size: 12px; color: var(--muted); font-style: italic; }
.src { margin: 14px 0 0; font-size: 12px; line-height: 1.5; color: var(--muted); }
.src span { font-weight: 700; }
.src a { color: var(--muted); }
.lesson h2 .tag { font-size: 12px; vertical-align: 3px; }
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


def page(title, crumbs, body, toggles=True, skip=""):
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
<nav class="crumbs">{crumbs}</nav>
{tg}
{body}
<p class="foot">Built from handwritten notes. Lesson tips and examples, and grammar examples, were written by Claude unless marked (your notes). Native-speaker friends have the last word on usage.</p>
</main>
<script>{TOGGLE_JS}</script>
</body>
</html>
"""


CRUMB_HOME = '<a href="../index.html">← All tools</a> · <a href="index.html">Lessons</a>'


def size_class(s):
    n = len(re.findall(r"[㄀-ㄯ一-鿿]", s or ""))
    return " l" if n >= 5 else " m" if n >= 4 else ""


def word_row(e):
    tw = e["t"] or e["s"]
    same = "" if e["t"] else " same"
    note = f'<span class="note">{esc(e["n"])}</span>' if e["n"] else ""
    if e["type"] == "sound":
        tw_cell = '<span class="c-tw"></span>'
    else:
        zy = f'<span class="zy">{esc(e["z"])}</span>' if e.get("z") else ""
        tw_cell = f'<span class="c-tw"><span class="zh{size_class(tw)}{same}" lang="zh-Hant-TW">{esc(tw)}</span>{zy}</span>'
    return (f'<div class="row peekable" tabindex="0">'
            f'<span><span class="zh{size_class(e["s"])}" lang="zh-Hans">{esc(e["s"])}</span><span class="py">{esc(e["p"])}</span></span>'
            f'{tw_cell}'
            f'<span><span class="mean">{esc(e["m"])}</span>{note}</span></div>')


SOURCE_LABEL = {"notes": "your notes", "hsk-list": "HSK 1 list", "added": "added by Claude"}


def parse_lesson(path, prefix):
    name = re.sub(r"^\d+-", "", path.stem)
    L = {"title": name, "summary": "", "related": [], "see": [], "file": f"{prefix}-{name}.html", "sections": [], "kind": prefix}
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


def example_card(who, parts):
    zh, py, en, src = parts[:4]
    src = f'<span class="from">{esc(src)}</span>' if src else ""
    if who:
        return (f'<div class="dlg peekable" tabindex="0"><span class="who" aria-label="Speaker {esc(who)}">{esc(who)}</span>'
                f'<span><span class="zh" lang="zh-Hans">{esc(zh)}</span><span class="py">{esc(py)}</span>'
                f'<span class="mean">{esc(en)}</span>{src}</span></div>')
    return (f'<div class="phrase peekable" tabindex="0"><span class="zh" lang="zh-Hans">{esc(zh)}</span>'
            f'<span class="py">{esc(py)}</span><span class="mean">{esc(en)}</span>{src}</div>')


def try_card(prompt, zh, py):
    return (f'<div class="try peekable" tabindex="0" aria-label="Practice: {esc(prompt)}. Tap to show the answer.">'
            f'<span class="q">{esc(prompt)}</span>'
            f'<span class="ans"><span class="zh" lang="zh-Hans">{esc(zh)}</span><span class="pyx">{esc(py)}</span></span>'
            f'<span class="hint">Say it, then tap to check</span></div>')


def sources_line(s, words):
    """The small 'where this comes from' note at the end of each section."""
    bits = []
    if words:
        counts = {}
        for w in words:
            counts[w["src"]] = counts.get(w["src"], 0) + 1
        bits.append("Words: " + ", ".join(f"{SOURCE_LABEL.get(k, k)} ({n})" for k, n in counts.items()))
    for label, url in s["sources"]:
        bits.append(f'<a href="{esc(url)}" target="_blank" rel="noopener">{esc(label)}</a>' if url else esc(label))
    if s["tips"] or s["examples"] or s["try"]:
        bits.append("Wording and unmarked examples: Claude")
    return f'<p class="src"><span>Sources:</span> {" · ".join(bits)}</p>' if bits else ""


def render_lesson(L, word_by_s):
    grammar = L["kind"] == "grammar"
    out = [f"<h1>{esc(L['title'])}</h1>"]
    if L["summary"]:
        out.append(f'<p class="lead">{esc(L["summary"])}</p>')
    if L["see"]:
        links = " · ".join(f'<a href="{esc(u)}" target="_blank" rel="noopener">{esc(l)}</a>' if u else esc(l) for l, u in L["see"])
        out.append(f'<p class="src"><span>Also covered in Yoyo Chinese:</span> {links}</p>')
    out.append('<ul class="subnav">' + "".join(
        f'<li><a href="#{slug(s["title"])}">{esc(s["title"])}</a></li>' for s in L["sections"]) + "</ul>")
    for s in L["sections"]:
        tag = f' <span class="tag">{esc(s["tag"])}</span>' if s["tag"] else ""
        out.append(f'<section class="lesson" id="{slug(s["title"])}"><h2>{esc(s["title"])}{tag}</h2>')
        if s["pattern"]:
            out.append(f'<p class="pattern">{inline(s["pattern"])}</p>')
        out += [f"<p>{inline(p)}</p>" for p in s["intro"]]
        words = [word_by_s[w] for w in s["words"]]
        if words:
            out.append('<h3>Words</h3><div class="list">' + "".join(word_row(w) for w in words) + "</div>")
        if s["tips"]:
            head = "How it works" if grammar else "How to use them"
            out.append(f'<div class="tips"><h3>{head}</h3><ul>' + "".join(f"<li>{inline(t)}</li>" for t in s["tips"]) + "</ul></div>")
        if s["examples"]:
            out.append('<h3>Examples</h3><div class="list">' + "".join(example_card(w, p) for w, p in s["examples"]) + "</div>")
        if s["try"]:
            out.append('<h3>Try it</h3><div class="list">' + "".join(try_card(*t) for t in s["try"]) + "</div>")
        out.append(sources_line(s, words))
        out.append("</section>")
    return "\n".join(out)


def load(folder, prefix):
    files = sorted(folder.glob("*.md"), key=lambda p: int(re.match(r"\d+", p.stem).group()))
    return [parse_lesson(p, prefix) for p in files]


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

    def related_cards(names):
        cards = []
        for n in names:
            key = n[9:] if n.startswith("Grammar: ") else n
            if key not in by_title:
                raise SystemExit(f"Unknown related link: {n}")
            L = by_title[key]
            kind = "Grammar" if L["kind"] == "grammar" else "Lesson"
            cards.append(f'<a class="card" href="{L["file"]}"><b>{kind}: {esc(L["title"])}</b><span>{esc(L["summary"])}</span></a>')
        return '<h2>Related</h2><div class="cards">' + "".join(cards) + "</div>" if cards else ""

    for group, label in ((lessons, "lesson"), (grammar, "grammar lesson")):
        for i, L in enumerate(group):
            prev = f'<a href="{group[i-1]["file"]}">← {esc(group[i-1]["title"])}</a>' if i else "<span></span>"
            nxt = f'<a href="{group[i+1]["file"]}">{esc(group[i+1]["title"])} →</a>' if i + 1 < len(group) else "<span></span>"
            body = render_lesson(L, word_by_s) + related_cards(L["related"]) + f'<nav class="pager">{prev}{nxt}</nav>'
            has_words = any(sec["words"] for sec in L["sections"])
            (OUT / L["file"]).write_text(page(f"{L['title']} · Mandarin {label}", CRUMB_HOME, body,
                                              skip="" if has_words else "ztw"), encoding="utf8")

    def cards(group):
        return "".join(f'<a class="card" href="{L["file"]}"><b>{i}. {esc(L["title"])}</b><span>{esc(L["summary"])}</span></a>'
                       for i, L in enumerate(group, 1))
    body = ("<h1>Lessons</h1><p class=\"lead\">Short lessons built from your notes: words or patterns, how they work, "
            "examples, and a quick practice. Each section says where its information comes from. "
            "To look a word up, use <a href=\"../tools/mandarin-notes.html\">My Mandarin notes</a>.</p>"
            f"<h2>Vocabulary</h2><div class=\"cards\">{cards(lessons)}</div>"
            f"<h2>Grammar</h2><p class=\"lead\">Checked against the <a href=\"https://resources.allsetlearning.com/chinese/grammar/Main_Page\" target=\"_blank\" rel=\"noopener\">AllSet Chinese Grammar Wiki</a>. Tags show AllSet's level.</p>"
            f"<div class=\"cards\">{cards(grammar)}</div>")
    (OUT / "index.html").write_text(page("Mandarin lessons", '<a href="../index.html">← All tools</a>', body, toggles=False), encoding="utf8")
    print(f"Wrote {len(lessons)} vocabulary lessons, {len(grammar)} grammar lessons and topics/index.html")
    if unused:
        print(f"Not in any lesson yet ({len(unused)}): {' '.join(unused)}")


if __name__ == "__main__":
    main()
