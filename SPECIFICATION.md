# Clinical Information System — Master Specification

**Status:** Draft · **Version:** 0.6 · **Date:** 2026-10-28

Start here for product direction and scope; use the document map for detailed requirements and definitions.

## Product direction

**Adopted direction:** A comprehensive open-source clinical information system across care settings and countries, with a shared clinical foundation, selectable modules, jurisdiction profiles, and controlled local configuration. Sweden is the first target.

Map the full product scope from the start; build it in working increments. Implementation order does not limit the ambition. The [coverage map](docs/coverage.md) records domains and gaps; depth, module boundaries, and build-versus-integrate choices develop with the workflows. National conventions belong in jurisdiction profiles unless justified as general requirements.

### Requirement categories

- **Core** — generally applicable healthcare capability.
- **Care-setting-specific** — needed for a particular care environment.
- **Jurisdiction-specific** — required by national or regional rules, infrastructure, or practice.
- **Deployment-specific** — required by an organization or installation.

Categories may overlap. They describe applicability, not release priority or mandatory module dependencies.

### Specification level

Specify workflows, information needs, constraints, and verification criteria. Keep broad coverage concise; develop detailed behavior alongside implementation. Defer data models, APIs, further technology choices, and deployment topology until workflow requirements constrain them. The adopted [development approach](#development-approach) is the exception.

### Modularity and configuration direction

| Mechanism | Responsibility |
|---|---|
| Shared clinical foundation | Common clinical meaning, identity, provenance, access, history, and safety guarantees. |
| Capability modules | Selectable clinical or administrative workflows with declared dependencies. |
| Care-setting profiles | Capabilities and workflow constraints for a care environment. |
| Jurisdiction profiles | National or regional rules, terminology, and infrastructure requirements. |
| Deployment configuration | Permitted organizational choices: teams, templates, routing, and roles. |
| Localization | Language, formats, and presentation that preserve clinical meaning. |

Boundaries remain open. Modules may depend on one another; separate deployment is not required. Profiles may require extensions, integrations, or operational procedures beyond settings. New jurisdictions should use maintained modules and profiles without country-specific product forks. Configuration constraints are specified in [ADM-005](docs/platform-requirements.md#adm-005--configuration-boundaries) and [MOD-004](docs/platform-requirements.md#mod-004--configuration-scope-and-conflicts).

### Interaction surfaces

**Adopted direction:** People use the product through a graphical client and through AI assistants acting on their behalf. Every action and every read of patient information is defined once, in one action interface that enforces authorization, workflow rules, and audit. The graphical client and assistants are both clients of it, with no privileges or rules of their own. An assistant acts only for an identified person, sees no more than that person may, and prepares consequential actions for the person to confirm. Requirements: [SUR and AGT](docs/platform-requirements.md#user-surfaces-and-assistants).

This constrains the technology decisions without making them; the interface's form and protocol remain open.

### Development approach

**Adopted direction:**

| Decision | Choice |
|---|---|
| Backend language | C#; all backend code. |
| Backend framework | ASP.NET Core. |
| Data access | Dapper. |
| Frontend | Svelte, using TypeScript. |
| Frontend framework | SvelteKit. |
| Database | PostgreSQL. |
| Backend tests | NUnit. |
| Frontend tests | Vitest. |
| Record model | openEHR, targeting the current releases, with ADL 2 and full AQL 1.1.0 built slice by slice. The project implements its own openEHR repository instead of running EHRbase. |
| Record model validation | A harness that systematically validates the openEHR implementation. Its [proposed design](docs/openehr-validation.md) is not yet adopted. |
| Architecture | Clean architecture. |
| Design | Object orientation and domain-driven design. |
| Testing | Test-driven development. |
| Delivery | Vertical slices. |

Everything else about the stack and process remains open under [Q-DEV](docs/decisions.md#development).

### Development and verification

Development proceeds without a customer acceptance or procurement process and without practitioner dogfooding. Workflows are grounded in published sources: regulations, regional routines, laboratory and service instructions, reported incidents, and studies. Each workflow records its evidence and is verified against scenarios built from it, using synthetic patients, as described in [Assurance](docs/assurance.md#scenario-based-verification). Where sources disagree or are silent, the workflow states the assumption it makes.

Testable behavior, clinical safety, privacy, and deployment-specific obligations remain part of quality. Assess readiness for actual care separately from development verification, for each supported setting and jurisdiction.

Compare selected assumptions with a second jurisdiction before claiming generality. That comparison does not commit the first release to another country; selection remains open under [JUR-Q01](docs/platform-requirements.md#jurisdiction-profiles).

## Scope and document map

The master owns product direction, scope, and specification rules. The documents below own detailed definitions and requirement statements. Their requirement statuses still apply.

| Supporting document | Authoritative content |
|---|---|
| [Coverage map](docs/coverage.md) | Product breadth, care-setting variations, and gaps awaiting detailed requirements. |
| [Foundational design exploration](docs/foundational-design.md) | Proposed ownership, information lifecycle, and module boundaries; exploratory, not adopted architecture. |
| [Clinical requirements](docs/clinical-requirements.md) | Patient identity, encounters, records, clinical workflows, consent, patient participation, information semantics, and summaries. |
| [Platform requirements](docs/platform-requirements.md) | Integration, access, audit, user surfaces and assistants, configuration, modules, quality requirements, and jurisdiction-profile mechanisms. |
| [Laboratory result loop](docs/workflow-laboratory-results.md) | First end-to-end workflow slice: states, draft rules, failure cases, and Swedish practice evidence. |
| [Laboratory result scenarios](docs/scenarios-laboratory-results.md) | Research-grounded acceptance scenarios for the laboratory result loop. |
| [Assurance](docs/assurance.md) | Regulation, clinical safety, verification, and migration requirements. |
| [openEHR validation harness](docs/openehr-validation.md) | How the project's openEHR implementation is validated: required by the development approach; design proposed. |
| [Verification references](docs/verification-references.md) | Pinned external contracts and their use in prototype cases; informative, not adopted implementation choices. |
| [Prototype findings](docs/prototype-findings.md) | Observed repository checks, failures, and evidence limits; not completed clinical workflow verification. |
| [Sweden profile](docs/sweden.md) | Swedish applicability questions, infrastructure, and reference sources. |
| [Terminology and actors](docs/terminology.md) | Shared definitions and candidate users. |
| [Decision index](docs/decisions.md) | Cross-domain choices and links to domain questions. |

Broad domain coverage is adopted. Implementation order, detailed workflows, module boundaries, integration responsibilities, and deployment readiness remain open. A mapped area is not yet a specified or implemented capability.

## Goals

Enable authorized users to document, find, and use patient information safely. Detailed obligations belong to the referenced requirements.

| Goal | Requirements |
|---|---|
| Reduce clinical error and cognitive burden. | [SAFE-001](docs/assurance.md#safe-001--clinical-risk-analysis)–[SAFE-006](docs/assurance.md#safe-006--configuration-safety), [SUR-001](docs/platform-requirements.md#sur-001--single-action-interface)–[SUR-003](docs/platform-requirements.md#sur-003--patient-identity-re-verification), [NFR-UX-001](docs/platform-requirements.md#nfr-ux-001--clinical-efficiency)–[NFR-UX-005](docs/platform-requirements.md#nfr-ux-005--supported-device-classes) |
| Preserve meaning, context, uncertainty, and history across care boundaries. | [INF-001](docs/clinical-requirements.md#inf-001--stable-identity-of-clinically-significant-information)–[INF-009](docs/clinical-requirements.md#inf-009--information-status), [INT-003](docs/platform-requirements.md#int-003--semantic-preservation), [WF-005](docs/clinical-requirements.md#wf-005--handover) |
| Make clinical actions, changes, and access attributable, including actions prepared by assistants. | [AGT-001](docs/platform-requirements.md#agt-001--delegated-identity)–[AGT-004](docs/platform-requirements.md#agt-004--provenance-of-generated-content), [DOC-007](docs/clinical-requirements.md#doc-007--correction-and-amendment)–[DOC-008](docs/clinical-requirements.md#doc-008--change-history), [IAM-002](docs/platform-requirements.md#iam-002--individual-accountability), [AUD-001](docs/platform-requirements.md#aud-001--patient-information-access-logging)–[AUD-006](docs/platform-requirements.md#aud-006--administrative-and-configuration-audit) |
| Enforce access according to purpose and care context. | [IAM-003](docs/platform-requirements.md#iam-003--need-based-access)–[IAM-004](docs/platform-requirements.md#iam-004--context-sensitive-authorization), [CON-001](docs/clinical-requirements.md#con-001--consent)–[CON-004](docs/clinical-requirements.md#con-004--cross-organizational-information-exchange) |
| Exchange structured information without unnecessary proprietary dependency. | [DOC-002](docs/clinical-requirements.md#doc-002--narrative-and-structured-documentation), [CLI-010](docs/clinical-requirements.md#cli-010--clinical-terminology-and-coding), [INT-001](docs/platform-requirements.md#int-001--external-interfaces)–[INT-005](docs/platform-requirements.md#int-005--provenance-of-imported-information) |
| Adapt modules, local rules, and presentation while preserving shared guarantees. | [MOD-001](docs/platform-requirements.md#mod-001--selectable-capabilities)–[MOD-007](docs/platform-requirements.md#mod-007--reproducible-configuration-context), [JUR-001](docs/platform-requirements.md#jur-001--separation-of-general-and-jurisdiction-specific-requirements)–[JUR-004](docs/platform-requirements.md#jur-004--versioned-applicability-and-evidence), [NFR-LOC-001](docs/platform-requirements.md#nfr-loc-001--interface-and-clinical-language)–[NFR-LOC-004](docs/platform-requirements.md#nfr-loc-004--localization-verification) |

## Requirement status

Requirements use the following statuses:

- **Proposed** — draft behavior to refine through implementation, verification, and published evidence.
- **Externally driven** — clearly required by an identified external obligation, standard, or jurisdictional rule; exact implementation still requires validation.
- **Decision required** — detailed behavior, applicability, or delivery boundary depends on an unresolved decision; this does not remove its domain from the product ambition.

Priority is intentionally not assigned in this version except where an external obligation makes a capability unavoidable for a particular deployment.

### Editing and readiness rules

- Keep each requirement focused on one obligation, with a stable ID, status, and applicability.
- Give each requirement or question one authoritative location. Link by ID; keep verification criteria with the requirement or in linked cases.
- For new or materially changed requirements, include **Verify:** with an observable pass/fail outcome and **Open:** references for unresolved inputs.
- For each implementation increment, define behavior, dependencies, and verification cases, including relevant failures. Resolve uncertainties affecting correctness; unrelated open questions do not block development.
- Keep rationale only when it explains a constraint or tradeoff. Label examples and explanations as informative; new obligations need requirement IDs.
- Create a supporting document when a topic needs its own workflow, state, data, or verification definitions. Avoid empty placeholders and one-file-per-requirement fragmentation.
- Supporting detail must stay within the master scope; resolve conflicts explicitly. Update links when moving content.
- Edit the current documents in place; create snapshots only for agreed baselines.

**Verify** describes a planned check, not a test result. Existing requirements without verification criteria remain discovery proposals.

## Recommended next specification work

1. Review the coverage map for missing domains, roles, and cross-setting journeys.
2. Define representative workflows across that breadth: actors, triggers, information changes, handovers, completion, and failures.
3. Identify shared guarantees, module dependencies, local variation, and integrations; compare selected assumptions with another jurisdiction.
4. Decide the remaining development questions: roadmap, backlog, the rest of the technology stack, the openEHR scope, and the validation harness design ([Q-DEV-002–007](docs/decisions.md#development)), including scale targets ([SCL-Q01](docs/platform-requirements.md#scalability)) and the first increment's surfaces ([SUR-Q01](docs/platform-requirements.md#user-surfaces-and-assistants)). No product code is written before these decisions.
5. Build working increments and verify them against research-grounded scenarios; link findings to requirements and regression checks. Prototypes written before step 4 test rules only and are not reused as product code.
6. Develop safety, privacy, operational, and jurisdiction evidence alongside capabilities; set measurable quality targets for actual care use.

## Change log

| Version | Date | Change |
|---|---|---|
| 0.1 | 2026-09-19 | Initial Swedish-oriented structured specification. |
| 0.2 | 2026-09-19 | Reframed as a general clinical information system with Sweden as the initial case study. Translated to English. Removed premature architecture, system-context, and internal data-model proposals. Added requirement categories for core, care-setting, jurisdiction, and deployment variation. |
| 0.3 | 2026-09-19 | Adopted comprehensive modular scope with Sweden first and practitioner dogfooding. Added module, localization, and profile requirements with verification criteria. Split the master from supporting definitions and a coverage map; requirement IDs retained. |
| 0.4 | 2026-10-26 | Dropped practitioner dogfooding: workflows are grounded in published sources and verified against research-grounded scenarios. Added the laboratory result loop as the first workflow slice and EU regulatory requirements. |
| 0.5 | 2026-10-27 | Adopted interaction surfaces: a graphical client and AI assistants as clients of one action interface. Added user-surface and assistant requirements and the development decisions that precede product code. Stopped prototype work until those decisions are made. Adopted the development approach: C# backend, Svelte frontend in TypeScript, PostgreSQL, clean architecture, object orientation, domain-driven design, test-driven development, and vertical slices. |
| 0.6 | 2026-10-28 | Adopted frameworks: ASP.NET Core, Dapper, SvelteKit, NUnit, and Vitest. Adopted openEHR as the record model, targeting the current releases with ADL 2 and full AQL 1.1.0, implemented by the project, with a required validation harness; proposed the harness design. Replaced the REST 1.0.3 reference pages with 1.1.0. |
