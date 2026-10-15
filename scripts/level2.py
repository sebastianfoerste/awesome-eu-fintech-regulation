"""Level 2 tracker: the Commission's delegated and implementing acts under each Level 1 act.

CELLAR, the EU Publications Office's metadata service, records which act each EU act
is based on, its dates and whether it is in force. This script asks CELLAR for the
delegated and implementing acts based on the five Level 1 acts this list covers, keeps
them in data/level2.csv, and renders docs/level2.md and the status line at the top of
README.md from that file. It reads metadata only and interprets nothing.

    python scripts/level2.py update   query CELLAR, rewrite the CSV, re-render both pages
    python scripts/level2.py render   re-render both pages from the CSV after editing it
    python scripts/level2.py check    exit 1 if a page no longer matches the CSV (offline)
    python scripts/level2.py diff     list what CELLAR now says differently from the CSV

Columns added to the CSV by hand (an annotation column, say) survive `update`.
"""

import argparse
import csv
import datetime
import io
import re
import sys
from collections import namedtuple
from pathlib import Path

import cellar

ROOT = Path(__file__).resolve().parents[1]
CSV_PATH = ROOT / "data" / "level2.csv"
DOCS_PATH = ROOT / "docs" / "level2.md"
README_PATH = ROOT / "README.md"

Regime = namedtuple("Regime", "name celex citation")
REGIMES = (
    Regime("MiCAR", "32023R1114", "Regulation (EU) 2023/1114"),
    Regime("DORA", "32022R2554", "Regulation (EU) 2022/2554"),
    Regime("MiFID II", "32014L0065", "Directive 2014/65/EU"),
    Regime("PSD2", "32015L2366", "Directive (EU) 2015/2366"),
    Regime("AI Act", "32024R1689", "Regulation (EU) 2024/1689"),
)
NOTES = {
    "MiFID II": "Acts based only on Regulation (EU) No 600/2014 (MiFIR) are not listed.",
}
RESOURCE_TYPE = "http://publications.europa.eu/resource/authority/resource-type/"
TYPES = {
    "REG_DEL": "Delegated Regulation",
    "REG_IMPL": "Implementing Regulation",
    "DIR_DEL": "Delegated Directive",
    "DIR_IMPL": "Implementing Directive",
    "DEC_DEL": "Delegated Decision",
    "DEC_IMPL": "Implementing Decision",
}
COLUMNS = ["regime", "celex", "act", "title", "adopted", "entry_into_force", "applies_from",
           "applies_in_part_from", "in_force", "end_of_validity", "eli"]

STATUS_START = "<!-- level2-status:start -->"
STATUS_END = "<!-- level2-status:end -->"
CHECKED = re.compile(r"^Checked against CELLAR on (?P<date>\d{1,2} [A-Z][a-z]+ \d{4})\.$", re.M)
PENDING = re.compile(r"; not yet adopted\.$")

CITATION = re.compile(r"^Commission ((?:Delegated|Implementing) (?:Regulation|Directive|Decision) "
                      r"\([^)]+\) (?:No )?\d+/\d+)")
SUBJECT_PREFIX = re.compile(r"^Commission (?:Delegated|Implementing) (?:Regulation|Directive|Decision) "
                            r"\([^)]+\) (?:No )?\d+/\d+ of \d{1,2} \w+ \d{4},? ")
# Official titles end in "(Text with EEA relevance)", "(... relevance.)" or "(... relevance. )".
EEA_RELEVANCE = re.compile(r"\s*\(Text with EEA relevance\.?\s*\)\.?$")
# Applied in order, at most one: drop the 'supplementing <Level 1 act> ...' preamble so the
# subject starts where the title says what the act does. Titles that match none stay whole.
LEVEL1_REFERENCE = r".*?of the European Parliament and of the Council(?: on [^,]*?)?,? "
SUBJECT_PREAMBLES = (
    (re.compile(r"^laying down (implementing technical standards) for the application of "
                + LEVEL1_REFERENCE + r"(with regard to|as regards) "), r"\1 \2 "),
    (re.compile(r"^laying down (implementing technical standards) (with regard to|as regards) "), r"\1 \2 "),
    (re.compile(r"^(?:on )?(?:supplementing|laying down the rules for the application of) "
                + LEVEL1_REFERENCE + r"(?:with regard to|as regards|by) "), ""),
)

Change = namedtuple("Change", "kind regime celex act url detail")


def query(regimes=REGIMES):
    basics = " ".join(f'"{regime.celex}"^^xsd:string' for regime in regimes)
    types = " ".join(f"<{RESOURCE_TYPE}{code}>" for code in TYPES)
    return cellar.PREFIXES + f"""
SELECT ?basic_celex ?celex ?type ?eli ?in_force ?adopted ?end_of_validity ?title ?date ?date_type ?date_comment
WHERE {{
  VALUES ?basic_celex {{ {basics} }}
  VALUES ?type {{ {types} }}
  ?basic cdm:resource_legal_id_celex ?basic_celex .
  ?work cdm:resource_legal_based_on_resource_legal ?basic ;
        cdm:resource_legal_id_celex ?celex ;
        cdm:work_has_resource-type ?type .
  OPTIONAL {{ ?work cdm:resource_legal_eli ?eli }}
  OPTIONAL {{ ?work cdm:resource_legal_in-force ?in_force }}
  OPTIONAL {{ ?work cdm:work_date_document ?adopted }}
  OPTIONAL {{ ?work cdm:resource_legal_date_end-of-validity ?end_of_validity }}
  OPTIONAL {{
    ?expression cdm:expression_belongs_to_work ?work ;
                cdm:expression_uses_language <http://publications.europa.eu/resource/authority/language/ENG> ;
                cdm:expression_title ?title .
  }}
  OPTIONAL {{
{cellar.DATES_PATTERN}
  }}
}}
"""


def parse(rows, regimes=REGIMES):
    """Fold CELLAR's one-row-per-date results into one CSV row per regime and act."""
    names = {regime.celex: regime.name for regime in regimes}
    acts = {}
    for row in rows:
        act = acts.setdefault((names[row["basic_celex"]], row["celex"]), {"dates": {}})
        for field in ("type", "eli", "in_force", "adopted", "end_of_validity", "title"):
            if row.get(field):
                act.setdefault(field, set()).add(row[field])
        if row.get("date"):
            kind = cellar.date_kind(row.get("date_type"), row.get("date_comment"))
            act["dates"].setdefault(kind, set()).add(row["date"])
    return sort_rows(record(regime, celex, act) for (regime, celex), act in acts.items())


def record(regime, celex, act):
    def first(field):  # CELLAR should return one value; pick the same one every run if not
        return min(act.get(field, {""}))

    dates = act["dates"]
    entry = dates.get("EV") or dates.get("")  # one act has its only date unannotated
    flags = {cellar.boolean(value) for value in act.get("in_force", ())}
    title = " ".join(first("title").split())
    end = first("end_of_validity")
    return {
        "regime": regime,
        "celex": celex,
        "act": citation(title, first("type"), celex),
        "title": title,
        "adopted": first("adopted"),
        "entry_into_force": min(entry) if entry else "",
        "applies_from": "; ".join(sorted(dates.get("MA", ()))),
        "applies_in_part_from": "; ".join(sorted(dates.get("MA/PART", ()))),
        "in_force": flags.pop() if len(flags) == 1 else "",
        "end_of_validity": "" if end == "9999-12-31" else end,
        "eli": first("eli"),
    }


def citation(title, type_uri, celex):
    """'Delegated Regulation (EU) 2025/1264', from the official title where it has one."""
    if match := CITATION.match(title):
        return match[1]
    parts = cellar.CELEX.match(celex)
    return f"{TYPES[type_uri.rsplit('/', 1)[-1]]} (EU) {parts['year']}/{int(parts['number'])}"


def sort_rows(rows):
    order = {regime.name: index for index, regime in enumerate(REGIMES)}

    def key(row):
        parts = cellar.CELEX.match(row["celex"])
        year, number = (int(parts["year"]), int(parts["number"])) if parts else (0, 0)
        return order.get(row["regime"], len(order)), year, number, row["celex"]

    return sorted(rows, key=key)


def read_csv(path=CSV_PATH):
    """The rows, and the names of any columns that did not come from CELLAR."""
    with open(path, newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        rows = list(reader)
    return rows, [column for column in reader.fieldnames or [] if column not in COLUMNS]


def to_csv(rows, extra=()):
    out = io.StringIO()
    writer = csv.DictWriter(out, fieldnames=COLUMNS + list(extra), lineterminator="\n", extrasaction="ignore")
    writer.writeheader()
    writer.writerows(rows)
    return out.getvalue()


def merge(fetched, existing, extra):
    """CELLAR's columns from `fetched`, hand-added columns from `existing`."""
    kept = {(row["regime"], row["celex"]): row for row in existing}
    return [{**row, **{column: kept.get((row["regime"], row["celex"]), {}).get(column, "") for column in extra}}
            for row in fetched]


def guard(fetched, existing):
    """Refuse to treat an empty CELLAR answer as every act having disappeared."""
    for regime in REGIMES:
        had = any(row["regime"] == regime.name for row in existing)
        if had and not any(row["regime"] == regime.name for row in fetched):
            raise SystemExit(f"CELLAR returned no acts for {regime.name}; not trusting that answer.")


def compare(old, new):
    """What `new` (CELLAR now) says differently from `old` (the CSV), CELLAR's columns only."""
    before = {(row["regime"], row["celex"]): row for row in old}
    after = {(row["regime"], row["celex"]): row for row in new}
    changes = []
    for key in after.keys() - before.keys():
        row = after[key]
        detail = f"adopted {row['adopted']}, in force from {row['entry_into_force']}, in force: {row['in_force']}"
        changes.append(Change("new", *key, row["act"], eurlex(row), detail))
    for key in before.keys() - after.keys():
        row = before[key]
        changes.append(Change("removed", *key, row["act"], eurlex(row), "no longer returned by CELLAR"))
    for key in before.keys() & after.keys():
        old_row, new_row = before[key], after[key]
        fields = [column for column in COLUMNS if old_row.get(column, "") != new_row.get(column, "")]
        if "in_force" in fields:
            detail = f"in force: {old_row['in_force'] or '(empty)'} -> {new_row['in_force'] or '(empty)'}"
            changes.append(Change("in_force", *key, new_row["act"], eurlex(new_row), detail))
        if others := [field for field in fields if field != "in_force"]:
            detail = "; ".join(f"{field}: {old_row.get(field) or '(empty)'} -> {new_row.get(field) or '(empty)'}"
                               for field in others)
            changes.append(Change("changed", *key, new_row["act"], eurlex(new_row), detail))
    kinds = ["new", "in_force", "changed", "removed"]
    order = {regime.name: index for index, regime in enumerate(REGIMES)}
    return sorted(changes, key=lambda change: (kinds.index(change.kind), order.get(change.regime, 99), change.celex))


def report(changes, today):
    """The body of the level2-update issue."""
    lines = [f"CELLAR, the EU Publications Office's metadata service, no longer matches "
             f"`data/level2.csv` (weekly check, {today}).", ""]
    for kind, heading in (("new", "New acts"), ("in_force", "In-force flag changed"),
                          ("changed", "Other changes"), ("removed", "No longer returned by CELLAR")):
        items = [change for change in changes if change.kind == kind]
        if items:
            lines += [f"### {heading} ({len(items)})", ""]
            lines += [f"- {c.regime}: [{c.act}]({c.url}) (`{c.celex}`): {c.detail}" for c in items]
            lines.append("")
    lines.append("To update: run `python scripts/level2.py update`, review the diff of `data/level2.csv`, "
                 "and open a pull request that closes this issue. Until then, the weekly check rewrites "
                 "this issue's body.")
    return "\n".join(lines) + "\n"


def eurlex(row):
    if match := re.match(r"^https?://data\.europa\.eu/eli/(.+)$", row.get("eli", "")):
        return f"https://eur-lex.europa.eu/eli/{match[1]}"
    return f"https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:{row['celex']}"


def subject(title):
    """The official title without the act's own citation and the 'supplementing ...' preamble."""
    text = SUBJECT_PREFIX.sub("", EEA_RELEVANCE.sub("", title), count=1)
    for pattern, replacement in SUBJECT_PREAMBLES:
        if pattern.match(text):
            text = pattern.sub(replacement, text, count=1)
            break
    text = text.rstrip(" .")
    return text[:1].upper() + text[1:]


def anchor(heading):
    return re.sub(r"[^\w\- ]", "", heading.strip().lower()).replace(" ", "-")


def cell(text):
    return text.replace("|", r"\|")


def applies(row):
    dates = [(date, "") for date in row["applies_from"].split("; ") if date]
    dates += [(date, " (in part)") for date in row["applies_in_part_from"].split("; ") if date]
    return "; ".join(f"{date}{suffix}" for date, suffix in sorted(dates)) or "–"


def render_docs(rows, checked):
    lines = [
        "# Level 2 tracker",
        "",
        "Delegated and implementing acts the Commission has adopted under the five Level 1 acts this list "
        "covers, as recorded by [CELLAR](https://op.europa.eu/en/web/cellar), the EU Publications Office's "
        "metadata service. An act is listed under a Level 1 act when CELLAR records it as based on that act.",
        "",
        "Generated by [`scripts/level2.py`](../scripts/level2.py) from [`data/level2.csv`](../data/level2.csv); "
        "edit the CSV, not this page. Nothing here is legal advice: the Official Journal texts on EUR-Lex prevail.",
        "",
        f"Checked against CELLAR on {cellar.long_date(checked)}.",
        "",
        "| Level 1 act | In force | No longer in force |",
        "|---|--:|--:|",
    ]
    for regime in REGIMES:
        acts = [row for row in rows if row["regime"] == regime.name]
        current = sum(row["in_force"] == "true" for row in acts)
        lines.append(f"| [{regime.name}](#{anchor(regime.name)}), {regime.citation} | {current} | {len(acts) - current} |")
    lines += [
        "",
        "*Adopted* is the date of the act and *in force from* its date of entry into force. *Applies from* lists "
        "the later dates of application CELLAR records, marked *in part* where only some provisions apply from "
        "that date; a dash means CELLAR records no separate date. Not included: drafts, ESA final reports, "
        "guidelines and Q&As (Level 3), and Official Journal corrigenda.",
    ]
    for regime in REGIMES:
        acts = [row for row in rows if row["regime"] == regime.name]
        current = [row for row in acts if row["in_force"] == "true"]
        former = [row for row in acts if row["in_force"] != "true"]
        level1 = f"https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:{regime.celex}"
        intro = f"Level 1 act: [{regime.citation}]({level1}). In force: {len(current)}."
        lines += ["", f"## {regime.name}", "", " ".join([intro, NOTES.get(regime.name, "")]).strip()]
        if current:
            lines += ["", "| Act | Subject (from the official title) | Adopted | In force from | Applies from |",
                      "|---|---|---|---|---|"]
            lines += [f"| [{row['act']}]({eurlex(row)}) | {cell(subject(row['title']))} | {row['adopted']} "
                      f"| {row['entry_into_force']} | {applies(row)} |" for row in current]
        if former:
            lines += ["", "No longer in force:", "",
                      "| Act | Subject (from the official title) | Adopted | In force from | End of validity |",
                      "|---|---|---|---|---|"]
            lines += [f"| [{row['act']}]({eurlex(row)}) | {cell(subject(row['title']))} | {row['adopted']} "
                      f"| {row['entry_into_force']} | {row['end_of_validity'] or '–'} |" for row in former]
    return "\n".join(lines) + "\n"


def render_status(rows, pending, checked):
    counts = [f"[{regime.name} {sum(row['regime'] == regime.name and row['in_force'] == 'true' for row in rows)}]"
              f"(docs/level2.md#{anchor(regime.name)})" for regime in REGIMES]
    if pending:
        waiting = f"{pending} {'measure' if pending == 1 else 'measures'} submitted but not yet adopted, " \
                  "listed under Level 2 measures"
    else:
        waiting = "none listed"
    return (f"**Status at a glance**, checked against official EU metadata (CELLAR) on {cellar.long_date(checked)}: "
            f"Level 2 acts in force under {', '.join(counts[:-1])} and {counts[-1]}. Pending: {waiting}.")


def level2_section(readme):
    lines = readme.splitlines()
    start = lines.index("## Level 2 measures")
    end = next((i for i in range(start + 1, len(lines)) if lines[i].startswith("## ")), len(lines))
    return lines[start + 1:end]


def pending_count(readme):
    return sum(1 for line in level2_section(readme) if line.startswith("- [") and PENDING.search(line))


def replace_status(readme, status):
    block = re.compile(re.escape(STATUS_START) + r".*?" + re.escape(STATUS_END), re.S)
    if not block.search(readme):
        raise SystemExit(f"README.md has no {STATUS_START} ... {STATUS_END} block")
    return block.sub(lambda _: f"{STATUS_START}\n{status}\n{STATUS_END}", readme, count=1)


def checked_date(docs):
    match = CHECKED.search(docs)
    return cellar.iso_date(match["date"]) if match else None


def pages(rows, checked, readme):
    """docs/level2.md and README.md as they should read for these rows."""
    status = render_status(rows, pending_count(readme), checked)
    return render_docs(rows, checked), replace_status(readme, status)


def fetch():
    return parse(cellar.select(query()))


def main(argv=None):
    parser = argparse.ArgumentParser(description="Level 2 tracker built from CELLAR metadata.")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("update", help="query CELLAR, rewrite data/level2.csv and re-render both pages")
    commands.add_parser("render", help="re-render docs/level2.md and the README status line from the CSV")
    commands.add_parser("check", help="exit 1 if docs/level2.md or the README status line is out of date")
    diff = commands.add_parser("diff", help="compare CELLAR with data/level2.csv")
    diff.add_argument("--report", type=Path, help="write the issue body here if they differ, else delete it")
    args = parser.parse_args(argv)
    today = datetime.date.today().isoformat()
    readme = README_PATH.read_text(encoding="utf-8")

    if args.command == "update":
        existing, extra = read_csv() if CSV_PATH.exists() else ([], [])
        fetched = fetch()
        guard(fetched, existing)
        rows = merge(fetched, existing, extra)
        for change in compare(existing, rows):
            print(f"{change.kind}: {change.regime} {change.act}: {change.detail}")
        CSV_PATH.parent.mkdir(exist_ok=True)
        CSV_PATH.write_text(to_csv(rows, extra), encoding="utf-8")
        docs, readme = pages(rows, today, readme)
        DOCS_PATH.write_text(docs, encoding="utf-8")
        README_PATH.write_text(readme, encoding="utf-8")
        for regime in REGIMES:
            print(f"{regime.name}: {sum(row['regime'] == regime.name for row in rows)} acts")
        return 0

    rows, _ = read_csv()
    checked = (checked_date(DOCS_PATH.read_text(encoding="utf-8")) if DOCS_PATH.exists() else None) or today

    if args.command == "render":
        docs, readme = pages(rows, checked, readme)
        DOCS_PATH.write_text(docs, encoding="utf-8")
        README_PATH.write_text(readme, encoding="utf-8")
        return 0

    if args.command == "check":
        docs, expected = pages(rows, checked, readme)
        stale = [path.name for path, text in ((DOCS_PATH, docs), (README_PATH, expected))
                 if not path.exists() or path.read_text(encoding="utf-8") != text]
        if stale:
            print(f"Out of date: {', '.join(stale)}. Run: python scripts/level2.py render", file=sys.stderr)
            return 1
        return 0

    fetched = fetch()
    guard(fetched, rows)
    changes = compare(rows, fetched)
    for change in changes:
        print(f"{change.kind}: {change.regime} {change.act}: {change.detail}")
    print(f"{len(changes)} difference(s) between CELLAR and data/level2.csv")
    if args.report:
        if changes:
            args.report.write_text(report(changes, today), encoding="utf-8")
        else:
            args.report.unlink(missing_ok=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
