"""Offline structural checks on README.md.

The weekly workflow checks that links resolve; that needs the network. These checks
run anywhere and catch the mistakes a hand-edited list actually makes: malformed
entries, duplicate links, a contents entry pointing at a renamed heading, and a
disclosure count that no longer matches the curator's own entries.
"""

import re
from pathlib import Path

README = (Path(__file__).resolve().parents[1] / "README.md").read_text(encoding="utf-8")
LINES = README.splitlines()

ENTRY = re.compile(r"^- \[(?P<name>[^\]]+)\]\((?P<url>https?://[^\s)]+)\) - (?P<desc>\S.*)$")
ANCHOR = re.compile(r"^- \[[^\]]+\]\(#(?P<anchor>[^)]+)\)$")
NUMBERS = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10}


def _slug(heading):
    return re.sub(r"[^\w\- ]", "", heading.strip().lower()).replace(" ", "-")


def _entry_lines():
    return [line for line in LINES if line.startswith("- ") and not ANCHOR.match(line)]


def test_every_entry_is_well_formed():
    bad = [line for line in _entry_lines() if not ENTRY.match(line)]
    assert not bad, "malformed entries:\n" + "\n".join(bad)


def test_no_duplicate_links():
    urls = [ENTRY.match(line)["url"] for line in _entry_lines() if ENTRY.match(line)]
    duplicates = sorted({u for u in urls if urls.count(u) > 1})
    assert not duplicates, f"duplicate links: {duplicates}"


def test_contents_anchors_match_headings():
    headings = {_slug(line.lstrip("#")) for line in LINES if line.startswith("## ")}
    anchors = [m["anchor"] for line in LINES if (m := ANCHOR.match(line))]
    missing = [a for a in anchors if a not in headings]
    assert anchors and not missing, f"contents entries without a heading: {missing}"


def test_curator_disclosure_count_matches_entries():
    start = LINES.index("### Maintained by the curator")
    block = []
    for line in LINES[start + 1:]:
        if line.startswith("#"):
            break
        block.append(line)
    disclosure = next(line for line in block if line.startswith("Disclosure:"))
    stated = NUMBERS[re.search(r"these (\w+)", disclosure)[1]]
    listed = sum(1 for line in block if ENTRY.match(line))
    assert stated == listed, f"disclosure says {stated}, section lists {listed}"
