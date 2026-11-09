# -*- coding: utf-8 -*-
"""Génère une version Markdown de chaque page (servie aux agents qui envoient Accept: text/markdown)."""
import os, re, glob, html
from html.parser import HTMLParser
from urllib.parse import urljoin
from common import ROOT, SITE

SKIP = {"script", "style", "svg", "noscript", "dialog", "button", "select", "option", "input", "textarea", "template", "nav", "footer", "form"}

class MD(HTMLParser):
    def __init__(self, base):
        super().__init__(convert_charrefs=True)
        self.base = base; self.out = []; self.in_main = False; self.skip = 0; self.stack = []
        self.list = []; self.href = None; self.link_start = None; self.cell = None; self.row = None; self.rows = []
        self.in_table = False; self.first_h1 = True; self.h1 = ""; self.cur_h = None; self.in_summary = False

    def w(self, s):
        if self.in_main and not self.skip:
            if self.cell is not None: self.cell.append(s)
            else: self.out.append(s)

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "main" and a.get("id") == "contenu": self.in_main = True; return
        if not self.in_main: return
        if self.skip or tag in SKIP or a.get("aria-hidden") == "true" or "visually-hidden" in a.get("class", "").split() and tag == "span" and False:
            self.skip += 1; self.stack.append(("skip", tag)); return
        self.stack.append(("ok", tag))
        if tag in ("h1", "h2", "h3", "h4"):
            self.cur_h = int(tag[1]); self.out.append("\n\n" + ("#" * self.cur_h) + " ")
        elif tag == "p": self.out.append("\n\n")
        elif tag in ("ul", "ol"): self.list.append([tag, 0]); self.out.append("\n")
        elif tag == "li":
            lv = self.list[-1] if self.list else ["ul", 0]; lv[1] += 1
            self.out.append("\n" + "  " * (len(self.list) - 1) + ("- " if lv[0] == "ul" else f"{lv[1]}. "))
        elif tag == "br": self.w("  \n")
        elif tag in ("strong", "b"): self.w("**")
        elif tag in ("em", "i"): self.w("*")
        elif tag == "a" and a.get("href") and not a["href"].startswith(("javascript:", "#")):
            self.href = urljoin(self.base, a["href"]); self.w("[")
        elif tag == "summary": self.in_summary = True; self.out.append("\n\n**")
        elif tag == "details": self.out.append("\n")
        elif tag == "dt": self.out.append("\n\n**")
        elif tag == "dd": self.out.append("\n")
        elif tag == "blockquote": self.out.append("\n\n> ")
        elif tag == "table": self.in_table = True; self.rows = []
        elif tag == "tr": self.row = []
        elif tag in ("td", "th"): self.cell = []

    def handle_endtag(self, tag):
        if tag == "main" and self.in_main and not self.stack: self.in_main = False; return
        if not self.in_main: return
        if not self.stack: return
        kind, t = self.stack.pop()
        if kind == "skip": self.skip -= 1; return
        if tag in ("h1", "h2", "h3", "h4"): self.out.append("\n")
        elif tag in ("span", "time", "small", "div", "figcaption", "label"): self.w(" ")
        elif tag in ("ul", "ol"):
            if self.list: self.list.pop()
            self.out.append("\n")
        elif tag in ("strong", "b"): self.w("**")
        elif tag in ("em", "i"): self.w("*")
        elif tag == "a" and self.href: self.w(f"]({self.href})"); self.href = None
        elif tag == "summary": self.in_summary = False; self.out.append("**\n")
        elif tag == "dt": self.out.append("**")
        elif tag in ("td", "th"):
            txt = re.sub(r"\s+", " ", "".join(self.cell or [])).strip().replace("|", "\\|")
            if self.row is not None: self.row.append((tag, txt))
            self.cell = None
        elif tag == "tr":
            if self.row: self.rows.append(self.row)
            self.row = None
        elif tag == "table":
            self.in_table = False
            if self.rows:
                width = max(len(r) for r in self.rows)
                lines = []
                for i, r in enumerate(self.rows):
                    cells = [c[1] for c in r] + [""] * (width - len(r))
                    lines.append("| " + " | ".join(cells) + " |")
                    if i == 0: lines.append("|" + " --- |" * width)
                self.out.append("\n\n" + "\n".join(lines) + "\n")
            self.rows = []

    def handle_data(self, data):
        if self.in_main and not self.skip:
            if self.cell is not None: self.cell.append(data)
            else: self.out.append(data)

def convert(path):
    t = open(path, encoding="utf-8").read()
    base = re.search(r'rel="canonical" href="([^"]*)"', t).group(1)
    title = html.unescape(re.search(r"<title>(.*?)</title>", t, re.S).group(1)).strip()
    desc = html.unescape((re.search(r'name="description" content="([^"]*)"', t) or [0, ""])[1] if re.search(r'name="description" content="([^"]*)"', t) else "")
    p = MD(base); p.feed(t)
    body = "".join(p.out)
    body = re.sub(r"[ \t]+\n", "\n", body)
    body = re.sub(r"[ \t]{2,}", " ", body)
    body = re.sub(r"\n{3,}", "\n\n", body).strip()
    m = re.match(r"# (.+)\n", body)
    h1 = m.group(1).strip() if m else title
    if m: body = body[m.end():].strip()
    head = f"# {h1}\n\n> {desc}\n\nSource : {base}\n\n" if desc else f"# {h1}\n\nSource : {base}\n\n"
    foot = ("\n\n---\n\nLOTIER Immobilier (SARL LOTIER), 40 rue Française, 1er étage, 34500 Béziers. Téléphone : 04 67 11 28 31. E-mail : contact@lotier-immobilier.com.\n"
            f"Pages utiles : [À propos]({SITE}/a-propos/) · [Contact]({SITE}/contact/) · [Honoraires]({SITE}/nos-honoraires/) · [Mentions légales]({SITE}/mentions-legales/) · [Plan du site]({SITE}/plan-du-site.html)\n")
    return head + body + foot

def md_path(f):
    return f[:-5] + ".md" if not f.endswith("index.html") else f[:-5] + ".md"

n = 0
for f in glob.glob(f"{ROOT}/**/*.html", recursive=True):
    rel = os.path.relpath(f, ROOT)
    if rel.startswith(("v2/", "audit-lotier/", "mise-en-ligne/", "node_modules/", "scripts/", ".claude/")) or rel in ("404.html",): continue
    if "name=\"robots\" content=\"noindex" in open(f, encoding="utf-8").read() and rel.startswith("mylotier"): continue
    out = f[:-5] + ".md"
    open(out, "w", encoding="utf-8").write(convert(f)); n += 1
print(n, "versions Markdown générées")
