# Clinical requirements

[Master specification](../SPECIFICATION.md) · Draft supporting specification.

The [coverage map](coverage.md) includes domains still awaiting detailed requirements. Conditional wording such as "if in scope" refers to the selected module or deployment; it does not exclude that domain from the product ambition.

## Patient identity and demographics

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

## Organization, care context, and encounters

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
- **ENC-Q02:** Which scheduling responsibilities belong in product modules versus external services?
- **ENC-Q03:** Which bed and capacity-management responsibilities belong in product modules versus external services?
- **ENC-Q04:** How should overlapping and cross-organizational care processes be represented to users?

---

## Clinical documentation

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

**Verify:** Confirm reviewed content. The confirmation identifies the user, time, and exact versions and presentation reviewed, which remain retrievable after a template change. If that content or a reference required to be current changes before confirmation, confirmation fails visibly and records no attestation; confirming after re-review succeeds. Fixtures: [case 1](record-model-comparison.md#case-1--concurrent-signing).  
**Open:** [DOC-Q01](#clinical-documentation), [INF-Q02](#information-requirements).

### DOC-006 — Countersigning or supervisory confirmation
**Category:** Care-setting-specific / Jurisdiction-specific  
**Status:** Decision required  
The system shall support countersigning or supervisory confirmation where required.

### DOC-007 — Correction and amendment
**Category:** Core  
**Status:** Proposed  
The system shall support correction and amendment without silently destroying or rewriting previously recorded clinical information.

**Verify:** Correct an item that has been reviewed or confirmed. The earlier revision remains retrievable and unchanged, references to it still resolve, and the new revision identifies the one it supersedes. The new revision is not presented as reviewed or confirmed until it is. Fixtures: [case 2](record-model-comparison.md#case-2--corrected-result-after-review).  
**Open:** [INF-Q02](#information-requirements), [DOC-Q02](#clinical-documentation).

### DOC-008 — Change history
**Category:** Core  
**Status:** Proposed  
It shall be possible to determine relevant previous states of clinical documentation, who made a change, and when it occurred.

**Verify:** After sequential and concurrent changes to an item, its history lists every committed revision with author and recording time, and each earlier state is retrievable unchanged. Rejected or failed changes add no revision.  
**Open:** [DOC-Q02](#clinical-documentation), [DOC-Q04](#clinical-documentation).

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

## Clinical facts and health information

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
- **CLI-Q02:** Which terminology and classification systems are required in the first jurisdictions and use cases?
- **CLI-Q03:** Who is responsible for reconciling conflicting clinical information from different sources?
- **CLI-Q04:** Which information is allowed to be provisional, patient-reported, imported, or unverified?

---

## Medications

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

## Orders, investigations, and results

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

**Verify:** Review a result, then receive its correction twice. The review stays linked to the version reviewed, the correction is current but unreviewed, and exactly one reassessment is assigned to a responsible recipient. Interrupt processing between storing the correction and assigning reassessment; after recovery, the outcome is the same. Fixtures: [case 2](record-model-comparison.md#case-2--corrected-result-after-review).  
**Open:** [ORD-Q02](#orders-investigations-and-results), [INF-Q03](#information-requirements).

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

## Referrals and consultations

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

## Care plans, tasks, and clinical workflow

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

**Verify:** Hand over pending items with their clinical context. Each item always has exactly one accountable owner; responsibility moves from the sender only when the receiver accepts that item or a defined fallback applies. Delivery receipt, rejection, or acceptance of a superseded handover does not move it, and the sender sees unaccepted items as outstanding. A result corrected after transfer reaches the owner at that time. Fixtures: [case 3](record-model-comparison.md#case-3--hospital-to-home-care-handover).  
**Open:** [WF-Q04](#care-plans-tasks-and-clinical-workflow), [INT-Q03](platform-requirements.md#interoperability).

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

## Clinical decision support

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

## Consent, restrictions, and patient choices

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

## Patient access and participation

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

## Information requirements

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

## Patient summary and longitudinal overview

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
