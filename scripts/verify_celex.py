"""Check the README's EUR-Lex entries against CELLAR, the EU Publications Office's metadata.

EUR-Lex answers automated clients with HTTP 202 and an empty page, so a link checker
"passes" every EUR-Lex link without fetching it. This script checks what those entries
actually claim, by CELEX number:

- the act exists in CELLAR;
- the act the link text cites (e.g. "Regulation (EU) 2023/1114") is the act linked;
- the act is still in force;
- an "Adopted <date>, in force <date>." status line matches CELLAR's date of the act
  and date of entry into force.

    python scripts/verify_celex.py [README.md ...]    exit 1 on any mismatch
"""

import re
import sys
from collections import namedtuple
from pathlib import Path

import cellar

ROOT = Path(__file__).resolve().parents[1]

Entry = namedtuple("Entry", "path line name url celex adopted in_force")
LINK = re.compile(r"^- \[(?P<name>[^\]]+)\]\((?P<url>https?://eur-lex\.europa\.eu/[^\s)]+)\) - (?P<desc>.*)$")
CELEX_URL = re.compile(r"[?&]uri=CELEX:(?P<celex>[0-9A-Z()]+)")
ELI_URL = re.compile(r"/eli/(?P<path>[a-z_]+/\d{4}/\d+)")
STATUS = re.compile(r"Adopted (?P<adopted>\d{1,2} [A-Z][a-z]+ \d{4}), in force (?P<in_force>\d{1,2} [A-Z][a-z]+ \d{4})")


def entries(path):
    """The README entries that link to EUR-Lex, with the CELEX number and dates they state."""
    found = []
    for number, text in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        match = LINK.match(text)
        if not match:
            continue
        url = match["url"]
        celex = None
        if by_celex := CELEX_URL.search(url):
            celex = by_celex["celex"]
        elif by_eli := ELI_URL.search(url):
            celex = cellar.celex_from_eli(by_eli["path"])
        status = STATUS.search(match["desc"])
        found.append(Entry(path.name, number, match["name"], url, celex,
                           cellar.iso_date(status["adopted"]) if status else None,
                           cellar.iso_date(status["in_force"]) if status else None))
    return found


def query(celexes):
    values = " ".join(f'"{celex}"^^xsd:string' for celex in sorted(set(celexes)))
    return cellar.PREFIXES + f"""
SELECT ?celex ?in_force ?adopted ?date ?date_type ?date_comment
WHERE {{
  VALUES ?celex {{ {values} }}
  ?work cdm:resource_legal_id_celex ?celex .
  OPTIONAL {{ ?work cdm:resource_legal_in-force ?in_force }}
  OPTIONAL {{ ?work cdm:work_date_document ?adopted }}
  OPTIONAL {{
{cellar.DATES_PATTERN}
  }}
}}
"""


def records(rows):
    """One record per CELEX number: in-force flags, dates of the act, dates of entry into force."""
    acts = {}
    for row in rows:
        act = acts.setdefault(row["celex"], {"in_force": set(), "adopted": set(), "entry": set(), "unannotated": set()})
        if row.get("in_force"):
            act["in_force"].add(cellar.boolean(row["in_force"]))
        if row.get("adopted"):
            act["adopted"].add(row["adopted"])
        if row.get("date"):
            kind = cellar.date_kind(row.get("date_type"), row.get("date_comment"))
            if kind == "EV":
                act["entry"].add(row["date"])
            elif not kind:
                act["unannotated"].add(row["date"])
    return acts


def problems(found, acts):
    """Everything an entry claims that CELLAR does not confirm, one line each."""
    issues = []
    for entry in found:
        where = f"{entry.path}:{entry.line} {entry.name}"
        if not entry.celex:
            issues.append(f"{where}: no CELEX number or ELI in {entry.url}")
            continue
        act = acts.get(entry.celex)
        if act is None:
            issues.append(f"{where}: CELLAR has no act {entry.celex}")
            continue
        cited = cellar.celex_from_citation(entry.name)
        if cited and cited != entry.celex:
            issues.append(f"{where}: link text cites {cited}, link goes to {entry.celex}")
        if act["in_force"] != {"true"}:
            flags = ", ".join(sorted(act["in_force"])) or "missing"
            issues.append(f"{where}: CELLAR in-force flag is {flags}, not true")
        if entry.adopted and entry.adopted not in act["adopted"]:
            issues.append(f"{where}: says adopted {entry.adopted}, CELLAR has {', '.join(sorted(act['adopted'])) or 'no date'}")
        if entry.in_force:
            entry_dates = act["entry"] or act["unannotated"]
            if not entry_dates or entry.in_force != min(entry_dates):
                found_dates = ", ".join(sorted(entry_dates)) or "no date"
                issues.append(f"{where}: says in force {entry.in_force}, CELLAR has {found_dates}")
    return issues


def main(argv=None):
    paths = [Path(arg) for arg in (argv if argv is not None else sys.argv[1:])] or [ROOT / "README.md"]
    found = [entry for path in paths for entry in entries(path)]
    celexes = [entry.celex for entry in found if entry.celex]
    acts = records(cellar.select(query(celexes))) if celexes else {}
    issues = problems(found, acts)
    for issue in issues:
        print(issue, file=sys.stderr)
    dated = sum(1 for entry in found if entry.adopted)
    print(f"{len(found)} EUR-Lex entries checked against CELLAR ({dated} with dates): "
          f"{len(issues)} problem(s)")
    return 1 if issues else 0


if __name__ == "__main__":
    sys.exit(main())
