"""Offline checks on scripts/verify_celex.py, against a fixed CELLAR answer instead of the network."""

import cellar
import verify_celex

EV = "{EV|http://publications.europa.eu/resource/authority/fd_335/EV} Date of entry into force"
CELLAR_ROWS = [
    {"celex": "32023R1114", "in_force": "1", "adopted": "2023-05-31", "date": "2023-06-29", "date_type": EV},
    {"celex": "32025R1264", "in_force": "1", "adopted": "2025-06-27", "date": "2025-10-23", "date_type": EV},
    {"celex": "32019R0001", "in_force": "0", "adopted": "2019-01-01", "date": "2019-02-01", "date_type": EV},
]


def check(tmp_path, *lines):
    readme = tmp_path / "README.md"
    readme.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return verify_celex.problems(verify_celex.entries(readme), verify_celex.records(CELLAR_ROWS))


def test_matching_entries_pass(tmp_path):
    assert check(
        tmp_path,
        "- [MiCAR — Regulation (EU) 2023/1114](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32023R1114) - Crypto.",
        "- [Delegated Regulation (EU) 2025/1264](https://eur-lex.europa.eu/eli/reg_del/2025/1264/oj) - RTS. "
        "Adopted 27 June 2025, in force 23 October 2025.",
    ) == []


def test_wrong_dates_are_reported(tmp_path):
    issues = check(tmp_path, "- [Delegated Regulation (EU) 2025/1264](https://eur-lex.europa.eu/eli/reg_del/2025/1264/oj) - "
                             "RTS. Adopted 26 June 2025, in force 24 October 2025.")
    assert len(issues) == 2
    assert "adopted 2025-06-26, CELLAR has 2025-06-27" in issues[0]
    assert "in force 2025-10-24, CELLAR has 2025-10-23" in issues[1]


def test_link_text_citing_another_act_is_reported(tmp_path):
    issues = check(tmp_path, "- [DORA — Regulation (EU) 2022/2554](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32023R1114) - Typo.")
    assert issues == ["README.md:1 DORA — Regulation (EU) 2022/2554: link text cites 32022R2554, link goes to 32023R1114"]


def test_unknown_and_repealed_acts_are_reported(tmp_path):
    issues = check(tmp_path,
                   "- [Regulation (EU) 2019/1](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32019R0001) - Old.",
                   "- [Regulation (EU) 2099/1](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32099R0001) - Typo.")
    assert any("in-force flag is false" in issue for issue in issues)
    assert any("CELLAR has no act 32099R0001" in issue for issue in issues)


def test_main_queries_every_eur_lex_entry_once(monkeypatch, tmp_path, capsys):
    readme = tmp_path / "README.md"
    readme.write_text("- [Delegated Regulation (EU) 2025/1264](https://eur-lex.europa.eu/eli/reg_del/2025/1264/oj) - "
                      "RTS. Adopted 27 June 2025, in force 23 October 2025.\n"
                      "- [EBA page](https://www.eba.europa.eu/x) - Not on EUR-Lex.\n", encoding="utf-8")
    queries = []
    monkeypatch.setattr(cellar, "select", lambda query: queries.append(query) or CELLAR_ROWS)
    assert verify_celex.main([str(readme)]) == 0
    assert len(queries) == 1 and '"32025R1264"^^xsd:string' in queries[0]
    assert "1 EUR-Lex entries checked against CELLAR (1 with dates): 0 problem(s)" in capsys.readouterr().out


def test_the_readme_has_eur_lex_entries_to_check():
    found = verify_celex.entries(verify_celex.ROOT / "README.md")
    assert len(found) >= 6 and all(entry.celex for entry in found)
