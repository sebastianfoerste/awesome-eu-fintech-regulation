# How this list is curated and checked

Detail moved out of the README. Nothing here is legal advice.

## Inclusion rules

Taken from [CONTRIBUTING.md](../CONTRIBUTING.md). An entry qualifies if it is one of:

- an EU legislative text or official Level 2/3 measure;
- a regulator page or register;
- a genuinely open-source tool (OSI license, public repo, runs without a paid account);
- a free tracker or guide of lasting value.

Primary sources win over commentary. Blog posts and law-firm client alerts are out of scope. Entries can be removed when they go stale, get archived, or turn into a sales funnel.

## Self-promotion

The list's maintainer also maintains four of the linked tools. They sit in their own section, "Maintained by the curator", with a disclosure line, and meet the same maturity rule as every other tool. A test checks that the number in that line matches the number of entries.

## Level 2 tracker

[`level2.md`](level2.md) lists every delegated and implementing act CELLAR, the EU Publications Office's metadata service, records as based on one of the five Level 1 acts. `scripts/level2.py` keeps it in [`data/level2.csv`](../data/level2.csv) (CELEX number, citation, official title, date of the act, entry into force, dates of application, in-force flag, end of validity, ELI) and renders the tracker page and the README status line from that file:

```bash
python scripts/level2.py update   # query CELLAR, rewrite the CSV, re-render both pages
python scripts/level2.py render   # re-render after editing the CSV by hand
python scripts/level2.py check    # offline: exit 1 if a page no longer matches the CSV
python scripts/level2.py diff     # list what CELLAR now says differently from the CSV
```

Columns added to the CSV by hand, such as a note on what an act fixes, survive `update`. The annotated entries under "Level 2 measures" in the README stay hand-written.

## Automated checks

| Check | Workflow | When | Needs network |
|---|---|---|---|
| Link check (lychee, settings in `lychee.toml`) on `README.md`, `CONTRIBUTING.md` and `docs/`; 403 and 429 are accepted because regulator sites bot-wall clients, genuine 404s fail. EUR-Lex is excluded and 202 is not accepted: EUR-Lex answers bots with an empty 202 page, so a pass there proves nothing | `.github/workflows/link-check.yml` | weekly (Mondays 06:00 UTC) and manual | yes |
| CELEX check (`scripts/verify_celex.py`): every EUR-Lex entry in the README exists in CELLAR, cites the act it links, is in force, and its "Adopted …, in force …" dates match CELLAR | `.github/workflows/link-check.yml` | weekly and manual | yes |
| Level 2 watch (`scripts/level2.py diff`): opens or updates its own issue labelled `level2-update`, leaving alone the reports people file under that label through the issue form, when CELLAR records a new act under the five Level 1 acts, an in-force flag changes, or other dates or titles change | `.github/workflows/level2-watch.yml` | weekly (Mondays 07:00 UTC) and manual | yes |
| [awesome-lint](https://github.com/sindresorhus/awesome-lint) on `README.md` | `.github/workflows/awesome-lint.yml` | pull requests and pushes to `main` | yes (installs awesome-lint) |
| Offline tests (`tests/`): entry format, no duplicate links, contents anchors match headings, Contents first, alphabetical sections, Level 2 status wording and dates, no placeholders, disclosure count; the CSV is well formed and the tracker page and README status line match it; the CELLAR parsing and diffing logic on fixed answers; the link check does not accept 202 and skips EUR-Lex; the Level 2 watch rewrites only its own issue; community files present | `.github/workflows/tests.yml` | pull requests and pushes to `main` | no |

Run the offline tests locally:

```bash
pip install pytest
python -m pytest -q
```

## Query the list from the shell

The list is CC0 and needs no install. To print the annotated Level 2 entries and their status lines:

```bash
git clone https://github.com/sebastianfoerste/awesome-eu-fintech-regulation
cd awesome-eu-fintech-regulation
sed -n '/^## Level 2 measures/,/^## Legislation/p' README.md | grep -oE '^- \[[^]]*\]|(Adopted|Submitted) [^;]*(;[^;]*)*\.$' | sed 's/^- //'
```

Output on the current README:

```text
[Delegated Regulation (EU) 2025/1264]
Adopted 27 June 2025, in force 23 October 2025.
[EBA final report EBA/RTS/2024/10]
Submitted 13 June 2024; the Commission proposed amendments on 28 August 2025; not yet adopted.
[EBA asset-referenced and e-money token page]
```

The whole tracker is in `data/level2.csv`, for example `grep '^DORA,' data/level2.csv`.

## Caveats

- The annotated Level 2 entries in the README are hand-maintained. Their CELEX numbers and dates are checked against CELLAR every week, but drafts and ESA reports are not in CELLAR: check the linked primary source before relying on them.
- The tracker reports what CELLAR records. It says nothing about what an act means; the Official Journal texts on EUR-Lex prevail.
- The list covers a short set of regimes (MiCAR, DORA, MiFID II, PSD2, AI Act in financial services). Missing regimes are gaps, not exclusions.
