# Verification references

[Assurance](assurance.md#testing-and-verification) · **Status:** Informative reference set · **Date:** 2026-09-19 · **Updated:** 2026-10-28

The [local reference pack](../references/README.md) contains selected, unmodified standards pages. Its [manifest](../references/manifest.json) pins source URLs, releases, retrieval dates, licenses, and content hashes. These references support the [openEHR validation harness](openehr-validation.md) and the earlier [record-model comparison](record-model-comparison.md); they do not establish conformance.

## Retained contracts

| Reference | Baseline and local entry points | Verification use |
|---|---|---|
| openEHR reference model | RM 1.1.0: [Common](../references/upstream/openehr/RM-1.1.0/common.html), [EHR](../references/upstream/openehr/RM-1.1.0/ehr.html), [Data Types](../references/upstream/openehr/RM-1.1.0/data_types.html) | Version history, contributions, attestation scope, clinical context, quantities, uncertainty, and time. |
| openEHR identifiers | BASE 1.2.0: [Base Types](../references/upstream/openehr/BASE-1.2.0/base_types.html) | Stable object identity versus version identity and references. |
| openEHR REST | ITS-REST 1.1.0: [Overview](../references/upstream/openehr/ITS-REST-1.1.0/overview.html), [EHR](../references/upstream/openehr/ITS-REST-1.1.0/ehr.html), [Query](../references/upstream/openehr/ITS-REST-1.1.0/query.html), [Definition](../references/upstream/openehr/ITS-REST-1.1.0/definition.html) | Conditional updates, histories, errors, template operations, and query responses. |
| openEHR query and modelling | QUERY 1.1.0: [AQL](../references/upstream/openehr/QUERY-1.1.0/AQL.html); AM 2.3.0: [ADL 2](../references/upstream/openehr/AM-2.3.0/ADL2.html), [ADL 1.4](../references/upstream/openehr/AM-2.3.0/ADL1.4.html) | Query semantics and content constraints; derive valid and invalid fixtures. AM component version and ADL language version are distinct. |
| HL7 FHIR exchange | R5 5.0.0: [HTTP](../references/upstream/fhir/R5/http.html), [documents](../references/upstream/fhir/R5/documents.html), [references](../references/upstream/fhir/R5/references.html), [validation](../references/upstream/fhir/R5/validation.html) | Transactions, concurrency, exact-version references, document boundaries, and validation limits. Composition, DiagnosticReport, Observation, Task, and Provenance pages are also retained. |

The openEHR implementation targets the current releases; the [harness](openehr-validation.md#target-releases) lists them. On 2026-10-28 the REST pages were replaced with release 1.1.0, published 19 July 2026; the earlier comparison and repository experiment used 1.0.3. R5 does not select a Swedish interface version. Read each document's normative/informative and maturity markings; inclusion does not make every example a requirement.

## Connect clauses to product cases

| Existing case | Product requirements | Standard mechanisms to inspect | Product behavior to prove separately |
|---|---|---|---|
| Concurrent signing | [DOC-005](clinical-requirements.md#doc-005--signing-and-confirmation), [DOC-008](clinical-requirements.md#doc-008--change-history) | Common §6.2.8; composition update preconditions; FHIR HTTP concurrency and document attestation. | Reject a stale reviewed snapshot, including required-fresh referenced content; retain the exact confirmed presentation. |
| Corrected result | [DOC-007](clinical-requirements.md#doc-007--correction-and-amendment), [ORD-006](clinical-requirements.md#ord-006--result-review-and-follow-up) | Common §6; DiagnosticReport/Observation status and references; transaction boundaries. | Preserve prior review, create one reassessment obligation, reconcile duplicates and late messages, and recover across crashes. |
| Care handover | [WF-005](clinical-requirements.md#wf-005--handover), [INT-004](platform-requirements.md#int-004--reliable-state-changing-exchange), [IAM-004](platform-requirements.md#iam-004--context-sensitive-authorization) | EHR instructions/actions; FHIR Task and document references. | Explicit responsibility acceptance, retry reconciliation, current authorization, and follow-up after correction. |

The [cases](record-model-comparison.md) own expected outcomes. When making them executable, record requirement and case, source ID and exact clause, server/build/configuration, fixture hashes, stimulus, expected and observed outcome. Distinguish standard conformance from our additional workflow policy. A valid payload alone cannot prove the workflow.

## Material still to select

- **Clinical models:** select [CKM](https://ckm.openehr.org/ckm/) archetypes for the cases; retain exact revisions, publication status, licenses, dependencies, template source, and the compiled ADL 2 operational template. Add synthetic valid, invalid, corrected, and historical instances with expected outcomes.
- **Machine-readable contracts:** freeze the commit of the [openEHR OpenAPI sources](https://github.com/openEHR/specifications-ITS-REST/tree/master/computable/OAS) that matches ITS-REST 1.1.0, resolving referenced files. The published specification links to a moving branch, so that link is insufficient as a test pin. For the R5 comparison, use `hl7.fhir.r5.core#5.0.0` from [HL7's downloads](https://hl7.org/fhir/R5/downloads.html), plus exact validator, profile, and terminology versions. Select relevant [FHIR test cases](https://github.com/FHIR/fhir-test-cases) at a fixed revision.
- **Conformance material:** the [validation harness](openehr-validation.md#sources-of-expected-behavior) covers the openEHR conformance specifications and external test catalogues.

Broader security, recovery, usability, and jurisdiction checks remain in [Assurance](assurance.md), [Platform requirements](platform-requirements.md), and the [Sweden profile](sweden.md). Add the specific integration contracts and terminology releases when their scope is selected.
