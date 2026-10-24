# Platform requirements

[Master specification](../SPECIFICATION.md) · Draft supporting specification.

## Interoperability

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

**Verify:** Retry after a lost acknowledgement, deliver a message twice, and deliver an older source revision after a newer one. Each intended change takes effect once under one operation identity, and the older revision does not replace newer state. Unconfirmed delivery stays visible until reconciled. After a failure partway through an exchange, the outcome is complete or held in a visible intermediate state that recovery resolves.  
**Open:** [INT-Q03](#interoperability), [INF-Q03](clinical-requirements.md#information-requirements).

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

## Identity, authentication, and authorization

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

**Verify:** For each of job function, organizational context, care relationship, and purpose, and for a policy combining them, a request that differs from a permitted one only in a restricted factor is denied. The denial holds for direct reads, search, export, APIs, and background work, and derived summaries and counts disclose none of the denied content.  
**Open:** [Q-SEC-002](decisions.md#security-and-privacy), [IAM-Q04](#identity-authentication-and-authorization).

### IAM-004 — Context-sensitive authorization
**Category:** Core  
**Status:** Proposed  
Authorization shall be capable of considering both relatively stable user attributes and the context of the current access request.

**Verify:** One user with unchanged role and affiliation is permitted or denied according to the request's patient, care relationship, unit, and declared purpose. Decisions use the context at disclosure: after a care relationship ends or a restriction is added, cached views, queued exports, and retried deliveries no longer disclose the affected information. Fixtures: [case 3](record-model-comparison.md#case-3--hospital-to-home-care-handover).  
**Open:** [IAM-Q02](#identity-authentication-and-authorization), [IAM-Q03](#identity-authentication-and-authorization).

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

**Verify:** For each of employment, assignment, role, organizational affiliation, and care responsibility, record a change at its authoritative source, then repeat a request the earlier state permitted. Within the deployment's declared maximum delay, including in sessions opened before the change, the request is decided on the new state. A role change leaves no permission held only through the previous role, and a dated change takes effect at its stated time.  
**Open:** [IAM-Q01](#identity-authentication-and-authorization), [IAM-Q03](#identity-authentication-and-authorization).

### Open questions

- **IAM-Q01:** Which identity infrastructure is used in the first deployment?
- **IAM-Q02:** Which access decisions are controlled by the product and which by external policy services?
- **IAM-Q03:** How are temporary assignments, on-call duties, trainees, and consultants handled?
- **IAM-Q04:** How is access justified when no explicit care relationship exists but legitimate work requires access?

---

## Audit, access logging, and monitoring

### AUD-001 — Patient-information access logging
**Category:** Core / Jurisdiction-specific  
**Status:** Proposed  
The system shall record access to patient information with sufficient detail to support investigation, accountability, and jurisdictional monitoring requirements.

**Verify:** Run scripted accesses through every access path, including summaries and background work. Every disclosure has a log entry, and no entry records a disclosure that did not happen. If the log cannot be written, the access is refused or follows a declared fallback whose entries reach the log after recovery; nothing is disclosed without an eventual entry. Disclosures completed before an abrupt restart remain logged. Each supported jurisdiction profile's access-logging obligations trace to logged fields, demonstrated by a sample investigation.  
**Open:** [AVL-Q04](#availability-and-continuity), [Q-SEC-004](decisions.md#security-and-privacy).

### AUD-002 — Access-log context
**Category:** Core  
**Status:** Proposed  
Access logging shall capture the user, patient, time, and relevant organizational or technical context needed to understand the access.

**Verify:** Access one patient's information by direct read, search, export, summary, API client, and background job, and make one denied request. Each log entry identifies the individual user or technical identity and anyone acted for; the patient; time; action and outcome; the information disclosed; the access path; and the care unit, care relationship, declared purpose, and policy version the decision used. A reviewer can establish who saw what, when, and on what basis without reading the record's clinical content.  
**Open:** [AUD-Q04](#audit-access-logging-and-monitoring), [IAM-Q02](#identity-authentication-and-authorization).

### AUD-003 — Protection of audit information
**Category:** Core  
**Status:** Proposed  
Audit and access records shall be protected against unauthorized alteration and deletion.

**Verify:** Attempt to alter and delete existing audit and access records as a clinical user, a system administrator, a technical identity, and with the application's runtime database identity. Each attempt is refused and recorded, and the records are unchanged. A change made directly in storage is detected, with the affected records identified, at the tamper-evidence level the deployment declares. Disposal after the retention period removes only eligible records and is itself recorded.  
**Open:** [AUD-Q02](#audit-access-logging-and-monitoring), [AUD-Q03](#audit-access-logging-and-monitoring).

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

## Administration and configuration

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

## Modularity and configuration

### MOD-001 — Selectable capabilities
**Category:** Core / Care-setting-specific / Deployment-specific  
**Status:** Proposed  
Deployments shall support module selection according to declared workflow dependencies.

**Verify:** Remove an optional module outside the selected workflows; configuration validation and those workflows still pass.  
**Open:** [MOD-Q01](#modularity-and-configuration), [MOD-Q02](#modularity-and-configuration), [MOD-Q05](#modularity-and-configuration).

### MOD-002 — Module responsibilities and dependencies
**Category:** Core  
**Status:** Proposed  
Each module shall declare its workflows, dependencies, information ownership, and handover responsibilities.

**Verify:** Review each module boundary: authoritative sources, pending-work owners, and completion conditions are identified.  
**Open:** [MOD-Q02](#modularity-and-configuration).

### MOD-003 — Validation of combinations
**Category:** Core / Deployment-specific  
**Status:** Proposed  
Configuration validation shall prevent activation of workflows with missing dependencies or incompatible modules, profiles, integrations, or settings.

**Verify:** A valid combination passes; removing a dependency or introducing a declared conflict blocks activation and identifies the cause.  
**Open:** [MOD-Q05](#modularity-and-configuration).

### MOD-004 — Configuration scope and conflicts
**Category:** Core / Jurisdiction-specific / Deployment-specific  
**Status:** Proposed  
Settings shall declare scope, constraints, change authority, and contributing profiles. Required controls and applicable obligations shall constrain local overrides.

**Verify:** Authorized users can inspect effective settings and their sources. Unauthorized changes and overrides that violate declared constraints are rejected.  
**Open:** [ADM-Q02](#administration-and-configuration), [MOD-Q03](#modularity-and-configuration).

### MOD-005 — Governed extension
**Category:** Core / Care-setting-specific / Jurisdiction-specific  
**Status:** Proposed  
Extensions shall declare ownership, version, compatibility, and verification requirements, and preserve shared clinical requirements.

**Verify:** Each extension version identifies its owner and dependencies and passes checks for shared requirements in supported combinations.  
**Open:** [MOD-Q04](#modularity-and-configuration), [MOD-Q05](#modularity-and-configuration), [Q-GEN-001](decisions.md#product-generality).

### MOD-006 — Safe capability and configuration changes
**Category:** Core / Deployment-specific  
**Status:** Proposed  
Capability, profile, and setting changes shall preserve required history and define the disposition of pending work, access, and dependent workflows before activation.

**Verify:** Change review includes impact, verification, and recovery evidence. Exercise recovery after a clinical action; history remains available and the action is reconciled, not erased by restoring settings.  
**Open:** [MOD-Q05](#modularity-and-configuration), [MOD-Q06](#modularity-and-configuration).

### MOD-007 — Reproducible configuration context
**Category:** Core / Deployment-specific  
**Status:** Proposed  
Clinical actions shall retain references to the effective module, profile, and safety-relevant configuration versions.

**Verify:** After an upgrade, retrieve a prior action's configuration; it resolves to the original effective versions and values.  
**Open:** [MOD-Q01](#modularity-and-configuration), [MOD-Q05](#modularity-and-configuration).

### Open questions

- **MOD-Q01:** What is the minimum shared foundation for the first supported workflows?
- **MOD-Q02:** Which capabilities form the first modules, and which dependencies are necessary?
- **MOD-Q03:** Which variations can be expressed through configuration and which require an extension or integration?
- **MOD-Q04:** Who maintains and validates modules and profiles, and are third-party extensions in scope?
- **MOD-Q05:** Which combinations will be supported, and how will their compatibility and lifecycle be governed?
- **MOD-Q06:** What behavior is required when an external capability becomes unavailable during a workflow?

---

## Non-functional requirements

### Information security

#### NFR-SEC-001 — Confidentiality, integrity, availability, and accountability
**Status:** Proposed  
The product and its operation shall protect the confidentiality, integrity, availability, and accountability of patient and healthcare information.

#### NFR-SEC-002 — Protection in transit
**Status:** Proposed  
Sensitive information and credentials shall be protected in transit using current accepted security mechanisms appropriate to the deployment.

#### NFR-SEC-003 — Protection at rest
**Status:** Proposed  
Protection of sensitive information at rest shall be included in the security requirements. Exact mechanisms and key-management requirements are not specified here.

#### NFR-SEC-004 — Secret management
**Status:** Proposed  
Secrets and cryptographic credentials shall be managed so they are not exposed through source code or ordinary unsecured configuration.

#### NFR-SEC-005 — Secure development lifecycle
**Status:** Proposed  
The product shall be developed using a documented secure-development process including vulnerability management, dependency management, security testing, and incident response.

#### NFR-SEC-006 — Threat analysis
**Status:** Proposed  
Security threats to clinically or legally significant workflows shall be assessed and revisited when material product changes occur.

---

### Availability and continuity

#### NFR-AVL-001 — Availability targets
**Status:** Decision required  
Measurable availability targets shall be established per critical capability and care context before production commitments are made.

#### NFR-AVL-002 — Resilience of critical workflows
**Status:** Proposed  
Critical clinical workflows shall not depend on avoidable single technical failure points without an appropriate fallback or recovery mechanism.

#### NFR-AVL-003 — Recovery objectives
**Status:** Decision required  
Recovery point and recovery time objectives shall be established according to information and service criticality.

#### NFR-AVL-004 — Downtime procedures
**Status:** Proposed  
Each deployment shall have a defined way to continue clinically necessary work during system or network disruption.

#### Open questions

- **AVL-Q01:** What availability targets apply to the first care setting?
- **AVL-Q02:** Is read access required during a major central outage?
- **AVL-Q03:** Is client-side offline documentation required?
- **AVL-Q04:** Which functions may degrade safely during partial failure?

---

### Performance

#### NFR-PERF-001 — Interactive response
**Status:** Decision required  
Measurable response-time targets shall be established for common clinical actions such as opening a patient, viewing a summary, searching, saving documentation, signing, and ordering.

#### NFR-PERF-002 — Large longitudinal records
**Status:** Proposed  
Performance shall remain acceptable for patients with extensive longitudinal history.

#### NFR-PERF-003 — Realistic load
**Status:** Decision required  
Capacity targets shall be defined in terms meaningful to the intended deployment, including concurrent users, patient population, information volume, workflow activity, and integration traffic.

---

### Scalability

#### NFR-SCL-001 — Scale without loss of correctness
**Status:** Proposed  
The system shall be able to scale without compromising clinical information integrity, authorization, or traceability.

#### Open questions

- **SCL-Q01:** What population and organizational scale must the first release support?
- **SCL-Q02:** Must one deployment support a single provider, multiple providers, a region, or a national-scale service?

---

### Usability and accessibility

#### NFR-UX-001 — Clinical efficiency
**Status:** Proposed  
Common workflows shall minimize unnecessary steps and cognitive burden without weakening safety controls.

#### NFR-UX-002 — Critical information
**Status:** Proposed  
Information representing immediate clinical risk shall be presented clearly and consistently in relevant contexts.

#### NFR-UX-003 — Efficient professional interaction
**Status:** Proposed  
The system should support efficient interaction methods suitable for high-volume professional use, including keyboard-centric workflows where appropriate.

#### NFR-UX-004 — Accessibility
**Status:** Decision required  
Applicable accessibility requirements shall be established for each user-facing surface and jurisdiction.

#### NFR-UX-005 — Supported device classes
**Status:** Decision required  
Supported device classes and interaction contexts shall be defined by user role and workflow rather than assumed globally.

---

### Operability and technical monitoring

#### NFR-OPS-001 — Technical monitoring
**Status:** Proposed  
The system shall expose sufficient technical health information to operate the service safely, including availability, latency, errors, queues, and resource use where relevant.

#### NFR-OPS-002 — Cross-system troubleshooting
**Status:** Proposed  
Operational events shall be traceable across system boundaries without unnecessarily exposing patient-identifying information in technical logs.

#### NFR-OPS-003 — Operational alerting
**Status:** Proposed  
Failures that threaten critical clinical or integration workflows shall be detectable and capable of triggering operational response.

#### NFR-OPS-004 — Support without routine record access
**Status:** Proposed  
Normal operation and troubleshooting should, as far as practical, be possible without support or operations personnel reading patient records.

---

### Retention and disposal

#### NFR-RET-001 — Information lifecycle
**Status:** Proposed  
The system shall support applicable retention, archival, and disposal requirements without destroying required clinical history or accountability.

#### NFR-RET-002 — Different lifecycle categories
**Status:** Proposed  
Retention requirements shall be distinguishable for clinical records, audit information, technical logs, temporary workflow information, exports, and backups.

#### Open questions

- **RET-Q01:** Which retention requirements apply in the first jurisdiction and provider type?
- **RET-Q02:** Is long-term archival part of the product or an external service?
- **RET-Q03:** How are legal holds or preservation exceptions handled?

---

### Internationalization and localization

#### NFR-LOC-001 — Interface and clinical language
**Category:** Core / Jurisdiction-specific / Deployment-specific  
**Status:** Proposed  
Interface, documentation, and terminology display languages shall be independently specified, with supported languages and fallback rules. [DOC-012](clinical-requirements.md#doc-012--language-requirements) governs documentation-language constraints.

**Verify:** Switching interface language leaves stored clinical content unchanged; missing translations follow the declared fallback.  
**Open:** [LOC-Q01](#internationalization-and-localization), [LOC-Q03](#internationalization-and-localization).

#### NFR-LOC-002 — Identity and contact conventions
**Category:** Core / Jurisdiction-specific  
**Status:** Proposed  
Names, addresses, contact details, and identifiers shall follow the selected jurisdiction's conventions, preserving identifier scheme and issuer.

**Verify:** A supported non-Swedish profile accepts its identity formats without Swedish fields; identical identifiers from different schemes or issuers remain distinguishable.  
**Open:** [PAT-Q02](clinical-requirements.md#patient-identity-and-demographics), [LOC-Q02](#internationalization-and-localization).

#### NFR-LOC-003 — Time, numbers, and units
**Category:** Core / Jurisdiction-specific / Deployment-specific  
**Status:** Proposed  
Localized entry and display shall preserve clinical time, numeric values, source units, and required precision. Conversions shall identify the displayed unit.

**Verify:** Cases using supported date, decimal, time-zone, and unit conventions retain source values and time context. Ambiguous input is resolved before saving.  
**Open:** [LOC-Q04](#internationalization-and-localization).

#### NFR-LOC-004 — Localization verification
**Category:** Core / Jurisdiction-specific / Deployment-specific  
**Status:** Proposed  
Localization validation shall cover declared languages, writing systems, and layout directions in representative workflows.

**Verify:** Evidence covers safety labels, entry, search, output, and applicable accessibility criteria for each supported localization.  
**Open:** [LOC-Q01](#internationalization-and-localization), [LOC-Q02](#internationalization-and-localization), [LOC-Q03](#internationalization-and-localization); accessibility criteria under [NFR-UX-004](#nfr-ux-004--accessibility).

#### Open questions

- **LOC-Q01:** Which interface, documentation, and terminology languages are required in the first Swedish deployment?
- **LOC-Q02:** Which language and regional conventions should the second jurisdiction test?
- **LOC-Q03:** Which translation and terminology resources require clinical review, and who maintains them?
- **LOC-Q04:** Which workflows require unit conversion or users working across time zones?

---

## Jurisdiction profiles

Profiles cover local identity, terminology, documentation language, interoperability, prescribing, patient services, access, consent, audit, reporting, reimbursement, retention, and certification requirements.

A deployment may combine national, regional, and care-setting profiles. [MOD-003](#mod-003--validation-of-combinations) and [MOD-004](#mod-004--configuration-scope-and-conflicts) govern compatibility and conflicts; [ADM-005](#adm-005--configuration-boundaries) protects shared clinical meaning.

### JUR-001 — Separation of general and jurisdiction-specific requirements
**Status:** Proposed  
Requirements introduced solely by one jurisdiction shall be identified as such and shall not be treated as universal product requirements without explicit justification.

### JUR-002 — Equivalent local mechanisms
**Status:** Proposed  
Where multiple jurisdictions satisfy the same general clinical need through different national mechanisms, the specification shall preserve the general need and document the local mechanism separately.

### JUR-003 — Jurisdictional conformance
**Status:** Proposed  
Each supported jurisdiction shall have an explicit conformance scope stating which national or regional services, rules, and workflows the product supports.

### JUR-004 — Versioned applicability and evidence
**Category:** Jurisdiction-specific / Deployment-specific  
**Status:** Proposed  
Profiles shall retain versioned applicability records: sources, effective dates, scope, required capabilities, exclusions, and verification evidence.

**Verify:** Inspect those fields; change an applicable source and confirm that affected profiles, configurations, and workflows receive an impact assessment.  
**Open:** [JUR-Q02](#jurisdiction-profiles).

### Open questions

- **JUR-Q01:** Which jurisdiction should be the second case study after Sweden?
- **JUR-Q02:** What evidence is required before claiming support for a jurisdiction?
- **JUR-Q03:** Which differences belong to configuration and which require separately governed product capabilities?
