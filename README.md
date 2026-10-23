# Awesome EU Fintech Regulation [![Awesome](https://awesome.re/badge.svg)](https://awesome.re)

> Primary sources for EU fintech regulation, with a dated Level 2 tracker: MiCAR, DORA, MiFID II, PSD2 and the AI Act in financial services.

<!-- level2-status:start -->
**Status at a glance**, checked against official EU metadata (CELLAR) on 15 October 2026: Level 2 acts in force under [MiCAR 37](docs/level2.md#micar), [DORA 12](docs/level2.md#dora), [MiFID II 50](docs/level2.md#mifid-ii), [PSD2 9](docs/level2.md#psd2) and [AI Act 2](docs/level2.md#ai-act). Pending: 1 measure submitted but not yet adopted, listed under Level 2 measures.
<!-- level2-status:end -->

- **Primary sources only.** EUR-Lex texts, regulator pages and registers, not law-firm client alerts or vendor pages.
- **Level 2, dated.** A [tracker](docs/level2.md) of every delegated and implementing act under the five Level 1 acts, generated from the EU Publications Office's metadata, plus annotated entries for the measures that matter most and for drafts still in the pipeline.
- **Checked weekly.** CI checks every link, and every CELEX number and date against the official metadata; stale entries are removed. Offline tests run on every pull request.
- **Disclosed self-promotion.** The tools the curator maintains sit in their own labelled section.

Maintained by a practicing EU financial-regulation lawyer. Nothing here is legal advice. How the list is curated and checked: [docs/curation.md](docs/curation.md).

## Contents

- [Level 2 measures](#level-2-measures)
- [Legislation (Level 1)](#legislation-level-1)
- [Regulators and registers](#regulators-and-registers)
- [Guides and trackers](#guides-and-trackers)
- [Open-source tools](#open-source-tools)
- [Related lists](#related-lists)

## Level 2 measures

Delegated and implementing acts, and the drafts still in the pipeline. Level 1 tells you the obligation exists; Level 2 tells you the number. The tracker linked above lists every adopted act with its dates; the entries below are annotated by hand.

- [Delegated Regulation (EU) 2025/1264](https://eur-lex.europa.eu/eli/reg_del/2025/1264/oj) - RTS on the minimum contents of the liquidity management policy and procedures for issuers of significant ARTs and EMTs, and for other issuers where their competent authority requires it, under Art. 45(7), first subparagraph, point (b) MiCAR. Adopted 27 June 2025, in force 23 October 2025.
- [EBA final report EBA/RTS/2024/10](https://www.eba.europa.eu/sites/default/files/2024-06/580db2f3-8370-4927-baa3-0f995722b417/Final%20report_draft%20RTS%20further%20specifying%20the%20liquidity%20requirements%20Article%2036%204.pdf) - Draft RTS on the liquidity requirements of the reserve of assets under Art. 36(4) and Art. 45(7)(b) MiCAR, including the deposit minimums. Submitted 13 June 2024; the Commission proposed amendments on 28 August 2025; not yet adopted.
- [EBA asset-referenced and e-money token page](https://www.eba.europa.eu/regulation-and-policy/asset-referenced-and-e-money-tokens-mica) - Status tracker for every MiCAR technical standard EBA owns, including the EBA's 10 October 2025 opinion on the Commission's proposed amendments to the Art. 36(4) RTS. Its press release also carries the companion opinion on the HLFI RTS.

## Legislation (Level 1)

Official Journal texts on EUR-Lex. Later amendments appear in the consolidated versions.

- [MiCAR — Regulation (EU) 2023/1114](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32023R1114) - Markets in crypto-assets: whitepaper duties, ART/EMT regimes, CASP authorization.
- [DORA — Regulation (EU) 2022/2554](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32022R2554) - Digital operational resilience: ICT risk, third-party registers, incident reporting.
- [MiFID II — Directive 2014/65/EU](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32014L0065) - Markets in financial instruments; the boundary question for every token classification.
- [PSD2 — Directive (EU) 2015/2366](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32015L2366) - Payment services; still the operative regime pending PSD3/PSR.
- [AI Act — Regulation (EU) 2024/1689](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32024R1689) - Horizontal AI rules; Annex III point 5(b) and (c) catch credit scoring of natural persons and risk assessment and pricing in life and health insurance.

## Regulators and registers

- [ESMA — MiCA hub](https://www.esma.europa.eu/esmas-activities/digital-finance-and-innovation/markets-crypto-assets-regulation-mica) - Level 2/3 measures, Q&As, and supervisory convergence work.
- [ESMA — interim MiCA register](https://www.esma.europa.eu/esmas-activities/digital-finance-and-innovation/markets-crypto-assets-regulation-mica#InterimMiCARegister) - CSV files of notified whitepapers, ART and EMT issuers, authorized CASPs and non-compliant entities (Arts. 109 and 110 MiCAR). The primary empirical dataset for MiCAR work; the curator's [micar-register-observatory](https://github.com/sebastianfoerste/micar-register-observatory#dashboard) diffs it weekly (disclosure: maintained by the author of this list).
- [ESMA — DORA page](https://www.esma.europa.eu/esmas-activities/digital-finance-and-innovation/digital-operational-resilience-act-dora) - Joint-ESA RTS/ITS work and oversight of critical ICT providers.
- [EBA — supervisory role under MiCA](https://www.eba.europa.eu/activities/direct-supervision-and-oversight/ebas-supervisory-role-under-mica) - Supervision of significant ARTs and EMTs, significance assessments and supervisory colleges.
- [EIOPA — DORA page](https://www.eiopa.europa.eu/digital-operational-resilience-act-dora_en) - Insurance-sector DORA implementation.
- [BaFin — crypto institutions](https://www.bafin.de/DE/unternehmen-maerkte/aufsicht/kryptoinstitute/kryptoinstitute_node) - German NCA practice: notification and reporting duties under the KMAG, whitepaper submission under Art. 8 MiCAR (German).
- [European Commission — digital finance](https://finance.ec.europa.eu/digital-finance_en) - Legislative pipeline: PSD3/PSR, FiDA, digital euro.

## Guides and trackers

- [EU AI Act Explorer](https://artificialintelligenceact.eu/) - Full-text navigation, obligation timelines, and implementation tracker (Future of Life Institute).
- [VASP Tracker](https://vasptracker.com/) - Free tracker of crypto-asset service provider licensing dates, including each EU/EEA state's MiCAR transitional-period end date, with every date linked to the national law, ESMA list or regulator notice.

## Open-source tools

- [AegisAI](https://github.com/SdSarthak/AegisAI) - Open-source AI governance, risk and compliance platform with EU AI Act coverage.
- [AI Act Implementation Tool](https://github.com/NGO-Algorithm-Audit/AI-Act-Implementation-Tool) - Risk classification of algorithmic systems via structured questionnaires (Algorithm Audit).
- [AI Assessment Tool](https://github.com/AI4Belgium/ai-assessment-tool) - ALTAI-based trustworthy-AI self-assessment tool (AI4Belgium).
- [Arelle](https://github.com/Arelle/Arelle) - XBRL platform used for ESEF and EBA supervisory-reporting filings.
- [Common Domain Model](https://github.com/finos/common-domain-model) - FINOS/ISDA model of financial products, trades and lifecycle events; the substrate for digital regulatory reporting.
- [EuConform](https://github.com/Hiepler/EuConform) - EU AI Act risk classification and bias testing tool.
- [EUDI Wallet ARF](https://github.com/eu-digital-identity-wallet/eudi-doc-architecture-and-reference-framework) - Architecture and reference framework for the European Digital Identity Wallet.
- [FIRE Data Standard](https://github.com/SuadeLabs/fire) - Suade Labs' open data standard for granular regulatory reporting.
- [Rune DSL](https://github.com/finos/rune-dsl) - DSL and code generators behind the Common Domain Model and digital regulatory reporting.
- [XS2A](https://github.com/adorsys/xs2a) - Open-source NextGenPSD2 XS2A access-to-account interface implementation.

### Maintained by the curator

Disclosure: these four are maintained by the author of this list.

- [eu-ai-act-classifier](https://github.com/sebastianfoerste/eu-ai-act-classifier) - Deterministic EU AI Act risk-tier classifier with cited obligations and review gates.
- [eu-reg-mcp](https://github.com/sebastianfoerste/eu-reg-mcp) - MCP server giving AI agents cited, review-gated grounding in EU regulation: ESMA MiCAR register search, change tracking, white paper linting, EU AI Act classification.
- [micar-register-observatory](https://github.com/sebastianfoerste/micar-register-observatory) - Living dashboard of the ESMA interim MiCAR register: weekly snapshots, entry diffs, withdrawal tracking, and white paper format coverage.
- [micar-whitepaper-linter](https://github.com/sebastianfoerste/micar-whitepaper-linter) - Deterministic MiCAR whitepaper linter with pinpoint citations, CI action, and a reproducible study over ESMA-register filings.

## Related lists

- [awesome-eu-ai-act](https://github.com/GenAI-Gurus/awesome-eu-ai-act) - Tools, official sources, and templates for EU AI Act compliance.
- [awesome-legal-nlp](https://github.com/maastrichtlawtech/awesome-legal-nlp) - LegalNLP datasets, models, and benchmarks.
- [awesome-legaltech](https://github.com/Vaquill-AI/awesome-legaltech) - Open-source platforms, models, and tools for the legal ecosystem.

## Contributing

Contributions welcome — see [CONTRIBUTING.md](CONTRIBUTING.md). Hard rules: primary sources over commentary, working links, no vendor marketing pages, self-promotion requires disclosure. Licensed CC0 (see [LICENSE](LICENSE)).

## Footnotes

This list is part of "EU regulation as code", a set of repos by [sebastianfoerste](https://github.com/sebastianfoerste). The ones on EU fintech regulation are listed under Maintained by the curator; these two are about legal work more generally:

- [contract-review-eval-harness](https://github.com/sebastianfoerste/contract-review-eval-harness) - Scores an AI contract review against lawyer-written answer sets: did it find the clauses, grade the risk correctly, quote real text and avoid inventing anything.
- [legal-function-operating-system](https://github.com/sebastianfoerste/legal-function-operating-system) - How an in-house legal team runs: intake, risk bands, routing, SLAs, approvals and a board-ready report, with a supervised agent behind review gates.
