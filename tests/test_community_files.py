"""Offline checks on the community health files.

GitHub reads these files from fixed paths and quietly drops an issue form it cannot
parse, so a moved file or a missing key shows up only as a template that is no longer
offered. These checks need no network and no YAML parser: CI installs only pytest.
"""

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FORMS = [f".github/ISSUE_TEMPLATE/{name}.yml" for name in ("add-entry", "broken-link", "level2-status-update")]
FILES = ["CODE_OF_CONDUCT.md", "CITATION.cff", ".github/pull_request_template.md",
         ".github/ISSUE_TEMPLATE/config.yml", *FORMS]


def _read(relative):
    return (ROOT / relative).read_text(encoding="utf-8")


def test_community_files_exist():
    missing = [name for name in FILES if not (ROOT / name).is_file()]
    assert not missing, f"missing: {missing}"


def test_issue_forms_have_name_description_and_body():
    for form in FORMS:
        keys = set(re.findall(r"^(\w+):", _read(form), re.M))
        missing = {"name", "description", "body"} - keys
        assert not missing, f"{form} lacks top-level keys: {sorted(missing)}"


def test_level2_form_asks_for_celex_status_date_and_source():
    ids = set(re.findall(r"^\s+id: (\S+)$", _read(FORMS[2]), re.M))
    missing = {"celex", "status", "date", "source-url"} - ids
    assert not missing, f"level2-status-update.yml lacks fields: {sorted(missing)}"


def test_code_of_conduct_has_no_placeholder():
    assert "[INSERT" not in _read("CODE_OF_CONDUCT.md")


def test_citation_declares_version_and_license():
    citation = _read("CITATION.cff")
    assert re.search(r"^cff-version: 1\.2\.0$", citation, re.M)
    assert re.search(r"^license: CC0-1\.0$", citation, re.M)
