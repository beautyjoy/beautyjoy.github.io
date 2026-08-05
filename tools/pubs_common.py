"""Shared helpers for the BJC publications tooling.

These utilities are used by both ``fetch_publications.py`` (which pulls candidate
publications from scholarly sources) and ``review_publications.py`` (which lets a
human accept/reject candidates and appends the accepted ones to
``_data/publications.yml``).

The design goal is to *never* rewrite the existing ``publications.yml`` in a way
that clobbers its many hand-written comments and section headers. We therefore
only ever read that file (to dedupe against it) and *append* new entries to the
end of it as plain text.
"""

import os
import re

try:
    import yaml
except ImportError as exc:  # pragma: no cover - surfaced to the user directly
    raise SystemExit(
        "PyYAML is required. Install the tooling deps with:\n"
        "    pip install -r tools/requirements.txt"
    ) from exc


# Repo root is the parent of the tools/ directory this file lives in.
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PUBLICATIONS_YML = os.path.join(REPO_ROOT, "_data", "publications.yml")
# Papers a human reviewed and chose *not* to publish. Kept (with full metadata)
# so the fetch/review tools can skip them instead of re-surfacing them forever.
EXCLUDED_YML = os.path.join(os.path.dirname(os.path.abspath(__file__)), "excluded_publications.yml")

# Fields we emit, in the order the existing file uses them.
# ``external`` and ``slides_link`` are optional -- only emitted when truthy.
FIELD_ORDER = [
    "title",
    "filename",
    "authors",
    "doi",
    "category",
    "external",
    "year",
    "journal",
    "abstract",
    "external_link",
    "slides_link",
]

# Optional fields that are omitted entirely when falsy, to keep entries tidy.
OPTIONAL_FIELDS = {"external", "slides_link"}

# Categories the Research page knows how to filter on (see research.html).
KNOWN_CATEGORIES = [
    "paper",
    "poster",
    "talks",
    "workshop",
    "dissertation",
    "external evaluation",
]


def load_existing(path=PUBLICATIONS_YML):
    """Read the publications data file. Returns a list of dicts (never mutated)."""
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    return [entry for entry in (data or []) if isinstance(entry, dict)]


# Trailing qualifiers that publishers tack on but which don't change identity,
# e.g. "... Curriculum (Abstract Only)". Stripped before comparison so the same
# paper dedupes across sources.
_TITLE_QUALIFIER_RE = re.compile(
    r"\s*\((abstract only|abstract|extended abstract|keynote|poster|panel|"
    r"work in progress|wip)\)\s*$",
    re.IGNORECASE,
)


def normalize_title(title):
    """Lowercase, drop trailing qualifiers, strip punctuation/whitespace runs."""
    if not title:
        return ""
    text = _TITLE_QUALIFIER_RE.sub("", str(title))
    text = re.sub(r"[^a-z0-9]+", " ", text.lower())
    return text.strip()


def normalize_doi(doi):
    """Strip URL prefixes so equal DOIs compare equal."""
    if not doi:
        return ""
    text = str(doi).strip().lower()
    text = re.sub(r"^https?://(dx\.)?doi\.org/", "", text)
    return text


def dedupe_key(entry):
    """A stable key for deduping: prefer DOI, fall back to normalized title."""
    doi = normalize_doi(entry.get("doi"))
    if doi:
        return "doi:" + doi
    return "title:" + normalize_title(entry.get("title"))


def existing_keys(existing):
    """Build the set of dedupe keys (by DOI and by title) already on the site."""
    keys = set()
    for entry in existing:
        keys.add(dedupe_key(entry))
        # Also index the title on its own so a DOI-keyed entry still blocks a
        # title-only duplicate coming from a different source.
        title_key = "title:" + normalize_title(entry.get("title"))
        if title_key.strip() != "title:":
            keys.add(title_key)
    return keys


def is_duplicate(entry, keys):
    """True if ``entry`` matches something already in ``keys`` (see existing_keys)."""
    if dedupe_key(entry) in keys:
        return True
    title_key = "title:" + normalize_title(entry.get("title"))
    return title_key.strip() != "title:" and title_key in keys


def _yaml_scalar(value):
    """Render a value as a safe single-line YAML scalar.

    Empty/None becomes a blank (matching the existing file's ``doi:`` style).
    Ints pass through unquoted. Everything else is single-quoted with internal
    single quotes doubled, which is valid YAML for arbitrary one-line text.
    """
    if value is None or value == "":
        return ""
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, int):
        return str(value)
    text = " ".join(str(value).split())  # collapse newlines/whitespace runs
    return "'" + text.replace("'", "''") + "'"


def format_entry(entry):
    """Format one publication dict as a YAML list item matching the file style."""
    lines = []
    for i, field in enumerate(FIELD_ORDER):
        if field in OPTIONAL_FIELDS and not entry.get(field):
            continue  # optional; only emit when truthy
        prefix = "- " if i == 0 else "  "
        scalar = _yaml_scalar(entry.get(field))
        if scalar == "":
            lines.append("{0}{1}:".format(prefix, field))
        else:
            lines.append("{0}{1}: {2}".format(prefix, field, scalar))
    return "\n".join(lines)


def append_entries(entries, path=PUBLICATIONS_YML, header=None):
    """Append formatted entries to the data file, then verify it still parses.

    Returns the number of entries written. Raises ValueError (after rolling the
    file back) if the result would not be valid YAML.
    """
    if not entries:
        return 0

    original = ""
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as handle:
            original = handle.read()

    blocks = []
    if header:
        blocks.append("# " + header)
    blocks.extend(format_entry(entry) for entry in entries)

    addition = "\n" + "\n\n".join(blocks) + "\n"
    if not original.endswith("\n"):
        addition = "\n" + addition

    with open(path, "a", encoding="utf-8") as handle:
        handle.write(addition)

    # Safety net: make sure we produced valid YAML; if not, restore the file.
    try:
        with open(path, "r", encoding="utf-8") as handle:
            yaml.safe_load(handle)
    except yaml.YAMLError as exc:
        with open(path, "w", encoding="utf-8") as handle:
            handle.write(original)
        raise ValueError(
            "Appending entries produced invalid YAML; file was restored."
        ) from exc

    return len(entries)


def load_excluded(path=EXCLUDED_YML):
    """Read the reviewed-and-excluded publications list (empty if none yet)."""
    return load_existing(path)


def append_excluded(entries, path=EXCLUDED_YML):
    """Append reviewed-out publications to the excluded list, creating it if new."""
    if not entries and os.path.exists(path):
        return 0
    if not os.path.exists(path):
        with open(path, "w", encoding="utf-8") as handle:
            handle.write(
                "# Publications a human reviewed and chose NOT to publish on the\n"
                "# Research page. Kept with full metadata so the fetch/review tools\n"
                "# can skip them instead of re-surfacing them. Delete an entry here\n"
                "# to allow it to be re-reviewed.\n"
                "---\n"
            )
    return append_entries(entries, path=path)
