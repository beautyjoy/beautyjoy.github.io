#!/usr/bin/env python3
"""Fetch candidate publications for the BJC Research page.

Two keyless, no-signup scholarly sources are supported:

* **Crossref** (default) -- the authoritative DOI registry. Its ``query.title``
  search is precise and every hit comes with a DOI, which is exactly what we want
  for *verifying* publications. This is the default because it is reliable and
  double-serves the "verify papers" goal.
* **DBLP** (``--source dblp``) -- great CS-venue coverage, but its search API may
  be unreachable behind some networks/proxies.

Why not Google Scholar / ACM DL? Scholar has no API and blocks scraping; ACM DL
needs authentication for bulk metadata.

Results are normalized to the ``_data/publications.yml`` schema, run through a
light **relevance filter** (BJC search terms are broad enough to pull in
unrelated "beauty/joy" hits), and **deduped against what is already on the site**
(by DOI, then title). The output is a ``candidates.json`` file that
``review_publications.py`` reads.

Examples
--------
    # Crossref (default), built-in BJC query set:
    python3 tools/fetch_publications.py

    # Your own queries:
    python3 tools/fetch_publications.py --query "beauty and joy of computing"

    # DBLP instead of Crossref:
    python3 tools/fetch_publications.py --source dblp

    # Offline: re-parse a saved API response (Crossref or DBLP JSON):
    python3 tools/fetch_publications.py --source dblp --from-file dblp.json
"""

import argparse
import json
import os
import re
import sys
import unicodedata
import urllib.parse
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pubs_common import (  # noqa: E402
    REPO_ROOT,
    dedupe_key,
    existing_keys,
    is_duplicate,
    load_excluded,
    load_existing,
    normalize_doi,
    normalize_title,
)

DBLP_ENDPOINT = "https://dblp.org/search/publ/api"
CROSSREF_ENDPOINT = "https://api.crossref.org/works"
DEFAULT_OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "candidates.json")
# Crossref asks for a mailto in the User-Agent for its faster "polite" pool.
USER_AGENT = "BJC-publications-tool/1.0 (https://bjc.berkeley.edu; mailto:contact@bjc.berkeley.edu)"

# DBLP publication "type" -> our category vocabulary. Unknown types default to
# "paper"; the reviewer can re-classify posters/talks/workshops interactively.
DBLP_TYPE_TO_CATEGORY = {
    "Conference and Workshop Papers": "paper",
    "Journal Articles": "paper",
    "Informal and Other Publications": "paper",
    "Books and Theses": "dissertation",
    "Editorship": "workshop",
    "Parts in Books or Collections": "paper",
}

# Crossref "type" -> our category vocabulary.
CROSSREF_TYPE_TO_CATEGORY = {
    "journal-article": "paper",
    "proceedings-article": "paper",
    "book-chapter": "paper",
    "posted-content": "paper",
    "dissertation": "dissertation",
    "report": "paper",
}

# Default queries tuned for BJC-related work. Override with --query on the CLI.
DEFAULT_QUERIES = [
    "beauty and joy of computing",
    "snap block-based programming language",
    "AP computer science principles beauty joy computing",
]

# --- Relevance filtering -----------------------------------------------------
# BJC searches are broad ("beauty", "joy", "snap", "block-based") and pull in
# unrelated hits. We keep a candidate only if it looks like BJC-team work.
BJC_AUTHOR_FAMILIES = {
    "garcia", "harvey", "barnes", "ball", "mock", "mark", "klein", "milliken",
    "catete", "cateté", "price", "goldenberg", "hill", "chipman", "subramaniam",
    "segars", "monig", "mönig", "zhi", "dong", "lytle", "cuoco", "fries",
    "paley", "biga", "isvik", "dastur",
}
# Topic terms that, together with a known author, signal BJC-relevant work.
BJC_TOPIC_TERMS = [
    "beauty and joy", "snap", "block-based", "blocks", "computer science principles",
    "computing principles", "csp", "bjc", "computational thinking", "novice programming",
]


# Windows-1252 punctuation that shows up mis-encoded in some Crossref records.
_CP1252_FIXES = {
    "\x91": "'", "\x92": "'", "\x93": '"', "\x94": '"',
    "\x96": "–", "\x97": "—", "\x85": "…",
}
_TITLE_QUALIFIER_RE = re.compile(
    r"\s*\((abstract only|abstract|extended abstract|keynote|poster|panel)\)\s*$",
    re.IGNORECASE,
)


def clean_title(title):
    """Fix mis-encoded punctuation and drop trailing '(Abstract Only)' qualifiers."""
    if not title:
        return ""
    for bad, good in _CP1252_FIXES.items():
        title = title.replace(bad, good)
    title = _TITLE_QUALIFIER_RE.sub("", title)
    return title.rstrip(". ").strip()


def _norm(text):
    # Fold accents so "Mönig"/"Cateté" match the ASCII author families.
    folded = unicodedata.normalize("NFKD", text or "")
    folded = "".join(c for c in folded if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9]+", " ", folded.lower()).strip()


# Venue words that mark a computing publication -- used to keep author-only
# matches (2+ BJC surnames, no topic keyword) from admitting namesake noise in
# math/chemistry/history journals.
COMPUTING_VENUE_TERMS = [
    "comput", "sigcse", "informatics", "programming", "snap", "blocks",
    "iticse", "icer", "respect", "human factors", "artificial intel",
    "visual language", "learning sciences", "software", "technology",
]
# Titles that are proceedings cruft, not real publications.
JUNK_TITLE_RE = re.compile(
    r"^(session details|front matter|back matter|table of contents|"
    r"proceedings of|sigcse.*(preview|report)|.*symposium.*(preview|report))",
    re.IGNORECASE,
)


def count_bjc_authors(candidate):
    """How many known BJC-team author *families* appear on this candidate.

    Prefers the structured family names Crossref provides (``_families``) so a
    given name like "Mark Helman" or "Dan Schiller" does not false-match the
    June *Mark* / *Dan* families. Falls back to a substring scan otherwise.
    """
    families = candidate.get("_families")
    if families:
        return sum(1 for fam in families if fam in BJC_AUTHOR_FAMILIES)
    authors = _norm(candidate.get("authors"))
    return sum(1 for fam in BJC_AUTHOR_FAMILIES if fam in authors)


def is_relevant(candidate):
    """Heuristic: keep obvious BJC work, drop unrelated 'beauty/joy/snap' hits.

    Kept if any of:
      * the exact course name is in the title (strong signal on its own), or
      * a known BJC author *and* a computing topic term (drops unrelated
        "beauty and joy" papers -- Latin prose, pharmacology, ...), or
      * two or more known BJC authors *and* a computing venue (author-search
        safety net for BJC papers whose titles lack an obvious keyword, without
        admitting namesake papers in non-computing journals).
    Proceedings cruft (session details, front matter, ...) is always dropped.
    """
    title = _norm(candidate.get("title"))
    if JUNK_TITLE_RE.match((candidate.get("title") or "").strip()):
        return False
    if "beauty and joy of computing" in title:
        return True
    n_authors = count_bjc_authors(candidate)
    has_topic = any(term in title for term in BJC_TOPIC_TERMS)
    if n_authors >= 1 and has_topic:
        return True
    venue = _norm(candidate.get("journal"))
    is_computing_venue = any(term in venue for term in COMPUTING_VENUE_TERMS)
    return n_authors >= 2 and is_computing_venue


# --- HTTP --------------------------------------------------------------------
def _http_get_json(url):
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def _as_list(value):
    if value is None:
        return []
    return value if isinstance(value, list) else [value]


# --- DBLP --------------------------------------------------------------------
def dblp_search(query, limit):
    params = urllib.parse.urlencode({"q": query, "format": "json", "h": limit})
    return _http_get_json("{0}?{1}".format(DBLP_ENDPOINT, params))


def _clean_dblp_author(author):
    """DBLP authors are {'text': 'Name 0001', ...}; strip the disambig number."""
    name = author.get("text", "") if isinstance(author, dict) else str(author)
    parts = name.rsplit(" ", 1)
    if len(parts) == 2 and parts[1].isdigit():
        name = parts[0]
    return name.strip()


def parse_dblp(payload):
    hits = _as_list(payload.get("result", {}).get("hits", {}).get("hit"))
    candidates = []
    for hit in hits:
        info = hit.get("info", {})
        authors = _as_list(info.get("authors", {}).get("author"))
        names = [n for n in (_clean_dblp_author(a) for a in authors) if n]
        venue = info.get("venue")
        if isinstance(venue, list):
            venue = ", ".join(str(v) for v in venue)
        year = info.get("year")
        candidates.append({
            "title": clean_title(info.get("title")),
            "filename": None,
            "authors": ", ".join(names),
            "doi": info.get("doi"),
            "category": DBLP_TYPE_TO_CATEGORY.get(info.get("type"), "paper"),
            "year": int(year) if year and str(year).isdigit() else year,
            "journal": venue,
            "abstract": None,  # DBLP does not provide abstracts
            "external_link": info.get("ee") or info.get("url"),
            "_source": "dblp",
        })
    return candidates


# --- Crossref ----------------------------------------------------------------
CROSSREF_SELECT = "title,author,issued,container-title,DOI,URL,type,abstract"


def crossref_search(query, limit):
    params = urllib.parse.urlencode({
        "query.title": query, "rows": limit, "select": CROSSREF_SELECT,
    })
    return _http_get_json("{0}?{1}".format(CROSSREF_ENDPOINT, params))


def crossref_author_search(author, limit):
    params = urllib.parse.urlencode({
        "query.author": author, "rows": limit, "select": CROSSREF_SELECT,
    })
    return _http_get_json("{0}?{1}".format(CROSSREF_ENDPOINT, params))


def _clean_abstract(raw):
    """Crossref abstracts are JATS XML; strip tags to plain text."""
    if not raw:
        return None
    text = re.sub(r"<[^>]+>", " ", raw)
    text = re.sub(r"\s+", " ", text).strip()
    # Drop a leading "Abstract" label if present.
    return re.sub(r"^abstract[:\s]+", "", text, flags=re.IGNORECASE) or None


def parse_crossref(payload):
    items = payload.get("message", {}).get("items", [])
    candidates = []
    for item in items:
        authors = item.get("author") or []
        names = [
            " ".join(p for p in (a.get("given"), a.get("family")) if p).strip()
            for a in authors
        ]
        names = [n for n in names if n]
        families = [_norm(a.get("family")) for a in authors if a.get("family")]
        title = (item.get("title") or [""])[0]
        venue = (item.get("container-title") or [""])
        venue = venue[0] if venue else ""
        parts = (item.get("issued", {}).get("date-parts") or [[None]])[0]
        year = parts[0] if parts else None
        candidates.append({
            "title": clean_title(title),
            "filename": None,
            "authors": ", ".join(names),
            "doi": item.get("DOI"),
            "category": CROSSREF_TYPE_TO_CATEGORY.get(item.get("type"), "paper"),
            "year": int(year) if isinstance(year, int) else year,
            "journal": venue,
            "abstract": _clean_abstract(item.get("abstract")),
            "external_link": item.get("URL") or (
                "https://doi.org/" + item["DOI"] if item.get("DOI") else None),
            "_source": "crossref",
            "_families": families,
        })
    return candidates


SOURCES = {
    "crossref": (crossref_search, parse_crossref),
    "dblp": (dblp_search, parse_dblp),
}


# --- Dedupe ------------------------------------------------------------------
def dedupe_candidates(candidates, existing):
    """Drop candidates already on the site and collapse internal duplicates."""
    keys = existing_keys(existing)
    seen = set()
    fresh = []
    skipped = 0
    for cand in candidates:
        key = dedupe_key(cand)
        title_key = normalize_title(cand.get("title"))
        if not title_key:
            continue
        if is_duplicate(cand, keys) or key in seen or title_key in seen:
            skipped += 1
            continue
        seen.add(key)
        seen.add(title_key)
        fresh.append(cand)
    return fresh, skipped


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--source", choices=sorted(SOURCES), default="crossref",
                        help="Where to fetch from (default: crossref).")
    parser.add_argument("--query", action="append", default=[],
                        help="Title search query (repeatable). Defaults to a BJC-tuned set.")
    parser.add_argument("--author", action="append", default=[],
                        help="Author-name search (repeatable). Crossref only.")
    parser.add_argument("--from-file", action="append", default=[], metavar="PATH",
                        help="Parse a saved API response for --source instead of "
                             "hitting the network (repeatable).")
    parser.add_argument("--limit", type=int, default=50,
                        help="Max hits to request per query (default: 50).")
    parser.add_argument("--out", default=DEFAULT_OUT,
                        help="Where to write candidates.json.")
    parser.add_argument("--no-filter", action="store_true",
                        help="Skip the BJC relevance filter (keep every hit).")
    parser.add_argument("--keep-duplicates", action="store_true",
                        help="Do not drop candidates already in publications.yml.")
    args = parser.parse_args(argv)

    search_fn, parse_fn = SOURCES[args.source]

    payloads = []
    for path in args.from_file:
        with open(path, "r", encoding="utf-8") as handle:
            payloads.append(json.load(handle))

    if not args.from_file:
        # Use the default title query set only when no explicit query/author given.
        queries = args.query or ([] if args.author else DEFAULT_QUERIES)
        for query in queries:
            print("Querying {0} title: {1!r}".format(args.source, query), file=sys.stderr)
            try:
                payloads.append(search_fn(query, args.limit))
            except Exception as exc:
                print("  ! Could not reach {0} ({1}). If you are behind a network "
                      "policy, save the API response and re-run with --from-file."
                      .format(args.source, exc), file=sys.stderr)

        if args.author and args.source != "crossref":
            print("  ! --author is only supported for --source crossref; ignoring.",
                  file=sys.stderr)
        for author in (args.author if args.source == "crossref" else []):
            print("Querying crossref author: {0!r}".format(author), file=sys.stderr)
            try:
                payloads.append(crossref_author_search(author, max(args.limit, 80)))
            except Exception as exc:
                print("  ! Could not reach crossref ({0}).".format(exc), file=sys.stderr)

    candidates = []
    for payload in payloads:
        candidates.extend(parse_fn(payload))

    filtered_out = 0
    if not args.no_filter:
        kept = [c for c in candidates if is_relevant(c)]
        filtered_out = len(candidates) - len(kept)
        candidates = kept

    # Dedupe against both what is published *and* what was reviewed-and-excluded,
    # so a previously-rejected paper never comes back to be re-reviewed.
    existing = load_existing() + load_excluded()
    if args.keep_duplicates:
        fresh, skipped = candidates, 0
    else:
        fresh, skipped = dedupe_candidates(candidates, existing)

    fresh.sort(key=lambda c: (c.get("year") or 0), reverse=True)

    with open(args.out, "w", encoding="utf-8") as handle:
        json.dump(fresh, handle, indent=2, ensure_ascii=False)

    print("Parsed {0} record(s); dropped {1} as off-topic; {2} new candidate(s) "
          "after deduping ({3} already on the site or duplicated)."
          .format(len(candidates) + filtered_out, filtered_out, len(fresh), skipped),
          file=sys.stderr)
    print("Wrote {0}".format(os.path.relpath(args.out, REPO_ROOT)), file=sys.stderr)
    print("Next: python3 tools/review_publications.py", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
