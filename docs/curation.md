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

The list's maintainer also maintains four of the linked tools. They sit in their own section, "Maintained by the curator", with a disclosure line. A test checks that the number in that line matches the number of entries.

## Automated checks

| Check | Workflow | When | Needs network |
|---|---|---|---|
| Link check (lychee) on `README.md`; 403 and 429 are accepted because regulator sites bot-wall clients, genuine 404s fail | `.github/workflows/link-check.yml` | weekly (Mondays 06:00 UTC) and manual | yes |
| Offline structural tests (`tests/test_readme.py`): entry format, no duplicate links, contents anchors match headings, disclosure count matches | `.github/workflows/tests.yml` | pull requests and pushes to `main` | no |

Run the offline tests locally:

```bash
pip install pytest
python -m pytest -q
```

## Caveats

- Level 2 status lines are hand-maintained and dated; check the linked primary source before relying on them.
- The list covers a short set of regimes (MiCAR, DORA, MiFID II, PSD2, AI Act in financial services). Missing regimes are gaps, not exclusions.
