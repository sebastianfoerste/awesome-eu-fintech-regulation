"""Offline structural checks on README.md.

The weekly workflow checks that links resolve; that needs the network. These checks
run anywhere and catch the mistakes a hand-edited list actually makes: malformed
entries, duplicate links, a contents entry pointing at a renamed heading, a
disclosure count that no longer matches the curator's own entries, entries out of
order, status lines that drift from the fixed wording, and leftover placeholders.
"""

import re
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
README = (ROOT / "README.md").read_text(encoding="utf-8")
LINES = README.splitlines()

ENTRY = re.compile(r"^- \[(?P<name>[^\]]+)\]\((?P<url>https?://[^\s)]+)\) - (?P<desc>\S.*)$")
ANCHOR = re.compile(r"^- \[[^\]]+\]\(#(?P<anchor>[^)]+)\)$")
NUMBERS = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10}

# The fixed wording for Level 2 status lines, as set out in CONTRIBUTING.md.
DATE = r"\d{1,2} [A-Z][a-z]+ \d{4}"
ADOPTED = re.compile(rf"Adopted (?P<adopted>{DATE}), in force (?P<in_force>{DATE})(?:, applies from (?P<applies>{DATE}))?\.$")
SUBMITTED = re.compile(rf"Submitted (?P<submitted>{DATE})(?:; [^;]+)*; not yet adopted\.$")
DATES = re.compile(DATE)

# Sections whose entries are kept in alphabetical order (CONTRIBUTING.md).
ALPHABETICAL = ["## Guides and trackers", "## Open-source tools", "### Maintained by the curator",
                "## Related lists", "## Footnotes"]
PLACEHOLDER = re.compile(r"\[UNVERIFIED\]|\bTODO\b|\bTBD\b")


def _slug(heading):
    return re.sub(r"[^\w\- ]", "", heading.strip().lower()).replace(" ", "-")


def _entry_lines():
    """List entries after the Contents heading; the intro bullets above it are not entries."""
    start = LINES.index("## Contents")
    return [line for line in LINES[start:] if line.startswith("- ") and not ANCHOR.match(line)]


def _section(heading):
    """The lines under `heading`, up to the next heading of any level."""
    start = LINES.index(heading)
    block = []
    for line in LINES[start + 1:]:
        if line.startswith("#"):
            break
        block.append(line)
    return block


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


def test_contents_is_the_first_section():
    sections = [line for line in LINES if line.startswith("## ")]
    assert sections[0] == "## Contents", f"first section is {sections[0]!r}, expected '## Contents'"


def test_curator_disclosure_count_matches_entries():
    block = _section("### Maintained by the curator")
    disclosure = next(line for line in block if line.startswith("Disclosure:"))
    stated = NUMBERS[re.search(r"these (\w+)", disclosure)[1]]
    listed = sum(1 for line in block if ENTRY.match(line))
    assert stated == listed, f"disclosure says {stated}, section lists {listed}"


def test_alphabetical_sections_are_in_order():
    for heading in ALPHABETICAL:
        names = [m["name"] for line in _section(heading) if (m := ENTRY.match(line))]
        assert names, f"{heading} has no entries"
        assert names == sorted(names, key=str.casefold), f"{heading} is not in alphabetical order: {names}"


def test_level2_status_lines_use_the_fixed_wording():
    for line in _section("## Level 2 measures"):
        entry = ENTRY.match(line)
        if not entry:
            continue
        desc = entry["desc"]
        if "eur-lex.europa.eu" in entry["url"]:
            assert ADOPTED.search(desc), f"adopted act without 'Adopted <date>, in force <date>.': {entry['name']}"
        if "Submitted" in desc:
            assert SUBMITTED.search(desc), f"draft without 'Submitted <date>; ...; not yet adopted.': {entry['name']}"


def test_status_line_dates_are_real_dates():
    for line in _section("## Level 2 measures"):
        for text in DATES.findall(line):
            time.strptime(text, "%d %B %Y")  # raises on "31 June 2025" or a misspelt month


def test_no_placeholders_left():
    for path in (ROOT / "README.md", ROOT / "CONTRIBUTING.md", ROOT / "docs" / "curation.md"):
        found = [line for line in path.read_text(encoding="utf-8").splitlines() if PLACEHOLDER.search(line)]
        assert not found, f"placeholder text in {path.name}:\n" + "\n".join(found)
