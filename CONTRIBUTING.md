# Contributing

Add one entry per pull request.

An entry qualifies if it is one of: an EU legislative text or official Level 2/3 measure, a regulator page or register, a genuinely open-source tool (OSI license, public repo, runs without a paid account), or a free tracker/guide of lasting value.

Format: `- [Name](url) - One sentence, ending with a period.`

## Where an entry goes

Keep the section order of the Contents. Within a section:

- **Level 2 measures:** adopted acts first, then drafts and proposals, then status pages.
- **Legislation (Level 1):** the fixed regime order MiCAR, DORA, MiFID II, PSD2, AI Act.
- **Regulators and registers:** EU supervisory authorities (ESMA, EBA, EIOPA), then national authorities by country name, then the European Commission.
- **All other sections:** alphabetical by name, ignoring case. A test checks this.

## Level 2 status lines

Level 2 entries end with a dated status line in one of these forms, with dates written as `27 June 2025`:

- Adopted act: `Adopted <date of the act>, in force <date of entry into force>.` If the act applies from a later date, add `, applies from <date>` before the period.
- Draft or proposal: `Submitted <date>; <what has happened since, with its date>; not yet adopted.`
- Status pages carry no status line; they are dated at the source.

Tests check the wording. The weekly link check compares the dates of adopted acts with the EU Publications Office's metadata (CELLAR). Don't edit `docs/level2.md` by hand: it is generated from `data/level2.csv` by `python scripts/level2.py`. To annotate an act there, fill in an `article` or `what_it_fixes` column in the CSV; [docs/curation.md](docs/curation.md#level-2-tracker) explains how.

## Open-source tools

A tool qualifies if its repository is public, has an OSI-approved license and a README that says what it does and how to run it, is not archived, is at least 30 days old and has had a commit in the last 12 months. The same rule applies to the curator's own tools.

## Hard rules

- Working link (no redirects to marketing pages, no paywalls).
- Primary sources over commentary. Blog posts and law-firm client alerts are out of scope.
- If you maintain the linked project, say so in the PR description.
- Entries can be removed when they go stale, get archived, or turn into a sales funnel.

Run the offline checks before opening a pull request: `pip install pytest && python -m pytest -q`. Participation is governed by the [Code of Conduct](CODE_OF_CONDUCT.md).
