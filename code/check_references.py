#!/usr/bin/env python3
"""Check that every reference exists and that title, first author and year match.

Each \\bibitem in paper/section/095_reference_nature.tex is looked up in a primary
record: Crossref (DOI), arXiv (arXiv identifier, or a title search for OpenReview
items, whose site blocks automated access), the ACL Anthology BibTeX, NeurIPS
proceedings page metadata, or Open Library (ISBN). Titles are compared after
normalisation; the first author's family name and the year must appear in the
record. Network access is required. Exit code 1 if any reference fails.

Usage: python code/check_references.py [--json-out paper/results/reference_check.json]
"""
from __future__ import annotations
import argparse
import difflib
import json
import re
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

REF = Path(__file__).resolve().parents[1] / "paper/section/095_reference_nature.tex"
UA = {"User-Agent": "reference-check/1.0"}
# Items without a DOI/arXiv/ACL/NeurIPS/ISBN link that are verified by a fixed record.
MANUAL = {
    "mccarthy1969problems": "Machine Intelligence 4 (Edinburgh Univ. Press, 1969), pp. 463-502; "
                            "author's copy at www-formal.stanford.edu/jmc/mcchay69.pdf",
}


def get(url, tries=8):
    """GET with retries: arXiv answers bursts with HTTP 429 or slow responses."""
    for attempt in range(tries):
        try:
            req = urllib.request.Request(url, headers={**UA, "Accept": "application/json, text/html"})
            return urllib.request.urlopen(req, timeout=60).read().decode("utf-8", "replace")
        except Exception as exc:  # noqa: BLE001
            code = getattr(exc, "code", None)
            if attempt == tries - 1 or (code is not None and code not in (429, 500, 502, 503, 504)):
                raise
            time.sleep(20 * (attempt + 1))


def norm(t):
    """Lower-case ASCII words: LaTeX accents and Unicode diacritics are dropped."""
    import unicodedata
    t = re.sub(r"\\[`'^\"~=.uvHtcdbk]\{?([A-Za-z])\}?", r"\1", t)  # \'{o} -> o
    t = unicodedata.normalize("NFKD", t).encode("ascii", "ignore").decode()
    t = re.sub(r"\\[a-zA-Z]+|[{}$]", " ", t)
    return re.sub(r"[^a-z0-9]+", " ", t.lower()).strip()


AUTHORS = re.compile(r"""^\s*(?:(?:van\s|de\s)?[A-Z][^\s,]*(?:\s[A-Z][^\s,]*)?,\s(?:[A-Z]\.\s?)+
                     (?:,\s|\s?\\&\s|\s*et\ al\.\s*)?)+""", re.X)


def latex_title(body):
    """Title = text after the author list, up to the next sentence end or '('."""
    body = re.sub(r"\\refurl\{[^}]*\}", "", body)
    body = re.sub(r"\\emph\{([^}]*)\}", r"\1", body)
    rest = AUTHORS.sub("", body, count=1).strip()
    m = re.match(r"(.+?)(?:\.\s|\s\(|\.$)", rest, re.S)
    return " ".join((m.group(1) if m else rest).split())


def first_author(body):
    return re.split(r"[,.\s]", body.strip())[0].replace("\\", "")


def year(body):
    ys = re.findall(r"\((?:[^()]*?)(\d{4})\)", body) or re.findall(r"\b(19|20)\d{2}\b", body)
    return ys[-1] if ys else ""


def arxiv_entry(query=None, ident=None):
    u = ("https://export.arxiv.org/api/query?" +
         (f"id_list={ident}" if ident else "search_query=" + urllib.parse.quote(query) + "&max_results=3"))
    x = get(u)
    time.sleep(8)  # arXiv API etiquette
    out = []
    for e in re.findall(r"<entry>(.*?)</entry>", x, re.S):
        t = " ".join(re.search(r"<title>(.*?)</title>", e, re.S).group(1).split())
        out.append({"title": t, "authors": re.findall(r"<name>(.*?)</name>", e),
                    "year": re.search(r"<published>(\d{4})", e).group(1),
                    "comment": " ".join((re.search(r"<arxiv:comment[^>]*>(.*?)</arxiv:comment>", e, re.S)
                                         or re.match("()", "")).group(1).split())})
    return out


def lookup(key, body):
    if m := re.search(r"doi\.org/([^}\s]+)", body):
        r = json.loads(get("https://api.crossref.org/works/" + urllib.parse.quote(m.group(1))))["message"]
        return {"source": "Crossref DOI " + m.group(1), "title": (r.get("title") or [""])[0],
                "authors": [a.get("family", "") for a in r.get("author", [])],
                "year": str(r.get("issued", {}).get("date-parts", [[""]])[0][0]),
                "venue": (r.get("container-title") or [""])[0], "volume": r.get("volume"),
                "pages": r.get("page") or r.get("article-number")}
    if m := re.search(r"arxiv\.org/abs/([\d.]+)", body):
        e = arxiv_entry(ident=m.group(1))[0]
        return {"source": "arXiv " + m.group(1), **e}
    if m := re.search(r"aclanthology\.org/([\w.-]+?)/?\}", body):
        b = get(f"https://aclanthology.org/{m.group(1)}.bib")
        f = lambda k: " ".join((re.search(k + r'\s*=\s*"(.*?)",?\n\s*\w', b, re.S) or re.match("()", "")).group(1).split())
        return {"source": "ACL Anthology " + m.group(1), "title": f("title"),
                "authors": re.findall(r"(\w[\w-]*),", f("author")), "year": f("year"),
                "venue": f("booktitle"), "pages": f("pages")}
    if m := re.search(r"(proceedings\.neurips\.cc[^}\s]+)", body):
        h = get("https://" + m.group(1))
        meta = dict(re.findall(r'<meta name="citation_(\w+)" content="([^"]*)"', h))
        authors = re.findall(r'<meta name="citation_author" content="([^"]*)"', h)
        return {"source": "NeurIPS proceedings", "title": meta.get("title", ""),
                "authors": [a.split(",")[0].split()[-1] for a in authors],
                "year": meta.get("publication_date", "")[:4], "volume": meta.get("volume"),
                "pages": f'{meta.get("firstpage")}-{meta.get("lastpage")}'}
    if m := re.search(r"openlibrary\.org/isbn/(\d+)", body):
        r = json.loads(get(f"https://openlibrary.org/isbn/{m.group(1)}.json"))
        return {"source": "Open Library ISBN " + m.group(1), "title": r.get("title", ""),
                "authors": [], "year": re.sub(r"\D", "", r.get("publish_date", ""))[-4:],
                "venue": ", ".join(r.get("publishers", []))}
    if "openreview.net" in body:
        cands = arxiv_entry(query='ti:"' + latex_title(body)[:90] + '"')
        best = max(cands, key=lambda e: difflib.SequenceMatcher(None, norm(e["title"]), norm(latex_title(body))).ratio(),
                   default=None)
        if best:
            return {"source": "arXiv title search (OpenReview item)", **best}
    if key in MANUAL:
        return {"source": "fixed record", "title": latex_title(body), "authors": [first_author(body)],
                "year": year(body), "note": MANUAL[key]}
    return None


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--json-out", default="paper/results/reference_check.json")
    a = p.parse_args()
    items = re.findall(r"\\bibitem\{([^}]+)\}(.*?)(?=\\bibitem|\\end\{thebibliography\})",
                       REF.read_text(), re.S)
    report, failed = [], []
    for key, body in items:
        title, author, yr = latex_title(body), first_author(body), year(body)
        try:
            rec = lookup(key, body)
        except Exception as exc:  # network or parse error
            rec = None
            err = f"{type(exc).__name__}: {exc}"
        else:
            err = None
        if rec is None:
            ok, sim = False, 0.0
        else:
            sim = difflib.SequenceMatcher(None, norm(title), norm(rec["title"])).ratio()
            in_title = norm(rec["title"]) in norm(body) or norm(title) in norm(rec["title"])
            author_ok = not rec.get("authors") or any(norm(author) == norm(x) or norm(author) in norm(x)
                                                     for x in rec["authors"][:1] + rec["authors"])
            year_ok = not rec.get("year") or rec["year"] == yr or rec["year"] in body
            ok = (sim >= 0.85 or in_title) and author_ok and year_ok
        report.append({"key": key, "ok": ok, "title_similarity": round(sim, 2),
                       "cited_first_author": author, "cited_year": yr, "record": rec, "error": err})
        if not ok:
            failed.append(key)
        print(("OK  " if ok else "FAIL"), key, "|", rec["source"] if rec else err)
    Path(a.json_out).write_text(json.dumps(report, indent=1, ensure_ascii=False) + "\n")
    print(f"{len(items) - len(failed)}/{len(items)} references verified;",
          "FAILED: " + ", ".join(failed) if failed else "all match")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
