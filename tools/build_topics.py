#!/usr/bin/env python3
"""Build the topic pages in topics/ from vocab.csv, grammar.md and guides/*.md.

Normally run through tools/build_notes.py, which calls this at the end:

    python3 tools/build_notes.py

Pages built:
  topics/index.html            list of all topic pages
  topics/<group>.html          one per situation group (GROUPS in build_notes.py)
  topics/grammar-<n>.html      one per section of grammar.md
  topics/guide-<name>.html     one per study guide in guides/

Study guide format (guides/<name>.md):
  # Title
  related: People, Conversation, Grammar: <section title>   (optional; links)
  summary: one line for the index                           (optional)
  Paragraph text, ## Section headings, and bullets:
  - 中文 | pinyin | English | optional note     a phrase
  - A: 中文 | pinyin | English                  a line of dialogue (speaker before the colon)
  - Plain text                                 an ordinary bullet; **bold** and `code` work
"""
import html
import re
from pathlib import Path

import build_notes as bn

ROOT = bn.ROOT
OUT = ROOT / "topics"
GUIDES = ROOT / "guides"


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


def group_page(name):
    return slug(name) + ".html"


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
<p class="foot">Built from handwritten notes. Grammar examples and study guides were written by Claude unless marked (your notes). Native-speaker friends have the last word on usage.</p>
</main>
<script>{TOGGLE_JS}</script>
</body>
</html>
"""


CRUMB_HOME = '<a href="../index.html">← All tools</a> · <a href="index.html">Topics</a>'


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


def pattern_block(g):
    tag = f' <span class="tag">{esc(g["status"])}</span>' if g.get("status") else ""
    ex = f'<p class="ex">{esc(g["n"])}</p>' if g["n"] else ""
    extra = "".join(f"<li>{esc(x)}</li>" for x in g.get("extra", []))
    extra = f"<ul>{extra}</ul>" if extra else ""
    return f'<div class="pat"><h3>{esc(g["s"])}{tag}</h3><p>{esc(g["m"])}</p>{ex}{extra}</div>'


def grammar_sections(entries):
    secs = []
    for e in entries:
        if e["kind"] != "grammar":
            continue
        name = e["topic"].replace("Grammar: ", "")
        if not secs or secs[-1]["name"] != name:
            secs.append({"name": name, "patterns": [], "uses": e["uses"]})
        secs[-1]["patterns"].append(e)
    for i, s in enumerate(secs, 1):
        s["file"] = f"grammar-{i}-{slug(s['name'])}.html"
    return secs


def parse_guide(path):
    lines = path.read_text(encoding="utf8").splitlines()
    g = {"title": path.stem, "related": [], "summary": "", "file": f"guide-{path.stem}.html", "blocks": []}
    for line in lines:
        st = line.strip()
        if not st:
            continue
        if st.startswith("# "):
            g["title"] = st[2:].strip()
        elif st.startswith("related:"):
            g["related"] = [x.strip() for x in st[8:].split(",") if x.strip()]
        elif st.startswith("summary:"):
            g["summary"] = st[8:].strip()
        elif st.startswith("## "):
            g["blocks"].append(("h2", st[3:].strip()))
        elif st.startswith("- "):
            body = st[2:]
            m = re.match(r"^([A-Za-z][\w ]{0,11}):\s*(.+)$", body)
            if m and "|" in m.group(2):
                g["blocks"].append(("dlg", m.group(1), [x.strip() for x in m.group(2).split("|")]))
            elif "|" in body:
                g["blocks"].append(("phrase", [x.strip() for x in body.split("|")]))
            else:
                g["blocks"].append(("li", body))
        else:
            g["blocks"].append(("p", st))
    return g


def render_guide(g):
    out, in_list, in_ul = [], False, False

    def close():
        nonlocal in_list, in_ul
        if in_list:
            out.append("</div>")
            in_list = False
        if in_ul:
            out.append("</ul>")
            in_ul = False

    for b in g["blocks"]:
        kind = b[0]
        if kind in ("phrase", "dlg"):
            if in_ul:
                out.append("</ul>"); in_ul = False
            if not in_list:
                out.append('<div class="list">'); in_list = True
            if kind == "phrase":
                zh, py, en, *rest = b[1] + ["", "", ""]
                note = f'<span class="note">{inline(rest[0])}</span>' if rest and rest[0] else ""
                out.append(f'<div class="phrase peekable" tabindex="0"><span class="zh" lang="zh-Hans">{esc(zh)}</span>'
                           f'<span class="py">{esc(py)}</span><span class="mean">{esc(en)}</span>{note}</div>')
            else:
                who, (zh, py, en, *_rest) = b[1], b[2] + ["", "", ""]
                out.append(f'<div class="dlg peekable" tabindex="0"><span class="who" aria-label="Speaker {esc(who)}">{esc(who)}</span>'
                           f'<span><span class="zh" lang="zh-Hans">{esc(zh)}</span><span class="py">{esc(py)}</span>'
                           f'<span class="mean">{esc(en)}</span></span></div>')
        elif kind == "li":
            if in_list:
                out.append("</div>"); in_list = False
            if not in_ul:
                out.append("<ul>"); in_ul = True
            out.append(f"<li>{inline(b[1])}</li>")
        else:
            close()
            out.append(f"<h2>{inline(b[1])}</h2>" if kind == "h2" else f"<p>{inline(b[1])}</p>")
    close()
    return "\n".join(out)


def main():
    entries = bn.vocab_entries() + bn.grammar_entries()
    words = [e for e in entries if e["kind"] == "word"]
    secs = grammar_sections(entries)
    sec_by_name = {s["name"]: s for s in secs}
    guides = [parse_guide(p) for p in sorted(GUIDES.glob("*.md"))] if GUIDES.exists() else []
    OUT.mkdir(exist_ok=True)
    for old in OUT.glob("*.html"):
        old.unlink()

    def link_for(name):
        if name.startswith("Grammar: ") and name[9:] in sec_by_name:
            return sec_by_name[name[9:]]["file"], name[9:]
        if any(g == name for g, _ in bn.GROUPS):
            return group_page(name), name
        return None, name

    # Situation group pages
    group_counts = {}
    for gname, subs in bn.GROUPS:
        parts, nav = [], []
        seen = set()
        for u in subs:
            ws = [w for w in words if u in w["uses"]]
            if not ws:
                continue
            anchor = slug(u)
            nav.append(f'<li><a href="#{anchor}">{esc(u)}</a></li>')
            parts.append(f'<h2 id="{anchor}">{esc(u)}<small>{len(ws)}</small></h2><div class="list">'
                         + "".join(word_row(w) for w in ws) + "</div>")
            seen.update(id(w) for w in ws)
        group_counts[gname] = len(seen)
        related = [s for s in secs if set(s["uses"]) & set(subs)]
        rel_guides = [g for g in guides if gname in g["related"]]
        extra = ""
        if rel_guides or related:
            links = [f'<a class="card" href="{g["file"]}"><b>Study guide: {esc(g["title"])}</b><span>{esc(g["summary"])}</span></a>' for g in rel_guides]
            links += [f'<a class="card" href="{s["file"]}"><b>Grammar: {esc(s["name"])}</b><span>{len(s["patterns"])} patterns</span></a>' for s in related]
            extra = '<h2>Related</h2><div class="cards">' + "".join(links) + "</div>"
        body = (f"<h1>{esc(gname)}</h1><p class=\"lead\">{len(seen)} words and phrases, by situation. "
                f"Tap a row to peek at anything hidden.</p><ul class=\"subnav\">{''.join(nav)}</ul>"
                + "".join(parts) + extra)
        (OUT / group_page(gname)).write_text(page(f"{gname} · Mandarin topics", CRUMB_HOME, body), encoding="utf8")

    # Grammar section pages
    for i, s in enumerate(secs):
        prev = f'<a href="{secs[i-1]["file"]}">← {esc(secs[i-1]["name"])}</a>' if i else "<span></span>"
        nxt = f'<a href="{secs[i+1]["file"]}">{esc(secs[i+1]["name"])} →</a>' if i + 1 < len(secs) else "<span></span>"
        body = (f"<h1>{esc(s['name'])}</h1><p class=\"lead\">Grammar section {i+1} of {len(secs)}. "
                "Tags show the AllSet level.</p>"
                + "".join(pattern_block(g) for g in s["patterns"])
                + f'<nav class="pager">{prev}{nxt}</nav>')
        (OUT / s["file"]).write_text(page(f"{s['name']} · Mandarin grammar", CRUMB_HOME, body, toggles=False), encoding="utf8")

    # Study guides
    for g in guides:
        rel = []
        for name in g["related"]:
            f, label = link_for(name)
            if f:
                rel.append(f'<a class="card" href="{f}"><b>{esc(label)}</b><span>{"Grammar section" if f.startswith("grammar-") else "All words for this situation"}</span></a>')
        rel_html = '<h2>See also</h2><div class="cards">' + "".join(rel) + "</div>" if rel else ""
        body = f"<h1>{esc(g['title'])}</h1>" + render_guide(g) + rel_html
        (OUT / g["file"]).write_text(page(f"{g['title']} · Mandarin study guide", CRUMB_HOME, body, skip="ztw"), encoding="utf8")

    # Index
    gl = "".join(f'<a class="card" href="{g["file"]}"><b>{esc(g["title"])}</b><span>{esc(g["summary"])}</span></a>' for g in guides)
    sl = "".join(f'<a class="card" href="{group_page(n)}"><b>{esc(n)}</b><span>{group_counts[n]} words · {esc(", ".join(subs))}</span></a>'
                 for n, subs in bn.GROUPS)
    rl = "".join(f'<a class="card" href="{s["file"]}"><b>{i}. {esc(s["name"])}</b><span>{len(s["patterns"])} patterns</span></a>'
                 for i, s in enumerate(secs, 1))
    body = ("<h1>Topics</h1><p class=\"lead\">Read a topic top to bottom. To search or mix filters, use "
            "<a href=\"../tools/mandarin-notes.html\">My Mandarin notes</a>.</p>"
            + (f"<h2>Study guides</h2><div class=\"cards\">{gl}</div>" if gl else "")
            + f"<h2>Situations</h2><div class=\"cards\">{sl}</div>"
            + f"<h2>Grammar</h2><div class=\"cards\">{rl}</div>")
    (OUT / "index.html").write_text(page("Mandarin topics", '<a href="../index.html">← All tools</a>', body, toggles=False), encoding="utf8")
    print(f"Wrote {len(bn.GROUPS)} situation pages, {len(secs)} grammar pages, {len(guides)} guides and topics/index.html")


if __name__ == "__main__":
    main()
