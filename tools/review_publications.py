#!/usr/bin/env python3
"""Interactively review fetched publication candidates.

Reads ``candidates.json`` (produced by ``fetch_publications.py``), shows each
candidate one at a time, and lets you accept, skip, or edit it. Progress is
saved after every decision to ``tools/.review_state.json`` so you can quit and
resume later. Accepted entries are appended to ``_data/publications.yml`` when
you write.

Controls (shown each prompt):
    a  accept        s  skip          e  edit fields
    b  back          w  write+quit    q  quit (no write)
"""

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pubs_common import (  # noqa: E402
    EXCLUDED_YML,
    KNOWN_CATEGORIES,
    PUBLICATIONS_YML,
    REPO_ROOT,
    append_entries,
    append_excluded,
    normalize_title,
)

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_CANDIDATES = os.path.join(HERE, "candidates.json")
DEFAULT_STATE = os.path.join(HERE, ".review_state.json")

# Fields the reviewer can edit, in a sensible editing order.
EDITABLE_FIELDS = [
    "title", "authors", "year", "journal", "category",
    "abstract", "external_link", "doi", "filename",
]


def candidate_key(candidate):
    return normalize_title(candidate.get("title"))


def load_json(path, default):
    if not os.path.exists(path):
        return default
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def save_state(state, path):
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(state, handle, indent=2, ensure_ascii=False)


def clean_entry(candidate):
    """Strip internal (_-prefixed) bookkeeping fields before persisting."""
    return {k: v for k, v in candidate.items() if not k.startswith("_")}


def show(candidate, index, total, decision):
    line = "=" * 70
    status = ""
    if decision:
        status = "   [previously {0}]".format(decision.get("status"))
    print("\n" + line)
    print("Candidate {0} of {1}{2}".format(index + 1, total, status))
    print(line)
    print("  Title    : {0}".format(candidate.get("title") or "(none)"))
    print("  Authors  : {0}".format(candidate.get("authors") or "(none)"))
    print("  Year     : {0}".format(candidate.get("year") or "(none)"))
    print("  Venue    : {0}".format(candidate.get("journal") or "(none)"))
    print("  Type     : {0}".format(candidate.get("category") or "(none)"))
    print("  DOI      : {0}".format(candidate.get("doi") or "(none)"))
    print("  Link     : {0}".format(candidate.get("external_link") or "(none)"))
    if candidate.get("abstract"):
        print("  Abstract : {0}".format(candidate["abstract"]))
    if candidate.get("_source"):
        print("  Source   : {0}".format(candidate["_source"]))


def edit_entry(candidate):
    """Prompt-driven field editor. Returns the edited candidate (mutated copy)."""
    entry = dict(candidate)
    print("\nEdit fields (press Enter to keep current value).")
    print("Known types: {0}".format(", ".join(KNOWN_CATEGORIES)))
    for field in EDITABLE_FIELDS:
        current = entry.get(field)
        try:
            new = input("  {0} [{1}]: ".format(field, current if current not in (None, "") else ""))
        except EOFError:
            break
        if new.strip() == "":
            continue
        if field == "year":
            entry[field] = int(new) if new.strip().isdigit() else new.strip()
        else:
            entry[field] = new.strip()
    return entry


def flush_accepted(state, candidates_by_key, path):
    """Append accepted-but-unwritten entries to publications.yml; mark written."""
    pending = []
    keys = []
    for key, decision in state["decisions"].items():
        if decision.get("status") == "accepted" and not decision.get("written"):
            entry = decision.get("entry") or candidates_by_key.get(key, {})
            pending.append(clean_entry(entry))
            keys.append(key)
    if not pending:
        print("No new accepted entries to write.")
        return 0
    written = append_entries(
        pending, path=path,
        header="Added via tools/review_publications.py",
    )
    for key in keys:
        state["decisions"][key]["written"] = True
    print("Wrote {0} entry(ies) to {1}".format(
        written, os.path.relpath(path, REPO_ROOT)))
    return written


def flush_excluded(state, candidates_by_key, path=EXCLUDED_YML):
    """Append skipped-but-unrecorded entries to the excluded list; mark written."""
    pending = []
    keys = []
    for key, decision in state["decisions"].items():
        if decision.get("status") == "skipped" and not decision.get("written"):
            entry = decision.get("entry") or candidates_by_key.get(key, {})
            if entry:
                pending.append(clean_entry(entry))
                keys.append(key)
    if not pending:
        return 0
    written = append_excluded(pending, path=path)
    for key in keys:
        state["decisions"][key]["written"] = True
    print("Recorded {0} skipped paper(s) in {1}".format(
        written, os.path.relpath(path, REPO_ROOT)))
    return written


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--candidates", default=DEFAULT_CANDIDATES,
                        help="Path to candidates.json (default: tools/candidates.json).")
    parser.add_argument("--state", default=DEFAULT_STATE,
                        help="Path to the resumable progress file.")
    parser.add_argument("--out", default=PUBLICATIONS_YML,
                        help="Data file to append accepted entries to.")
    parser.add_argument("--excluded", default=EXCLUDED_YML,
                        help="File to record skipped (rejected) papers in.")
    parser.add_argument("--review-all", action="store_true",
                        help="Revisit candidates already decided in a prior session.")
    args = parser.parse_args(argv)

    candidates = load_json(args.candidates, None)
    if not candidates:
        print("No candidates found at {0}. Run fetch_publications.py first."
              .format(args.candidates), file=sys.stderr)
        return 1

    state = load_json(args.state, {"decisions": {}})
    state.setdefault("decisions", {})
    candidates_by_key = {candidate_key(c): c for c in candidates}

    total = len(candidates)
    index = 0
    while 0 <= index < total:
        candidate = candidates[index]
        key = candidate_key(candidate)
        decision = state["decisions"].get(key)
        if decision and not args.review_all:
            index += 1
            continue

        show(candidate, index, total, decision)
        try:
            choice = input("\n[a]ccept [s]kip [e]dit [b]ack [w]rite+quit [q]uit > ").strip().lower()
        except EOFError:
            print("\n(end of input) Saving progress and writing accepted entries.")
            break

        if choice in ("a", "accept"):
            state["decisions"][key] = {"status": "accepted", "entry": clean_entry(candidate), "written": False}
            save_state(state, args.state)
            index += 1
        elif choice in ("s", "skip"):
            # Keep full metadata so the skip persists to the excluded list.
            state["decisions"][key] = {"status": "skipped", "entry": clean_entry(candidate), "written": False}
            save_state(state, args.state)
            index += 1
        elif choice in ("e", "edit"):
            edited = edit_entry(candidate)
            candidates[index] = edited
            candidates_by_key[key] = edited
            state["decisions"][key] = {"status": "accepted", "entry": clean_entry(edited), "written": False}
            save_state(state, args.state)
            print("Saved edits and accepted.")
            index += 1
        elif choice in ("b", "back"):
            index = max(0, index - 1)
        elif choice in ("w", "write"):
            flush_accepted(state, candidates_by_key, args.out)
            flush_excluded(state, candidates_by_key, args.excluded)
            save_state(state, args.state)
            print("Progress saved. Bye!")
            return 0
        elif choice in ("q", "quit"):
            save_state(state, args.state)
            print("Progress saved (nothing written). Bye!")
            return 0
        else:
            print("Unrecognized choice: {0!r}".format(choice))

    # Reached the end (or EOF): write anything still pending and summarize.
    flush_accepted(state, candidates_by_key, args.out)
    flush_excluded(state, candidates_by_key, args.excluded)
    save_state(state, args.state)
    accepted = sum(1 for d in state["decisions"].values() if d.get("status") == "accepted")
    skipped = sum(1 for d in state["decisions"].values() if d.get("status") == "skipped")
    print("\nDone. {0} accepted, {1} skipped, {2} total reviewed."
          .format(accepted, skipped, accepted + skipped))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
