# Clinical Information System Specification

**Document status:** Draft  
**Version:** 0.2  
**Date:** 2026-09-19  
**Purpose:** Establish an initial requirements baseline for a general clinical information system. Sweden is the initial case study and implementation driver, but does not define the product boundary.

> This document deliberately avoids unnecessary assumptions. Where a capability, workflow, jurisdictional rule, or product decision has not been established, it is recorded as an open question rather than treated as decided.

---

# 1. Product framing

The product is intended to support healthcare delivery across multiple jurisdictions and care settings.

Sweden is used as:

- the initial case study,
- the first source of detailed real-world requirements,
- the initial implementation and validation environment,
- a means of testing whether the general product requirements are sufficiently expressive.

Swedish healthcare structures, terminology, integrations, administrative practices, and regulations must not be assumed to define the general product unless the underlying need is genuinely general.

## 1.1 Requirement categories

Each requirement should, where relevant, be classified according to the level at which it applies:

- **Core** — generally applicable healthcare capability.
- **Care-setting-specific** — required only in particular settings such as inpatient care, emergency care, primary care, intensive care, surgery, psychiatry, or oncology.
- **Jurisdiction-specific** — required because of national or regional healthcare infrastructure, regulation, terminology, reimbursement, identity schemes, or established practice.
- **Deployment-specific** — required by a particular healthcare organization or installation.

A requirement may belong to more than one category.

## 1.2 Specification level

This document specifies capabilities, workflows, information needs, constraints, invariants, and open questions.

It does **not** yet specify:

- internal software architecture,
- internal data structures,
- database schemas,
- API shapes,
- service boundaries,
- programming models,
- implementation technologies,
- physical deployment topology.

Those decisions should be made only after the relevant product and workflow requirements are sufficiently understood.

---

# 2. Scope

The specification initially covers:

- patient identity and demographics,
- healthcare organizations and care contexts,
- clinical documentation,
- structured clinical information,
- medications,
- orders, investigations, and results,
- referrals and consultations,
- care planning and clinical workflow,
- clinical decision support,
- patient preferences, consent, and information restrictions,
- patient access,
- interoperability,
- identity, authentication, authorization, and privacy,
- auditability and access monitoring,
- administration and configuration,
- availability, continuity, security, and performance,
- migration and information lifecycle,
- patient-safety and verification requirements.

## 2.1 Product scope not yet decided

The following are intentionally unresolved in version 0.2:

- which care settings the first release will support,
- whether the product is intended to become a complete clinical information system or a smaller clinical core used with external specialist systems,
- whether scheduling is part of the product,
- whether billing, reimbursement, coding, and revenue-cycle capabilities are part of the product,
- whether laboratory, imaging, intensive-care, theatre, or other specialist systems are built in or integrated,
- whether the product provides a patient-facing application or primarily interoperates with external patient services,
- which clinical decision-support capabilities belong in the product,
- the regulatory classification of the product or individual capabilities,
- the countries beyond Sweden that should be used as early validation cases.

---

# 3. Goals

The system shall enable authorized users to document, find, understand, and use relevant patient information in support of safe and effective healthcare.

The product should pursue the following properties.

1. **Patient safety** — information and workflows should reduce the likelihood and impact of clinical error.
2. **Continuity of information** — relevant information should remain understandable across time, encounters, teams, and organizational boundaries where permitted.
3. **Traceability** — it should be possible to determine who created, changed, signed, accessed, or otherwise acted on clinically or legally relevant information.
4. **Appropriate access** — access should be limited according to purpose, role, organizational context, care relationship, and other relevant constraints.
5. **Interoperability** — relevant information should be exchangeable with other systems without unnecessary proprietary dependency.
6. **Structured information where useful** — clinically meaningful facts should not exist only as narrative text when they need to be searched, validated, exchanged, aggregated, or used by decision support.
7. **Preserved clinical context** — structure must not remove context required for safe interpretation.
8. **Usability in clinical work** — common workflows should minimize unnecessary cognitive and administrative burden.
9. **Controlled change** — correction and amendment must preserve history and accountability.
10. **Jurisdictional adaptability** — national requirements should be supportable without turning local concepts into universal assumptions.
11. **Organizational adaptability** — local workflow variation should be supportable without requiring unnecessary product forks.

---

# 4. Terminology

| Term | Meaning in this document |
|---|---|
| Patient | A person receiving, having received, or expected to receive healthcare. |
| User | A human or technical actor using the system. |
| Healthcare provider | An organization or legal entity responsible for providing healthcare. Exact legal meaning varies by jurisdiction. |
| Care unit | An organizational unit within or associated with a healthcare provider. |
| Care contact | A planned or completed interaction between a patient and healthcare service, physical or digital. |
| Episode of care | A clinically or administratively related period of care. Exact boundaries are not yet defined. |
| Clinical information | Information used to document, understand, plan, deliver, or evaluate patient care. |
| Clinical record | The body of recorded clinical information that forms part of the patient record under the applicable jurisdiction. |
| Clinical fact | A discrete item of clinically meaningful information, such as a diagnosis, observation, allergy, medication order, result, or procedure. |
| Signing | An explicit confirmation of information or an action by an authorized user. Exact meaning depends on workflow and jurisdiction. |
| Access log | A trace of access to patient information. |
| Audit record | A broader trace of relevant system, administrative, security, and clinical actions. |
| Jurisdiction profile | The set of requirements specific to a country, region, or healthcare jurisdiction. |
| Deployment configuration | Organization-specific configuration that does not redefine general clinical meaning. |

---

# 5. Actors

The following actors are candidates. The initial supported set is an open product decision.

- physicians,
- nurses,
- nursing assistants,
- midwives,
- psychologists,
- physiotherapists,
- occupational therapists,
- social workers,
- speech and language therapists,
- dietitians,
- pharmacists,
- medical secretaries and clinical administrators,
- scheduling and administrative staff,
- clinical managers,
- system administrators,
- information-security personnel,
- audit and access-monitoring personnel,
- support personnel,
- patients,
- guardians,
- legally authorized representatives,
- external healthcare providers,
- external systems and technical clients.

### Open question ACT-Q01

Which professional roles and organizational forms must be supported in the first product release?

---

# 6. Requirement status

Requirements use the following statuses:

- **Proposed** — part of the current draft but not yet validated with representative healthcare organizations.
- **Externally driven** — clearly required by an identified external obligation, standard, or jurisdictional rule; exact implementation still requires validation.
- **Decision required** — inclusion or scope depends on an unresolved product decision.

Priority is intentionally not assigned in this version except where an external obligation makes a capability unavoidable for a particular deployment.

---

# 7. Functional requirements

## 7.1 Patient identity and demographics

### PAT-001 — Unambiguous patient identification
**Category:** Core  
**Status:** Proposed  
The system shall support associating clinical information with an identified patient and shall provide safeguards against documenting information for the wrong patient.

### PAT-002 — Patient with unknown or uncertain identity
**Category:** Core  
**Status:** Proposed  
The system shall support care and documentation when the patient's identity is unknown, incomplete, or uncertain.

### PAT-003 — Multiple identifier schemes
**Category:** Core / Jurisdiction-specific  
**Status:** Proposed  
The system shall support patients identified through different identifier schemes and shall not assume that one national identifier is universally available.

### PAT-004 — Sensitive demographic and identity information
**Category:** Core / Jurisdiction-specific  
**Status:** Proposed  
The system shall support controlled handling of demographic or identity information requiring special protection, including restrictions on display, search, export, and access where applicable.

### PAT-005 — Identity correction and duplicate resolution
**Category:** Core  
**Status:** Proposed  
The system shall support controlled correction of identity information and resolution of duplicate patient records without loss of clinical history or traceability.

### PAT-006 — Reversal of incorrect patient merge
**Category:** Core  
**Status:** Proposed  
Where patient records can be merged, the system should support controlled recovery from an incorrect merge when safe recovery is technically and clinically possible.

### PAT-007 — Contact information
**Category:** Core  
**Status:** Proposed  
The system shall support relevant patient contact information and its provenance and currency where these are clinically or operationally important.

### PAT-008 — Related persons and representatives
**Category:** Core / Jurisdiction-specific  
**Status:** Proposed  
The system shall support relevant relationships such as next of kin, guardians, carers, and legally authorized representatives.

### Open questions

- **PAT-Q01:** Is the system the authoritative source for patient demographics or does it consume them from another service?
- **PAT-Q02:** Which patient-identity schemes must be supported in the first implementation?
- **PAT-Q03:** How should identity changes affect historical information, searching, and external exchange?
- **PAT-Q04:** Which duplicate-resolution actions require human approval?

---

## 7.2 Organization, care context, and encounters

### ENC-001 — Healthcare organizations and care units
**Category:** Core  
**Status:** Proposed  
The system shall represent the organizational context necessary to understand responsibility, access, and provenance of clinical information.

### ENC-002 — Care contacts
**Category:** Core  
**Status:** Proposed  
The system shall support planned and completed care contacts with relevant time, location, participants, and organizational context.

### ENC-003 — Episodes and admissions
**Category:** Core / Care-setting-specific  
**Status:** Proposed  
The system shall support clinically and operationally meaningful episodes of care, including admission, transfer, and discharge where inpatient care is in scope.

### ENC-004 — Clinical and organizational responsibility
**Category:** Core  
**Status:** Proposed  
The system shall be able to represent responsible professionals, teams, and organizational units where required by the care process.

### ENC-005 — Care location
**Category:** Care-setting-specific  
**Status:** Decision required  
If inpatient or facility-based care is in scope, the system shall support the relevant physical or logical care locations and movement history.

### ENC-006 — Concurrent care
**Category:** Core  
**Status:** Proposed  
The system shall not assume that a patient can participate in only one active care process at a time.

### Open questions

- **ENC-Q01:** Which encounter and episode concepts are required across the first target care settings?
- **ENC-Q02:** Is scheduling part of the product or an external capability?
- **ENC-Q03:** Is bed and capacity management part of the product?
- **ENC-Q04:** How should overlapping and cross-organizational care processes be represented to users?

---

## 7.3 Clinical documentation

### DOC-001 — Clinical record entries
**Category:** Core  
**Status:** Proposed  
The system shall support recording clinical information with sufficient context to identify the patient, author or responsible party, relevant time, and care context.

### DOC-002 — Narrative and structured documentation
**Category:** Core  
**Status:** Proposed  
The system shall support both narrative and structured documentation where each form is appropriate.

### DOC-003 — Documentation templates
**Category:** Core / Deployment-specific  
**Status:** Proposed  
The system shall support configurable documentation templates without requiring every local template to become a product-specific data concept.

### DOC-004 — Draft and completed states
**Category:** Core  
**Status:** Proposed  
The system shall distinguish unfinished documentation from information considered complete for its intended workflow.

### DOC-005 — Signing and confirmation
**Category:** Core / Jurisdiction-specific  
**Status:** Proposed  
The system shall support explicit signing or confirmation where required by workflow, policy, or jurisdiction.

### DOC-006 — Countersigning or supervisory confirmation
**Category:** Care-setting-specific / Jurisdiction-specific  
**Status:** Decision required  
The system shall support countersigning or supervisory confirmation where required.

### DOC-007 — Correction and amendment
**Category:** Core  
**Status:** Proposed  
The system shall support correction and amendment without silently destroying or rewriting previously recorded clinical information.

### DOC-008 — Change history
**Category:** Core  
**Status:** Proposed  
It shall be possible to determine relevant previous states of clinical documentation, who made a change, and when it occurred.

### DOC-009 — Longitudinal presentation
**Category:** Core  
**Status:** Proposed  
The system shall support chronological presentation of clinically relevant events and documentation.

### DOC-010 — Search
**Category:** Core  
**Status:** Proposed  
Authorized users shall be able to search patient information. Search results shall enforce the same access and privacy rules as direct access.

### DOC-011 — Clinical summaries
**Category:** Core / Care-setting-specific  
**Status:** Proposed  
The system shall support summaries appropriate to the care setting, such as discharge summaries, visit summaries, transfer summaries, or handover documentation.

### DOC-012 — Language requirements
**Category:** Jurisdiction-specific / Deployment-specific  
**Status:** Decision required  
The system shall support applicable requirements concerning the language in which clinical records must be maintained and presented.

### Open questions

- **DOC-Q01:** For which documentation types is signing required?
- **DOC-Q02:** How should late entries and amendments be presented in different views?
- **DOC-Q03:** Are dictation, speech-to-text, or AI-assisted drafting in the initial scope?
- **DOC-Q04:** Is concurrent editing of the same clinical document required?
- **DOC-Q05:** Which information must be documented as narrative even when structured data exists elsewhere?

---

## 7.4 Clinical facts and health information

The system must support clinically meaningful information as more than undifferentiated text where structure is necessary for care, search, exchange, safety, or decision support. The exact internal representation is deliberately not specified here.

### CLI-001 — Diagnoses and health conditions
**Category:** Core  
**Status:** Proposed  
The system shall support recording diagnoses and other health conditions with sufficient context to understand their meaning, status, timing, source, and clinical relevance.

### CLI-002 — Problems
**Category:** Core  
**Status:** Proposed  
The system shall support active and historical clinical problems where the distinction from formal diagnosis is useful in the care process.

### CLI-003 — Allergies, intolerances, and hypersensitivities
**Category:** Core  
**Status:** Proposed  
The system shall support structured recording of clinically relevant allergies, intolerances, and hypersensitivities.

### CLI-004 — Critical clinical warnings
**Category:** Core  
**Status:** Proposed  
Information representing significant immediate risk shall be capable of being made prominent in relevant clinical contexts.

### CLI-005 — Observations and measurements
**Category:** Core  
**Status:** Proposed  
The system shall support observations and measurements with sufficient context for safe interpretation, including units and time where relevant.

### CLI-006 — Procedures and interventions
**Category:** Core  
**Status:** Proposed  
The system shall support planned and completed procedures and clinical interventions.

### CLI-007 — Devices and implants
**Category:** Core / Care-setting-specific / Jurisdiction-specific  
**Status:** Proposed  
The system shall support clinically and legally relevant information about devices and implants associated with the patient.

### CLI-008 — Complications and healthcare-associated conditions
**Category:** Core / Care-setting-specific  
**Status:** Proposed  
The system shall support documentation of complications and healthcare-associated conditions where relevant.

### CLI-009 — Patient preferences and goals
**Category:** Core  
**Status:** Proposed  
The system shall support clinically relevant patient preferences, goals, and expressed wishes.

### CLI-010 — Clinical terminology and coding
**Category:** Core / Jurisdiction-specific  
**Status:** Proposed  
The system shall support controlled terminologies and coding systems where needed for clinical meaning, exchange, classification, reporting, or reimbursement.

### Open questions

- **CLI-Q01:** Which clinical facts must be structured in the first release?
- **CLI-Q02:** Which terminology systems are required in the first jurisdictions?
- **CLI-Q03:** Who is responsible for reconciling conflicting clinical information from different sources?
- **CLI-Q04:** Which information is allowed to be provisional, patient-reported, imported, or unverified?

---

## 7.5 Medications

### MED-001 — Current medication picture
**Category:** Core  
**Status:** Proposed  
The system shall be able to present a coherent view of the patient's known current medication treatment, including source and currency where clinically important.

### MED-002 — Medication ordering
**Category:** Core / Care-setting-specific  
**Status:** Proposed  
The system shall support initiation, modification, suspension, resumption, and discontinuation of medication treatment where medication ordering is in scope.

### MED-003 — Indication or reason
**Category:** Core  
**Status:** Proposed  
The system shall support recording the clinical reason for medication treatment where relevant.

### MED-004 — Dosing
**Category:** Core / Care-setting-specific  
**Status:** Proposed  
The system shall support dosing patterns required by the relevant care settings, including regular, as-needed, time-limited, titrated, and other clinically necessary regimens.

### MED-005 — Medication administration
**Category:** Care-setting-specific  
**Status:** Decision required  
If medication administration is in scope, the system shall support planned and actual administrations, including relevant time, administering professional, omissions, and deviations.

### MED-006 — Infusions
**Category:** Care-setting-specific  
**Status:** Decision required  
If infusion therapy is in scope, the system shall support the relevant ordering, preparation, administration, monitoring, and change workflows.

### MED-007 — Prescription workflows
**Category:** Jurisdiction-specific  
**Status:** Decision required  
If outpatient or external prescribing is in scope, the system shall support the prescription workflows and external services required by the applicable jurisdiction.

### MED-008 — Medication reconciliation
**Category:** Core  
**Status:** Proposed  
The system shall support medication reconciliation and explicit handling of discrepancies between information sources.

### MED-009 — Medication decision support
**Category:** Core / Jurisdiction-specific  
**Status:** Decision required  
The system should be able to support clinically relevant checks such as interactions, allergies, duplicate therapy, contraindications, and dose-related risk. Exact capabilities, sources, and regulatory implications must be specified separately.

### Open questions

- **MED-Q01:** Is medication management part of the core product or a separately governed module?
- **MED-Q02:** Which care settings must medication ordering and administration support initially?
- **MED-Q03:** Which external medication and prescription services are required per jurisdiction?
- **MED-Q04:** Which medication knowledge bases and decision-support sources are acceptable?
- **MED-Q05:** How are discrepancies between patient-reported, externally sourced, prescribed, dispensed, and administered medication information handled?

---

## 7.6 Orders, investigations, and results

### ORD-001 — Clinical orders and requests
**Category:** Core  
**Status:** Proposed  
The system shall support initiating requests for clinically relevant investigations, services, and procedures.

### ORD-002 — External fulfillment
**Category:** Core  
**Status:** Proposed  
The system shall support orders that are fulfilled by external or specialist systems and shall be able to receive relevant status and results.

### ORD-003 — Results
**Category:** Core  
**Status:** Proposed  
The system shall present results with sufficient provenance, timing, status, and context for safe clinical interpretation.

### ORD-004 — Units, ranges, and abnormality
**Category:** Core  
**Status:** Proposed  
Quantitative results shall support relevant units, reference information, and abnormal-result indicators when supplied or clinically appropriate.

### ORD-005 — Trends
**Category:** Core  
**Status:** Proposed  
The system shall support viewing relevant measurements and results over time.

### ORD-006 — Result review and follow-up
**Category:** Core  
**Status:** Proposed  
The system shall support responsibility for receiving, reviewing, acknowledging, and following up results where the clinical workflow requires it.

### ORD-007 — Critical results
**Category:** Core / Care-setting-specific  
**Status:** Proposed  
The system shall support special handling and escalation of critical results according to defined organizational rules.

### ORD-008 — Imaging
**Category:** Care-setting-specific  
**Status:** Decision required  
If diagnostic imaging is in scope, the system shall support the necessary ordering, report, image-access, and status workflows, either directly or through integration.

### ORD-009 — Laboratory medicine
**Category:** Care-setting-specific  
**Status:** Decision required  
If laboratory workflows are in scope, the system shall support the necessary request, specimen, status, and result flows across relevant laboratory disciplines.

### Open questions

- **ORD-Q01:** Which order types are required initially?
- **ORD-Q02:** Who owns responsibility for unreviewed or unacknowledged results?
- **ORD-Q03:** Are order sets or protocol-based grouped orders required?
- **ORD-Q04:** Which specialist diagnostic systems remain authoritative for their data?

---

## 7.7 Referrals and consultations

### REF-001 — Referral creation
**Category:** Core  
**Status:** Proposed  
The system shall support referrals or consultation requests containing the clinical and administrative information required by the receiving service.

### REF-002 — Referral lifecycle
**Category:** Core  
**Status:** Proposed  
The system shall support the lifecycle of a referral or consultation request, including states such as created, sent, received, assessed, additional information requested, accepted, rejected, answered, and closed where relevant.

### REF-003 — Incoming referrals
**Category:** Core / Care-setting-specific  
**Status:** Proposed  
The system shall support receiving and triaging incoming referrals where the deployment acts as a receiving service.

### REF-004 — Responses
**Category:** Core  
**Status:** Proposed  
The system shall support linking consultation or referral responses to the original request and relevant care context.

### REF-005 — Follow-up and work queues
**Category:** Core  
**Status:** Proposed  
The system shall support identifying referrals that require action, supplementation, review, or response.

### Open questions

- **REF-Q01:** Which referral models differ materially between target jurisdictions?
- **REF-Q02:** Which referral exchanges should occur through direct interoperability and which through external regional or national services?
- **REF-Q03:** Is referral scheduling part of the same workflow or a separate capability?

---

## 7.8 Care plans, tasks, and clinical workflow

### WF-001 — Care plans
**Category:** Core  
**Status:** Proposed  
The system shall support documenting and reviewing care plans where applicable.

### WF-002 — Goals and planned activities
**Category:** Core  
**Status:** Proposed  
Care planning shall be able to include goals, planned activities, responsibility, status, and follow-up where clinically appropriate.

### WF-003 — Clinical tasks
**Category:** Core  
**Status:** Proposed  
The system shall support clinically relevant tasks assigned to appropriate individuals, roles, teams, or work queues.

### WF-004 — Work lists
**Category:** Core / Deployment-specific  
**Status:** Proposed  
The system shall support role- and context-sensitive work lists such as ward lists, result queues, referral queues, and follow-up lists.

### WF-005 — Handover
**Category:** Core / Care-setting-specific  
**Status:** Proposed  
The system should support controlled handover of relevant responsibility, pending work, and clinical context.

### WF-006 — Discharge planning
**Category:** Care-setting-specific  
**Status:** Decision required  
If inpatient care is in scope, the system shall support discharge planning and the necessary summaries, medication reconciliation, follow-up, and handover activities.

### Open questions

- **WF-Q01:** Which workflows should be configurable by a healthcare organization and which require product-level behavior?
- **WF-Q02:** Which tasks may be generated automatically?
- **WF-Q03:** Which temporary workflow information forms part of the legal or clinical record?
- **WF-Q04:** Which workflow states must be standardized across deployments to preserve interoperability and safety?

---

## 7.9 Clinical decision support

### CDS-001 — Distinction from source clinical information
**Category:** Core  
**Status:** Proposed  
Clinical decision-support output shall remain distinguishable from the underlying clinical information on which it is based.

### CDS-002 — Traceability
**Category:** Core  
**Status:** Proposed  
Where decision support can materially influence clinical action, the system shall support traceability of the relevant rule, model, knowledge source, version, and input context to the extent necessary for safety and governance.

### CDS-003 — Alert prioritization
**Category:** Core  
**Status:** Proposed  
The system shall support prioritization of alerts and other interventions to reduce inappropriate interruption and alert fatigue.

### CDS-004 — Override
**Category:** Core  
**Status:** Proposed  
Where decision support may be overridden, override behavior shall be explicit and may require a reason depending on risk and policy.

### CDS-005 — Intended purpose and regulatory assessment
**Category:** Jurisdiction-specific  
**Status:** Externally driven  
The intended purpose and regulatory implications of each material decision-support capability shall be established before production use.

### Open questions

- **CDS-Q01:** Which decision-support capabilities are in the first release?
- **CDS-Q02:** May deployments define their own clinical rules?
- **CDS-Q03:** Will predictive or generative models be used?
- **CDS-Q04:** What validation evidence is required before a locally configured rule can affect care?

---

## 7.10 Consent, restrictions, and patient choices

### CON-001 — Consent
**Category:** Core / Jurisdiction-specific  
**Status:** Proposed  
The system shall support the forms of consent that need to be recorded or enforced in care and information-exchange workflows.

### CON-002 — Information restrictions
**Category:** Core / Jurisdiction-specific  
**Status:** Proposed  
The system shall support restrictions on use or disclosure of patient information where required by applicable rules or patient choices.

### CON-003 — Emergency or exceptional access
**Category:** Jurisdiction-specific / Deployment-specific  
**Status:** Decision required  
Where exceptional access to otherwise restricted information is permitted, the system shall enforce the applicable conditions and create enhanced traceability.

### CON-004 — Cross-organizational information exchange
**Category:** Core / Jurisdiction-specific  
**Status:** Proposed  
The system shall apply the consent, authorization, restriction, and provenance rules required when information crosses organizational boundaries.

### Open questions

- **CON-Q01:** Which consent concepts are general clinical concepts and which are jurisdiction-specific mechanisms?
- **CON-Q02:** Which consent and restriction information is locally managed versus obtained from external services?
- **CON-Q03:** How are conflicting restrictions from different sources resolved?

---

## 7.11 Patient access and participation

### PRT-001 — Patient access to information
**Category:** Core / Jurisdiction-specific  
**Status:** Proposed  
The system shall be able to make permitted information available to the patient through the channel selected for the deployment.

### PRT-002 — Patient-submitted information
**Category:** Core  
**Status:** Decision required  
If patient-submitted information is in scope, the system shall clearly distinguish its source and support an appropriate review or incorporation process.

### PRT-003 — Representatives and proxies
**Category:** Core / Jurisdiction-specific  
**Status:** Decision required  
Patient-facing access shall support authorized representatives where required by the care model and applicable rules.

### PRT-004 — Patient visibility of access history
**Category:** Jurisdiction-specific  
**Status:** Decision required  
The system shall support patient access to relevant access-history information where required.

### Open questions

- **PRT-Q01:** Will the product include its own patient-facing application?
- **PRT-Q02:** Which patient-facing functions are expected to be provided by national or regional services?
- **PRT-Q03:** Which patient-submitted information can directly affect clinical workflow?

---

## 7.12 Interoperability

### INT-001 — External interfaces
**Category:** Core  
**Status:** Proposed  
The system shall provide documented and versioned mechanisms for exchanging information that must cross the product boundary.

### INT-002 — Standards
**Category:** Core / Jurisdiction-specific  
**Status:** Proposed  
Established healthcare or jurisdictional interoperability standards should be preferred over proprietary formats where they satisfy the clinical, semantic, operational, and security requirements.

### INT-003 — Semantic preservation
**Category:** Core  
**Status:** Proposed  
Information exchange shall preserve clinically relevant meaning, context, provenance, units, status, and uncertainty to the extent required for safe use.

### INT-004 — Reliable state-changing exchange
**Category:** Core  
**Status:** Proposed  
Exchange that changes clinical or operational state shall handle retries, duplicate messages, partial failure, and delayed delivery without uncontrolled duplicate clinical actions.

### INT-005 — Provenance of imported information
**Category:** Core  
**Status:** Proposed  
Users and downstream systems shall be able to distinguish imported information from locally created or locally verified information when that distinction matters clinically or legally.

### INT-006 — Jurisdictional infrastructure
**Category:** Jurisdiction-specific  
**Status:** Decision required  
The system shall support the national or regional interoperability services required by each supported jurisdiction profile.

### Open questions

- **INT-Q01:** Which external systems must be supported in the first deployment?
- **INT-Q02:** Which interoperability standards are mandatory in the first jurisdiction?
- **INT-Q03:** What information is authoritative locally and what remains authoritative in an external source?
- **INT-Q04:** Which information may be cached, copied, or transformed, and under what conditions?
- **INT-Q05:** What conformance testing is required for each external service?

---

## 7.13 Identity, authentication, and authorization

### IAM-001 — Strong authentication
**Category:** Core / Jurisdiction-specific  
**Status:** Proposed  
The system shall support authentication appropriate to the sensitivity of the information and the risk of the action being performed.

### IAM-002 — Individual accountability
**Category:** Core  
**Status:** Proposed  
Actions performed by human users shall be attributable to individually identifiable users. Shared personal clinical accounts shall not be relied on for accountable clinical access.

### IAM-003 — Need-based access
**Category:** Core  
**Status:** Proposed  
Access to patient information shall be restrictable according to job function, organizational context, care relationship, purpose, and other relevant factors.

### IAM-004 — Context-sensitive authorization
**Category:** Core  
**Status:** Proposed  
Authorization shall be capable of considering both relatively stable user attributes and the context of the current access request.

### IAM-005 — External identity infrastructure
**Category:** Jurisdiction-specific / Deployment-specific  
**Status:** Decision required  
The system shall integrate with the identity and credential infrastructure required by the deployment.

### IAM-006 — Privileged administration
**Category:** Core  
**Status:** Proposed  
Administrative privileges shall be separated from ordinary clinical access and subject to enhanced control and audit.

### IAM-007 — Technical identities
**Category:** Core  
**Status:** Proposed  
Technical clients and integrations shall use separately governed identities and only the privileges they require.

### IAM-008 — Authorization lifecycle
**Category:** Core  
**Status:** Proposed  
The system shall support timely change or removal of access when employment, assignment, role, organizational affiliation, or care responsibility changes.

### Open questions

- **IAM-Q01:** Which identity infrastructure is used in the first deployment?
- **IAM-Q02:** Which access decisions are controlled by the product and which by external policy services?
- **IAM-Q03:** How are temporary assignments, on-call duties, trainees, and consultants handled?
- **IAM-Q04:** How is access justified when no explicit care relationship exists but legitimate work requires access?

---

## 7.14 Audit, access logging, and monitoring

### AUD-001 — Patient-information access logging
**Category:** Core / Jurisdiction-specific  
**Status:** Proposed  
The system shall record access to patient information with sufficient detail to support investigation, accountability, and jurisdictional monitoring requirements.

### AUD-002 — Access-log context
**Category:** Core  
**Status:** Proposed  
Access logging shall capture the user, patient, time, and relevant organizational or technical context needed to understand the access.

### AUD-003 — Protection of audit information
**Category:** Core  
**Status:** Proposed  
Audit and access records shall be protected against unauthorized alteration and deletion.

### AUD-004 — Access monitoring
**Category:** Core / Jurisdiction-specific  
**Status:** Proposed  
The product shall provide functionality or export mechanisms sufficient for systematic monitoring of access to patient information.

### AUD-005 — Risk-based review
**Category:** Core  
**Status:** Proposed  
Monitoring should be able to identify patterns that may warrant review, such as unusual timing, exceptional access, broad access, or access across unexpected organizational boundaries.

### AUD-006 — Administrative and configuration audit
**Category:** Core  
**Status:** Proposed  
Changes to permissions, security settings, clinical configuration, terminology, decision-support rules, and other safety-relevant configuration shall be auditable.

### AUD-007 — Patient access to access history
**Category:** Jurisdiction-specific  
**Status:** Decision required  
The system shall support the information needed for patient visibility into access history where required.

### Open questions

- **AUD-Q01:** Is access-monitoring functionality part of the product or an external security capability?
- **AUD-Q02:** What retention periods apply to different forms of audit information?
- **AUD-Q03:** What level of tamper evidence is required?
- **AUD-Q04:** Which audit data may itself contain sensitive patient information?

---

## 7.15 Administration and configuration

### ADM-001 — Controlled configuration
**Category:** Core / Deployment-specific  
**Status:** Proposed  
The system shall support controlled and traceable configuration of templates, terminology bindings, workflow rules, permissions, and other configurable behavior.

### ADM-002 — Configuration history
**Category:** Core  
**Status:** Proposed  
For safety-relevant configuration it shall be possible to determine what configuration was effective at a given historical point where this matters for understanding a clinical event.

### ADM-003 — Organizational separation
**Category:** Deployment-specific  
**Status:** Decision required  
If multiple healthcare providers share an installation, requirements for information, configuration, and access separation shall be explicitly defined.

### ADM-004 — Terminology management
**Category:** Core / Jurisdiction-specific  
**Status:** Proposed  
The system shall support controlled adoption and updating of externally maintained terminology and code systems.

### ADM-005 — Configuration boundaries
**Category:** Core  
**Status:** Proposed  
Configuration shall not be used to redefine clinically fundamental concepts in ways that make safety, interoperability, or testing dependent on arbitrary local interpretation.

### Open questions

- **ADM-Q01:** Which configuration may a healthcare organization change without a product release?
- **ADM-Q02:** Which configuration changes require clinical governance or approval?
- **ADM-Q03:** How much variation should be supported within one installation?

---

# 8. Non-functional requirements

## 8.1 Information security

### NFR-SEC-001 — Confidentiality, integrity, availability, and accountability
**Status:** Proposed  
The product and its operation shall protect the confidentiality, integrity, availability, and accountability of patient and healthcare information.

### NFR-SEC-002 — Protection in transit
**Status:** Proposed  
Sensitive information and credentials shall be protected in transit using current accepted security mechanisms appropriate to the deployment.

### NFR-SEC-003 — Protection at rest
**Status:** Proposed  
Protection of sensitive information at rest shall be included in the security requirements. Exact mechanisms and key-management requirements are not specified here.

### NFR-SEC-004 — Secret management
**Status:** Proposed  
Secrets and cryptographic credentials shall be managed so they are not exposed through source code or ordinary unsecured configuration.

### NFR-SEC-005 — Secure development lifecycle
**Status:** Proposed  
The product shall be developed using a documented secure-development process including vulnerability management, dependency management, security testing, and incident response.

### NFR-SEC-006 — Threat analysis
**Status:** Proposed  
Security threats to clinically or legally significant workflows shall be assessed and revisited when material product changes occur.

---

## 8.2 Availability and continuity

### NFR-AVL-001 — Availability targets
**Status:** Decision required  
Measurable availability targets shall be established per critical capability and care context before production commitments are made.

### NFR-AVL-002 — Resilience of critical workflows
**Status:** Proposed  
Critical clinical workflows shall not depend on avoidable single technical failure points without an appropriate fallback or recovery mechanism.

### NFR-AVL-003 — Recovery objectives
**Status:** Decision required  
Recovery point and recovery time objectives shall be established according to information and service criticality.

### NFR-AVL-004 — Downtime procedures
**Status:** Proposed  
Each deployment shall have a defined way to continue clinically necessary work during system or network disruption.

### Open questions

- **AVL-Q01:** What availability targets apply to the first care setting?
- **AVL-Q02:** Is read access required during a major central outage?
- **AVL-Q03:** Is client-side offline documentation required?
- **AVL-Q04:** Which functions may degrade safely during partial failure?

---

## 8.3 Performance

### NFR-PERF-001 — Interactive response
**Status:** Decision required  
Measurable response-time targets shall be established for common clinical actions such as opening a patient, viewing a summary, searching, saving documentation, signing, and ordering.

### NFR-PERF-002 — Large longitudinal records
**Status:** Proposed  
Performance shall remain acceptable for patients with extensive longitudinal history.

### NFR-PERF-003 — Realistic load
**Status:** Decision required  
Capacity targets shall be defined in terms meaningful to the intended deployment, including concurrent users, patient population, information volume, workflow activity, and integration traffic.

---

## 8.4 Scalability

### NFR-SCL-001 — Scale without loss of correctness
**Status:** Proposed  
The system shall be able to scale without compromising clinical information integrity, authorization, or traceability.

### Open questions

- **SCL-Q01:** What population and organizational scale must the first release support?
- **SCL-Q02:** Must one deployment support a single provider, multiple providers, a region, or a national-scale service?

---

## 8.5 Usability and accessibility

### NFR-UX-001 — Clinical efficiency
**Status:** Proposed  
Common workflows shall minimize unnecessary steps and cognitive burden without weakening safety controls.

### NFR-UX-002 — Critical information
**Status:** Proposed  
Information representing immediate clinical risk shall be presented clearly and consistently in relevant contexts.

### NFR-UX-003 — Efficient professional interaction
**Status:** Proposed  
The system should support efficient interaction methods suitable for high-volume professional use, including keyboard-centric workflows where appropriate.

### NFR-UX-004 — Accessibility
**Status:** Decision required  
Applicable accessibility requirements shall be established for each user-facing surface and jurisdiction.

### NFR-UX-005 — Supported device classes
**Status:** Decision required  
Supported device classes and interaction contexts shall be defined by user role and workflow rather than assumed globally.

---

## 8.6 Operability and technical monitoring

### NFR-OPS-001 — Technical monitoring
**Status:** Proposed  
The system shall expose sufficient technical health information to operate the service safely, including availability, latency, errors, queues, and resource use where relevant.

### NFR-OPS-002 — Cross-system troubleshooting
**Status:** Proposed  
Operational events shall be traceable across system boundaries without unnecessarily exposing patient-identifying information in technical logs.

### NFR-OPS-003 — Operational alerting
**Status:** Proposed  
Failures that threaten critical clinical or integration workflows shall be detectable and capable of triggering operational response.

### NFR-OPS-004 — Support without routine record access
**Status:** Proposed  
Normal operation and troubleshooting should, as far as practical, be possible without support or operations personnel reading patient records.

---

## 8.7 Retention and disposal

### NFR-RET-001 — Information lifecycle
**Status:** Proposed  
The system shall support applicable retention, archival, and disposal requirements without destroying required clinical history or accountability.

### NFR-RET-002 — Different lifecycle categories
**Status:** Proposed  
Retention requirements shall be distinguishable for clinical records, audit information, technical logs, temporary workflow information, exports, and backups.

### Open questions

- **RET-Q01:** Which retention requirements apply in the first jurisdiction and provider type?
- **RET-Q02:** Is long-term archival part of the product or an external service?
- **RET-Q03:** How are legal holds or preservation exceptions handled?

---

# 9. Information requirements

This section describes properties the system must preserve about information. It deliberately does not prescribe an internal data model.

### INF-001 — Stable identity of clinically significant information
**Status:** Proposed  
Clinically significant recorded information shall remain referencable over time even when presentation, terminology, or surrounding context changes.

### INF-002 — Provenance
**Status:** Proposed  
Clinically relevant information shall retain sufficient provenance to understand its source, author or originator where applicable, time, and whether it was imported or transformed.

### INF-003 — Explicit history
**Status:** Proposed  
Clinically or legally significant history shall be represented as part of the product's information handling and shall not depend solely on infrastructure backups.

### INF-004 — Clinical time and recording time
**Status:** Proposed  
Where relevant, the system shall distinguish when something occurred clinically from when it was recorded, received, or changed in the system.

### INF-005 — Source-system context
**Status:** Proposed  
Information obtained from external systems shall retain sufficient source context to support reconciliation, interpretation, and troubleshooting.

### INF-006 — Terminology context
**Status:** Proposed  
Coded clinical information shall retain enough information about the terminology and human-readable meaning to support safe display and exchange.

### INF-007 — Unknown and absent information
**Status:** Proposed  
Where clinically significant, the system shall distinguish between concepts such as unknown, not asked, not applicable, explicitly negative, and unavailable rather than treating them as interchangeable absence.

### INF-008 — Source conflicts
**Status:** Proposed  
The system shall not silently collapse conflicting clinical information from different sources into a single apparently authoritative statement.

### INF-009 — Information status
**Status:** Proposed  
Where relevant, the system shall distinguish provisional, confirmed, corrected, entered-in-error, patient-reported, externally sourced, and otherwise qualified information.

### Open questions

- **INF-Q01:** Which information needs explicit provenance in the first release?
- **INF-Q02:** Which kinds of information may be corrected in place and which require explicit supersession or amendment?
- **INF-Q03:** Which clinical information is considered authoritative when multiple sources disagree?
- **INF-Q04:** Which jurisdictional information standards constrain the content and semantics of exchanged information?

---

# 10. Patient summary and longitudinal overview

The patient summary is a central product capability, but its exact content must be validated for each care setting.

### OVR-001 — Cross-domain summary
**Category:** Core  
**Status:** Proposed  
The system shall be able to present clinically relevant information from multiple parts of the record in a coherent summary.

### OVR-002 — Traceability to source
**Category:** Core  
**Status:** Proposed  
Summarized information shall remain traceable to its source and clinical context where necessary for interpretation.

### OVR-003 — Candidate summary content
**Category:** Core / Care-setting-specific  
**Status:** Proposed  
Candidate content includes:

- current problems and diagnoses,
- allergies and critical warnings,
- current medication treatment,
- active care plans,
- recent relevant observations and results,
- pending orders and referrals,
- upcoming activities,
- recent care contacts.

The actual content and prioritization shall depend on care setting and user role.

### OVR-004 — External-source visibility
**Category:** Core  
**Status:** Proposed  
Information from external sources shall be distinguishable from locally created or verified information when the distinction is clinically meaningful.

### Open question OVR-Q01

What qualifies as "current" information, and which person or process is responsible for maintaining that status?

---

# 11. Jurisdiction profiles

A jurisdiction profile captures requirements that arise from a particular country's or region's healthcare environment rather than from healthcare in general.

A profile may include:

- patient-identifier schemes,
- professional and organizational identity infrastructure,
- national or regional interoperability services,
- medication and prescription infrastructure,
- patient-facing national services,
- required terminology and classification systems,
- documentation-language requirements,
- access-control and audit requirements,
- consent and information-restriction mechanisms,
- mandatory reporting,
- reimbursement and coding workflows,
- retention and archival requirements,
- regulatory classification and certification obligations.

A jurisdiction profile shall not redefine a general clinical concept merely because the local healthcare system uses a particular implementation or administrative term.

### JUR-001 — Separation of general and jurisdiction-specific requirements
**Status:** Proposed  
Requirements introduced solely by one jurisdiction shall be identified as such and shall not be treated as universal product requirements without explicit justification.

### JUR-002 — Equivalent local mechanisms
**Status:** Proposed  
Where multiple jurisdictions satisfy the same general clinical need through different national mechanisms, the specification shall preserve the general need and document the local mechanism separately.

### JUR-003 — Jurisdictional conformance
**Status:** Proposed  
Each supported jurisdiction shall have an explicit conformance scope stating which national or regional services, rules, and workflows the product supports.

### Open questions

- **JUR-Q01:** Which jurisdiction should be the second case study after Sweden?
- **JUR-Q02:** What evidence is required before claiming support for a jurisdiction?
- **JUR-Q03:** Which differences belong to configuration and which require separately governed product capabilities?

---

# 12. Sweden case study and initial jurisdiction profile

This section drives the initial implementation but is not the definition of the general product.

## 12.1 Swedish patient identity

The Swedish implementation must investigate and, where required, support the relevant use of:

- personal identity numbers,
- coordination numbers,
- temporary or reserve identifiers,
- protected personal information.

### Sweden-specific open questions

- **SE-PAT-Q01:** Which source is authoritative for demographics in the first Swedish deployment?
- **SE-PAT-Q02:** Which services are used for reserve identifiers?
- **SE-PAT-Q03:** What exact behavior is required for protected personal data in search, display, messaging, export, and support workflows?

## 12.2 Swedish terminology and classifications

The Swedish profile must determine where the following are required or appropriate:

- ICD-10-SE,
- KVÅ,
- ICF,
- Snomed CT,
- national information structures and information sets published by Swedish authorities.

No decision is yet made about a single primary terminology for all clinical content.

## 12.3 National Medication List

The Swedish implementation must determine the required interaction with **Nationella läkemedelslistan (NLL)** based on the medication scope of the product and the first target care setting.

### Open questions

- **SE-MED-Q01:** Which NLL workflows are required in the first release?
- **SE-MED-Q02:** Which medication information is authoritative locally versus in NLL?
- **SE-MED-Q03:** What user workflows are required when local and national medication information differ?

## 12.4 National Patient Overview

The Swedish implementation must determine whether and how the product participates in **Nationell patientöversikt (NPÖ)**.

### Open questions

- **SE-NPO-Q01:** Is the system a producer of information to NPÖ?
- **SE-NPO-Q02:** Is the system a consumer of NPÖ information?
- **SE-NPO-Q03:** Which information sets are included?

## 12.5 1177

The Swedish implementation must determine which patient-facing functions are provided through **1177** and which, if any, are provided directly by the product.

### Open questions

- **SE-1177-Q01:** Which clinical information shall be made available through 1177 journal?
- **SE-1177-Q02:** Which patient interactions should occur through 1177 rather than a product-specific patient interface?
- **SE-1177-Q03:** What delay, review, or withholding rules apply to particular information sets?

## 12.6 Swedish identity and trust infrastructure

The first Swedish deployment must determine its requirements regarding infrastructure such as:

- HSA,
- SITHS,
- regional identity and access-management services,
- national or regional security services.

### Open questions

- **SE-IAM-Q01:** Which infrastructure is authoritative for professional identity, role, assignment, and organizational affiliation?
- **SE-IAM-Q02:** Which authorization decisions are made locally versus by shared services?

## 12.7 Swedish referrals and regional services

Referral and consultation workflows may depend on regional services and established regional practice.

### Open questions

- **SE-REF-Q01:** Which Swedish referral infrastructure must the first deployment support?
- **SE-REF-Q02:** Which parts of the referral process should be product capabilities versus integration with external services?

## 12.8 Swedish legal and regulatory profile

At minimum, the Swedish implementation shall maintain traceability against the currently applicable requirements arising from areas including:

- patient-record legislation,
- healthcare information processing and access rules,
- data protection,
- cross-provider information sharing,
- confidentiality and secrecy rules,
- medication-list legislation and connection requirements where applicable,
- national interoperability service requirements where applicable,
- medical-device or national medical-information-system regulation where applicable,
- archival and retention requirements,
- cybersecurity obligations applicable to the organization and delivery model.

The exact applicability of each source depends on intended purpose, care setting, provider type, product scope, and deployment model.

---

# 13. Regulatory and legal requirements management

This specification is not legal advice. Legal and regulatory requirements shall be maintained as traceable external requirements and validated for each jurisdiction before implementation and release.

### REG-001 — Intended purpose
**Status:** Externally driven  
The intended purpose of the product and any independently regulated capability shall be documented and version-controlled.

### REG-002 — Regulatory classification
**Status:** Externally driven  
A documented assessment shall determine whether the product or any capability is subject to medical-device, clinical-software, national information-system, or other sector-specific regulation in each supported jurisdiction.

### REG-003 — Scope boundaries
**Status:** Proposed  
Where different capabilities have materially different regulatory obligations, their product and governance boundaries shall be made explicit.

### REG-004 — Compliance traceability
**Status:** Proposed  
Externally imposed requirements shall be traceable to the product requirements, evidence, controls, and release scope that satisfy them.

### Open questions

- **REG-Q01:** Who is the legal manufacturer or equivalent responsible entity for the first commercial deployment?
- **REG-Q02:** Which capabilities may independently trigger medical-device regulation?
- **REG-Q03:** Which quality-management obligations apply to the first release?
- **REG-Q04:** Which regulatory assessments must be repeated for each jurisdiction?

---

# 14. Clinical risk management and patient safety

### SAFE-001 — Clinical risk analysis
**Status:** Proposed  
Capabilities that can affect patient care shall be subject to structured clinical risk analysis throughout the product lifecycle.

### SAFE-002 — Risk register
**Status:** Proposed  
Identified hazards and risks should be traceable to causes, controls, verification evidence, and residual risk.

### SAFE-003 — Safety-control requirements
**Status:** Proposed  
Requirements that act as safety controls shall be identifiable so that they are not removed or weakened without reassessment.

### SAFE-004 — Failure modes
**Status:** Proposed  
Risk analysis shall consider both incorrect behavior and absence or delay of expected behavior. Candidate failure modes include:

- wrong-patient documentation or action,
- wrong medication or dose,
- lost or overwritten clinical documentation,
- delayed or missed critical result,
- missed allergy or risk information,
- incorrect patient matching,
- duplicate orders or actions,
- stale clinical information presented as current,
- incorrect or missing external information,
- inappropriate information access,
- inability to access critical information during care,
- misleading aggregation of conflicting information.

### SAFE-005 — Human factors
**Status:** Proposed  
Usability problems that can cause or contribute to clinical error shall be treated as patient-safety risks, not only as user-experience defects.

### SAFE-006 — Configuration safety
**Status:** Proposed  
Configuration capable of materially changing clinical behavior shall be included in safety assessment, governance, testing, and audit requirements.

---

# 15. Testing and verification

### TST-001 — Requirements traceability
**Status:** Proposed  
Each production requirement shall be traceable to implementation evidence and verification appropriate to its risk and nature.

### TST-002 — Automated testing
**Status:** Proposed  
Automated tests shall be used for clinically important rules, authorization behavior, interoperability contracts, and regression-critical workflows where technically appropriate.

### TST-003 — Negative authorization testing
**Status:** Proposed  
Authorization and privacy controls shall include tests demonstrating that prohibited access is denied, not only that permitted access succeeds.

### TST-004 — Integration failure testing
**Status:** Proposed  
External integrations shall be tested for normal behavior and relevant failure conditions such as timeouts, duplicates, delayed responses, inconsistent responses, and retries.

### TST-005 — Migration verification
**Status:** Proposed  
Migration testing shall verify content, relationships, history, terminology, provenance, and other migrated properties according to the migration scope.

### TST-006 — Performance testing
**Status:** Proposed  
Performance testing shall use realistic longitudinal records, user concurrency, and integration activity rather than only small or empty test records.

### TST-007 — Recovery testing
**Status:** Proposed  
Backup, restore, continuity, and disaster-recovery capabilities shall be verified through actual recovery exercises appropriate to the deployment.

### TST-008 — Clinical workflow validation
**Status:** Proposed  
Representative users shall validate critical end-to-end workflows in realistic scenarios before production use.

### TST-009 — Configuration verification
**Status:** Proposed  
Safety-relevant deployment configuration shall be verified before activation and after material change.

---

# 16. Migration

### MIG-001 — Source traceability
**Status:** Proposed  
Migrated clinical information shall retain sufficient indication of its source where this is clinically, legally, or operationally important.

### MIG-002 — Incomplete or unsafe mapping
**Status:** Proposed  
Information that cannot be safely mapped shall not be silently discarded or reinterpreted. Exceptions shall be made explicit and reviewed.

### MIG-003 — Preservation of original representation
**Status:** Proposed  
Where structured migration cannot fully preserve meaning, the original representation may need to remain available alongside migrated information.

### MIG-004 — Migration reporting
**Status:** Proposed  
Each migration shall produce verifiable evidence of scope, mapping, exceptions, reconciliation, and outcome.

### MIG-005 — Patient-identity reconciliation
**Status:** Proposed  
Migration shall explicitly address patient matching and duplicate risk rather than assuming source and target identities are equivalent.

### Open questions

- **MIG-Q01:** Which existing systems must the first implementation migrate from?
- **MIG-Q02:** How much historical information must be migrated as structured information?
- **MIG-Q03:** Which information can remain available only as historical documents?
- **MIG-Q04:** What responsibility remains with the previous system after cutover?

---

# 17. Master list of open product questions

This section acts as a decision backlog. Detailed questions remain in their relevant sections; the following are the major product decisions.

## 17.1 Product and care settings

- **Q-PROD-001:** What is the first target care setting?
- **Q-PROD-002:** Is the first release intended to be a complete clinical information system or a narrower clinical core?
- **Q-PROD-003:** Which professional roles must be supported on day one?
- **Q-PROD-004:** Is inpatient care included in the first release?
- **Q-PROD-005:** Is emergency care included?
- **Q-PROD-006:** Is primary care included?
- **Q-PROD-007:** Does psychiatry require dedicated functionality in the initial scope?
- **Q-PROD-008:** Is scheduling included?
- **Q-PROD-009:** Is operating-theatre planning included?
- **Q-PROD-010:** Are billing, reimbursement, and revenue-cycle capabilities included?

## 17.2 Product generality

- **Q-GEN-001:** Which capabilities must be identical across jurisdictions to qualify as part of the product core?
- **Q-GEN-002:** Which variation should be handled as jurisdiction profiles?
- **Q-GEN-003:** Which variation should be handled as care-setting-specific capability?
- **Q-GEN-004:** Which variation should be deployment configuration?
- **Q-GEN-005:** Which second jurisdiction should be used to challenge assumptions derived from Sweden?
- **Q-GEN-006:** What evidence is sufficient to conclude that a concept is general rather than Sweden-specific?

## 17.3 Clinical information

- **Q-INF-001:** Which clinical information must be structured in the first release?
- **Q-INF-002:** Which terminology and classification systems are required for the first use cases?
- **Q-INF-003:** How are conflicting sources reconciled?
- **Q-INF-004:** Which information states and provenance distinctions must users be able to see?
- **Q-INF-005:** Which clinical information must remain available in its original representation?

## 17.4 Interoperability

- **Q-INT-001:** Which external systems are mandatory for the first deployment?
- **Q-INT-002:** Which national Swedish services are mandatory for the first deployment?
- **Q-INT-003:** Which international standards must be supported initially?
- **Q-INT-004:** Which external systems remain authoritative for their information?
- **Q-INT-005:** Which conformance and certification programs must be passed before production use?

## 17.5 Security and privacy

- **Q-SEC-001:** Which identity and credential infrastructure applies to the first deployment?
- **Q-SEC-002:** Which factors determine authorization to patient information?
- **Q-SEC-003:** Which patient restrictions and consent mechanisms are enforced locally versus externally?
- **Q-SEC-004:** Which access and audit information must be retained, and for how long?
- **Q-SEC-005:** Under what controlled circumstances may support personnel access patient information?
- **Q-SEC-006:** How is access to one's own or a related person's record handled when healthcare personnel are also patients?

## 17.6 Regulation and patient safety

- **Q-REG-001:** What is the formal intended purpose of the first product release?
- **Q-REG-002:** Which parts of the product may be regulated medical software?
- **Q-REG-003:** Which quality-system and lifecycle requirements apply?
- **Q-REG-004:** How are locally configured clinical rules governed and validated?
- **Q-REG-005:** How are regulatory requirements separated between the general product and a jurisdiction-specific deployment?

## 17.7 Operation

- **Q-OPS-001:** Which delivery models must be supported?
- **Q-OPS-002:** What availability commitments are required?
- **Q-OPS-003:** What recovery objectives are required?
- **Q-OPS-004:** Is offline operation required?
- **Q-OPS-005:** What scale must the first release support?
- **Q-OPS-006:** How are clinically significant upgrades introduced safely?

## 17.8 AI

- **Q-AI-001:** Is AI-assisted documentation in scope?
- **Q-AI-002:** May the system generate summaries of clinical information?
- **Q-AI-003:** May AI generate suggestions concerning diagnosis, medication, investigations, or treatment?
- **Q-AI-004:** Which AI capabilities are clinical decision support and which are administrative assistance?
- **Q-AI-005:** What verification, provenance, versioning, and human-review requirements apply to AI-generated clinical content?

---

# 18. Recommended next specification work

The next iteration should deepen requirements through real clinical workflows rather than through implementation design.

Recommended sequence:

1. select the first care setting and representative user groups,
2. define 10–20 end-to-end clinical workflows in plain language,
3. identify the information needed, created, changed, and handed over in each workflow,
4. identify safety-critical decisions and failure modes in each workflow,
5. identify which parts of each workflow are general, care-setting-specific, Swedish, or deployment-specific,
6. establish the initial Swedish external-system and national-service scope,
7. define measurable non-functional expectations for the selected workflows,
8. establish the initial regulatory and clinical-risk scope,
9. turn validated workflow needs into more precise and testable requirements.

Architecture, internal information models, API design, and technical decomposition should follow only when the workflow and requirement basis is strong enough to constrain those decisions meaningfully.

---

# 19. Swedish reference sources to track

The following are starting points for the Swedish case study. Applicability and current wording must be checked for each relevant release.

1. **Patient Data Act (Patientdatalag 2008:355), Swedish Parliament**  
   https://www.riksdagen.se/sv/dokument-och-lagar/dokument/svensk-forfattningssamling/patientdatalag-2008355_sfs-2008-355

2. **HSLF-FS 2016:40 — patient records and processing of personal data in healthcare, National Board of Health and Welfare**  
   https://www.socialstyrelsen.se/kunskapsstod-och-regler/regler-och-riktlinjer/foreskrifter-och-allmanna-rad/konsoliderade-foreskrifter/201640-om-journalforing-och-behandling-av-personuppgifter-i-halso--och-sjukvarden/

3. **Information security for healthcare providers, Swedish Authority for Privacy Protection (IMY)**  
   https://www.imy.se/verksamhet/dataskydd/dataskydd-pa-olika-omraden/vard/informationssakerhet--for-vardgivare/

4. **Monitoring access to patient information, IMY**  
   https://www.imy.se/verksamhet/dataskydd/dataskydd-pa-olika-omraden/vard/informationssakerhet--for-vardgivare/kontroll-av-atkomst-till-uppgifter---for-vardgivare/

5. **Assignment of access rights to patient information, IMY**  
   https://www.imy.se/verksamhet/dataskydd/dataskydd-pa-olika-omraden/vard/informationssakerhet--for-vardgivare/tilldelning-av-behorighet-till-uppgifter-om-patienter--for-vardgivare/

6. **National Medication List — requirements for connecting healthcare systems, Swedish eHealth Agency**  
   https://samarbetsyta.ehalsomyndigheten.se/handboken/latest/utveckla-mot-e-haelsomyndighetens-tjaenster/information-stoed-och-krav-per-delsystem/nationella-laekemedelslistan-nll/krav-pa-anslutande-system-nll/sammanstaellning-av-krav/sammanstaellning-av-krav-vard

7. **National Service Platform, Inera**  
   https://www.inera.se/tjanster/arkitektur-och-digital-infrastruktur/nationella-tjansteplattformen/

8. **1177 Journal, Inera**  
   https://www.inera.se/journalen

9. **National Patient Overview (NPÖ), Inera**  
   https://www.inera.se/tjanster/alla-tjanster-a-o/npo---nationell-patientoversikt/

10. **National information structure and national information sets, National Board of Health and Welfare**  
    https://informationsstruktur.socialstyrelsen.se/

11. **National Medical Information Systems (NMI), Swedish Medical Products Agency**  
    https://www.lakemedelsverket.se/sv/medicinteknik/tillverka/nationella-medicinska-informationssystem

---

# 20. Change log

| Version | Date | Change |
|---|---|---|
| 0.1 | 2026-09-19 | Initial Swedish-oriented structured specification. |
| 0.2 | 2026-09-19 | Reframed as a general clinical information system with Sweden as the initial case study. Translated to English. Removed premature architecture, system-context, and internal data-model proposals. Added requirement categories for core, care-setting, jurisdiction, and deployment variation. |
