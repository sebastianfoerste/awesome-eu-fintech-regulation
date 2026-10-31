"""Offline checks on the settings and shell logic of the weekly workflows.

Both workflows run on a schedule, so a mistake here shows up days later, or never:
a link check that counts EUR-Lex's empty 202 page as working passes without
checking anything, and a watcher that picks the wrong issue overwrites a report
someone filed by hand.
"""

import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def _read(relative):
    return (ROOT / relative).read_text(encoding="utf-8")


def _codes(spec):
    """'200..=201' -> {200, 201}; '300..303' -> {300, 301, 302}; '206' or 206 -> {206}."""
    spec = str(spec)
    if "..=" in spec:
        low, high = spec.split("..=")
        return set(range(int(low), int(high) + 1))
    if ".." in spec:
        low, high = spec.split("..")
        return set(range(int(low), int(high)))
    return {int(spec)}


def test_link_check_neither_accepts_202_nor_fetches_eur_lex():
    tomllib = pytest.importorskip("tomllib")  # Python 3.11+
    config = tomllib.loads(_read("lychee.toml"))
    accepted = set().union(*(_codes(spec) for spec in config["accept"]))
    assert 202 not in accepted, "EUR-Lex answers bots with an empty 202 page; accepting 202 passes unchecked links"
    assert 200 in accepted and 404 not in accepted
    eur_lex = "https://eur-lex.europa.eu/eli/reg_del/2025/1264/oj"
    assert any(re.search(pattern, eur_lex) for pattern in config["exclude"]), "EUR-Lex is checked by verify_celex.py"


def test_level2_watch_rewrites_only_its_own_issue():
    """The issue form files reports under the same label, so the watcher must find its issue by title."""
    workflow = _read(".github/workflows/level2-watch.yml")
    title = re.search(r'^\s+TITLE: "([^"]+)"$', workflow, re.M)
    assert title, "level2-watch.yml should set the watcher's issue title once, as TITLE"
    listing = re.search(r"gh issue list (.+?)\n(?!\s+--)", workflow, re.S)
    assert listing and 'select(.title == \\"$TITLE\\")' in listing[1], "gh issue list must pick the issue by title"
    assert '--title "$TITLE"' in workflow, "the watcher must create its issue under the title it searches for"
    form_title = re.search(r'^title: "([^"]*)"$', _read(".github/ISSUE_TEMPLATE/level2-status-update.yml"), re.M)[1]
    assert not title[1].startswith(form_title), "issues filed through the form would match the watcher's title"


WORKFLOWS = sorted((ROOT / ".github" / "workflows").glob("*.yml"))
USES = re.compile(r"^\s+(?:- )?uses: ")
# owner/repo[/path]@<full commit SHA> # v<version>: a tag can be moved, a commit cannot.
PINNED = re.compile(r"^\s+(?:- )?uses: [\w.-]+/[\w.-]+(?:/[\w./-]+)?@[0-9a-f]{40} # v\d+(?:\.\d+)*$")


def test_every_action_is_pinned_to_a_commit_with_its_version():
    """Dependabot (.github/dependabot.yml) moves the pins; nothing else should."""
    assert WORKFLOWS, "no workflows under .github/workflows"
    loose = [f"{path.name}:{number}: {line.strip()}"
             for path in WORKFLOWS
             for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1)
             if USES.match(line) and not PINNED.match(line)]
    assert not loose, "actions not pinned to a commit SHA with a version comment:\n" + "\n".join(loose)


def test_every_workflow_declares_permissions():
    missing = [path.name for path in WORKFLOWS
               if not re.search(r"^permissions:", path.read_text(encoding="utf-8"), re.M)]
    assert not missing, f"workflows without a top-level permissions block: {missing}"


def test_dependabot_watches_the_action_pins():
    config = _read(".github/dependabot.yml")
    assert re.search(r"^\s+- package-ecosystem: github-actions$", config, re.M), "dependabot.yml must cover github-actions"
