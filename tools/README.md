# Publications tooling

Helpers for keeping the [Research page](../research.html) up to date. The page
renders `_data/publications.yml`; these scripts help you **pull** candidate
publications from scholarly sources, **review** them interactively, and **append**
the ones you keep — without ever clobbering the hand-written comments and section
headers in the data file.

```
fetch_publications.py  ->  candidates.json  ->  review_publications.py  ->  _data/publications.yml
                                                                       \->  excluded_publications.yml
```

Once a paper is either published or excluded, the tools never surface it again.

## Setup

```sh
pip install -r tools/requirements.txt   # just PyYAML
```

Run everything from the repo root.

## 1. Fetch candidates

```sh
# Crossref (default), built-in BJC query set:
python3 tools/fetch_publications.py

# Search by title and/or by author (both repeatable):
python3 tools/fetch_publications.py \
    --query "beauty and joy of computing" \
    --author "Michael Ball" --author "Dan Garcia"
```

This writes `tools/candidates.json` (git-ignored), already:

* **relevance-filtered** to BJC-team work (broad "beauty/joy/snap" hits in Latin
  prose, chemistry, etc. are dropped — see `is_relevant`),
* **deduped** against both `_data/publications.yml` *and*
  `excluded_publications.yml`, so nothing you've already decided comes back, and
* **sorted most-recent-first**.

### Sources

| Source | Flag | Notes |
|--------|------|-------|
| **Crossref** | *(default)* | The authoritative DOI registry — every hit is DOI-verified, which doubles as *paper verification*. Precise `query.title` / `query.author` search. |
| **DBLP** | `--source dblp` | Great CS-venue coverage, but its search API may be unreachable behind some networks/proxies. |

We deliberately do **not** scrape Google Scholar (no API, blocks bots) or ACM DL
(auth required for bulk metadata). `--author` is Crossref-only.

> Crossref often omits abstracts for conference papers, so those candidates have
> an empty abstract. Add one during review if you want it shown on the page.

### Working offline / behind a network policy

Save an API response elsewhere and parse it locally (repeatable, takes precedence
over the network):

```sh
python3 tools/fetch_publications.py --from-file crossref_response.json
python3 tools/fetch_publications.py --source dblp --from-file dblp_response.json
```

## 2. Review candidates

```sh
python3 tools/review_publications.py
```

Each candidate is shown one at a time. Controls:

| key | action |
|-----|--------|
| `a` | accept as-is → `_data/publications.yml` |
| `s` | skip → recorded in `excluded_publications.yml` (won't resurface) |
| `e` | edit fields, then accept |
| `b` | go back one |
| `w` | write accepted + excluded, then quit |
| `q` | quit without writing |

**Progress is saved after every decision** to `tools/.review_state.json`
(git-ignored), so you can quit and resume — already-reviewed candidates are
skipped next run (use `--review-all` to revisit them).

## The "external work" flag

A publication with **no BJC-team authors** is external work (e.g. a third-party
adaptation of BJC, or Jens Mönig's solo Snap! design papers). Mark these with:

```yaml
- title: '...'
  external: true   # renders an "external work" badge; filterable on the page
  ...
```

The Research page shows an *external work* badge and an **All work / BJC team /
External work** filter driven by this field.

## Verify before committing

```sh
git diff _data/publications.yml
bundle exec jekyll build
```

## Files

| file | purpose |
|------|---------|
| `fetch_publications.py` | pull + normalize + relevance-filter + dedupe candidates |
| `review_publications.py` | interactive, resumable accept/skip/edit → append |
| `pubs_common.py` | shared YAML load / dedupe / safe-append helpers |
| `excluded_publications.yml` | reviewed-and-rejected papers (committed; skipped by fetch) |
| `requirements.txt` | Python dependencies |
| `candidates.json` | fetch output (git-ignored) |
| `.review_state.json` | resumable review progress (git-ignored) |
