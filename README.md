# Awesome EU Fintech Regulation [![Awesome](https://awesome.re/badge.svg)](https://awesome.re)

A curated list of primary sources, regulator resources, and open-source tools for EU financial regulation: MiCAR, DORA, MiFID II, PSD2, and the AI Act as it hits financial services.

Maintained by a practicing EU financial-regulation lawyer. Every link is checked before merge; entries that go stale get removed. Nothing here is legal advice.

## Contents

- [Legislation (Level 1)](#legislation-level-1)
- [Regulators and registers](#regulators-and-registers)
- [Guides and trackers](#guides-and-trackers)
- [Open-source tools](#open-source-tools)
- [Related lists](#related-lists)

## Legislation (Level 1)

Consolidated texts on EUR-Lex.

- [MiCAR — Regulation (EU) 2023/1114](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32023R1114) - Markets in crypto-assets: whitepaper duties, ART/EMT regimes, CASP authorization.
- [DORA — Regulation (EU) 2022/2554](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32022R2554) - Digital operational resilience: ICT risk, third-party registers, incident reporting.
- [MiFID II — Directive 2014/65/EU](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32014L0065) - Markets in financial instruments; the boundary question for every token classification.
- [PSD2 — Directive (EU) 2015/2366](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32015L2366) - Payment services; still the operative regime pending PSD3/PSR.
- [AI Act — Regulation (EU) 2024/1689](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32024R1689) - Horizontal AI rules; Annex III catches credit scoring and insurance pricing.

## Regulators and registers

- [ESMA — MiCA hub](https://www.esma.europa.eu/esmas-activities/digital-finance-and-innovation/markets-crypto-assets-regulation-mica) - Level 2/3 measures, Q&As, and supervisory convergence work.
- [ESMA — MiCA register](https://registers.esma.europa.eu/publication/searchRegister?core=esma_registers_mica) - Notified whitepapers, authorized CASPs and issuers. The primary empirical dataset for MiCAR work.
- [ESMA — DORA page](https://www.esma.europa.eu/esmas-activities/digital-finance-and-innovation/digital-operational-resilience-act-dora) - Joint-ESA RTS/ITS work and oversight of critical ICT providers.
- [EBA — markets in crypto-assets](https://www.eba.europa.eu/activities/direct-supervision-and-oversight/markets-crypto-assets) - ART/EMT supervision, significance assessments, own-funds guidance.
- [EIOPA — DORA page](https://www.eiopa.europa.eu/digital-operational-resilience-act-dora_en) - Insurance-sector DORA implementation.
- [BaFin — MiCAR portal](https://www.bafin.de/DE/Aufsicht/MiCAR/MiCAR_node.html) - German NCA practice: authorization procedure, national transition rules (German).
- [European Commission — digital finance](https://finance.ec.europa.eu/digital-finance_en) - Legislative pipeline: PSD3/PSR, FiDA, digital euro.

## Guides and trackers

- [EU AI Act Explorer](https://artificialintelligenceact.eu/) - Full-text navigation, obligation timelines, and implementation tracker (Future of Life Institute).

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

Disclosure: these six are maintained by the author of this list.

- [micar-whitepaper-linter](https://github.com/sebastianfoerste/micar-whitepaper-linter) - Deterministic MiCAR whitepaper linter with pinpoint citations, CI action, and a reproducible study over ESMA-register filings.
- [eu-ai-act-classifier](https://github.com/sebastianfoerste/eu-ai-act-classifier) - Deterministic EU AI Act risk-tier classifier with cited obligations and review gates.
- [dora-third-party-register-and-resilience-workbench](https://github.com/sebastianfoerste/dora-third-party-register-and-resilience-workbench) - DORA ICT third-party register and resilience governance workbench with audit exports.
- [eu-financial-reg-horizon-scanner](https://github.com/sebastianfoerste/eu-financial-reg-horizon-scanner) - Review-gated horizon scanner for EU financial regulation with proof packets and citations.
- [contract-review-eval-harness](https://github.com/sebastianfoerste/contract-review-eval-harness) - Evaluation harness for legal AI contract review: clause scoring, citation grounding, unsupported-citation counts and an adversarial minimal-pair campaign across NDA, SaaS and Art. 28 GDPR data processing agreements.
- [legal-function-operating-system](https://github.com/sebastianfoerste/legal-function-operating-system) - Deterministic legal function operating model for intake, risk, routing, SLAs, approvals and board reporting, with a versioned control contract between the operating model and its supervised agent.

## Related lists

- [awesome-eu-ai-act](https://github.com/GenAI-Gurus/awesome-eu-ai-act) - Tools, official sources, and templates for EU AI Act compliance.
- [awesome-legal-nlp](https://github.com/maastrichtlawtech/awesome-legal-nlp) - LegalNLP datasets, models, and benchmarks.
- [awesome-legaltech](https://github.com/Vaquill-AI/awesome-legaltech) - Open-source platforms, models, and tools for the legal ecosystem.

## Contributing

Contributions welcome — see [CONTRIBUTING.md](CONTRIBUTING.md). Hard rules: primary sources over commentary, working links, no vendor marketing pages, self-promotion requires disclosure.
