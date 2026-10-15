"""Offline checks on the Level 2 tracker: data/level2.csv, docs/level2.md and the README status line.

The weekly workflow asks CELLAR for changes; that needs the network. These checks run
anywhere: the committed CSV is well formed, the generated pages still match it, the
hand-written Level 2 entries agree with it, and the parsing and diffing logic behaves
on a fixed CELLAR answer.
"""

import re

import pytest

import cellar
import level2

ROWS, EXTRA = level2.read_csv()
README = level2.README_PATH.read_text(encoding="utf-8")
ISO = re.compile(r"^\d{4}-\d{2}-\d{2}$")
ELI = "http://data.europa.eu/eli/"


def binding(celex, date="", date_type="", comment="", **fields):
    row = {"basic_celex": "32023R1114", "celex": celex, "type": level2.RESOURCE_TYPE + "REG_DEL",
           "eli": f"{ELI}reg_del/{celex[1:5]}/{int(celex[6:])}/oj", "in_force": "1", "adopted": "2025-06-27",
           "end_of_validity": "9999-12-31",
           "title": f"Commission Delegated Regulation (EU) {celex[1:5]}/{int(celex[6:])} of 27 June 2025 "
                    "supplementing Regulation (EU) 2023/1114 of the European Parliament and of the Council "
                    "with regard to regulatory technical standards specifying the minimum contents of the "
                    "liquidity  management policy (Text with EEA relevance)",
           "date": date, "date_type": date_type, "date_comment": comment}
    row.update(fields)
    return {key: value for key, value in row.items() if value}


ENTRY_INTO_FORCE = "{EV|http://publications.europa.eu/resource/authority/fd_335/EV} Date of entry into force"
APPLICATION = "{MA|http://publications.europa.eu/resource/authority/fd_335/MA} Date of application"


def test_pages_match_the_csv():
    assert level2.main(["check"]) == 0, "run: python scripts/level2.py render"


def test_csv_rows_are_well_formed():
    assert ROWS, "data/level2.csv is empty"
    keys = [(row["regime"], row["celex"]) for row in ROWS]
    assert len(keys) == len(set(keys)), "duplicate (regime, celex) rows"
    regimes = {regime.name for regime in level2.REGIMES}
    for row in ROWS:
        parts = cellar.CELEX.match(row["celex"])
        assert parts, row["celex"]
        assert row["regime"] in regimes, row["regime"]
        assert row["in_force"] in {"true", "false"}, row["celex"]
        assert ISO.match(row["adopted"]) and ISO.match(row["entry_into_force"]), row["celex"]
        assert row["adopted"] <= row["entry_into_force"], row["celex"]
        assert row["eli"].startswith(ELI), row["celex"]
        assert f"{parts['year']}/{int(parts['number'])}" in row["act"], (row["act"], row["celex"])


def test_csv_covers_micar_and_dora():
    counts = {name: sum(row["regime"] == name and row["in_force"] == "true" for row in ROWS)
              for name in ("MiCAR", "DORA")}
    assert counts["MiCAR"] > 0 and counts["DORA"] > 0, counts


def test_status_line_counts_match_the_csv():
    status = re.search(re.escape(level2.STATUS_START) + r"\n(.*)\n" + re.escape(level2.STATUS_END), README)[1]
    for regime in level2.REGIMES:
        stated = int(re.search(rf"\[{re.escape(regime.name)} (\d+)\]", status)[1])
        assert stated == sum(row["regime"] == regime.name and row["in_force"] == "true" for row in ROWS), regime.name


def test_annotated_readme_entries_agree_with_the_csv():
    by_celex = {row["celex"]: row for row in ROWS}
    checked = 0
    for line in level2.level2_section(README):
        eli = re.search(r"\(https://eur-lex\.europa\.eu/eli/([a-z_]+/\d{4}/\d+)", line)
        status = re.search(r"Adopted (\d{1,2} \w+ \d{4}), in force (\d{1,2} \w+ \d{4})", line)
        if not (eli and status):
            continue
        row = by_celex[cellar.celex_from_eli(eli[1])]
        assert (cellar.iso_date(status[1]), cellar.iso_date(status[2])) == (row["adopted"], row["entry_into_force"])
        checked += 1
    assert checked, "no dated EUR-Lex entry under Level 2 measures"


def test_parse_folds_dates_flags_and_titles():
    rows = level2.parse([
        binding("32025R1264", "2025-10-23", ENTRY_INTO_FORCE),
        binding("32025R1264", "2026-01-01", APPLICATION),
        binding("32025R1264", "2026-07-01", APPLICATION, "{MA/PART|x} Partial application"),
    ])
    assert len(rows) == 1
    row = rows[0]
    assert row["act"] == "Delegated Regulation (EU) 2025/1264"
    assert (row["entry_into_force"], row["applies_from"], row["applies_in_part_from"]) == \
        ("2025-10-23", "2026-01-01", "2026-07-01")
    assert row["in_force"] == "true" and row["end_of_validity"] == ""
    assert "  " not in row["title"]
    assert row["eli"] == f"{ELI}reg_del/2025/1264/oj"


def test_subject_drops_the_citation_and_the_supplementing_preamble():
    title = level2.parse([binding("32025R1264")])[0]["title"]
    assert level2.subject(title) == ("Regulatory technical standards specifying the minimum contents of the "
                                     "liquidity management policy")


def test_merge_keeps_hand_added_columns():
    fetched = [{"regime": "DORA", "celex": "32024R1774", "title": "new title"}]
    existing = [{"regime": "DORA", "celex": "32024R1774", "title": "old title", "what_it_fixes": "ICT risk"}]
    merged = level2.merge(fetched, existing, ["what_it_fixes"])
    assert merged == [{"regime": "DORA", "celex": "32024R1774", "title": "new title", "what_it_fixes": "ICT risk"}]


def test_guard_refuses_an_empty_answer_for_a_regime():
    with pytest.raises(SystemExit):
        level2.guard([], [{"regime": "MiCAR", "celex": "32025R1264"}])


def test_compare_reports_new_changed_and_removed_acts():
    old = level2.parse([binding("32025R1264", "2025-10-23", ENTRY_INTO_FORCE),
                        binding("32024R1503", "2024-06-19", ENTRY_INTO_FORCE)])
    new = level2.parse([binding("32025R1264", "2025-10-23", ENTRY_INTO_FORCE, in_force="0"),
                        binding("32026R0001", "2026-02-01", ENTRY_INTO_FORCE)])
    kinds = {(change.kind, change.celex) for change in level2.compare(old, new)}
    assert kinds == {("new", "32026R0001"), ("in_force", "32025R1264"), ("removed", "32024R1503")}
    body = level2.report(level2.compare(old, new), "2026-10-19")
    assert "### New acts (1)" in body and "### In-force flag changed (1)" in body
    assert "https://eur-lex.europa.eu/eli/reg_del/2026/1/oj" in body


def test_csv_round_trip_is_stable():
    assert level2.to_csv(ROWS, EXTRA) == level2.CSV_PATH.read_text(encoding="utf-8")
