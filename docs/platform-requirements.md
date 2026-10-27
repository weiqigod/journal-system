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

**Verify:** Using the product's monitoring function or its export, an authorized reviewer lists access by patient, by user, and by care unit for a chosen period. Consecutive exports cover the log without gaps or duplicates, reconcile with its entry counts, and use a documented, versioned format. Only monitoring roles can retrieve these records, and each retrieval is itself logged.  
**Open:** [AUD-Q01](#audit-access-logging-and-monitoring), [AUD-Q04](#audit-access-logging-and-monitoring).

### AUD-005 — Risk-based review
**Category:** Core  
**Status:** Proposed  
Monitoring should be able to identify patterns that may warrant review, such as unusual timing, exceptional access, broad access, or access across unexpected organizational boundaries.

**Verify:** Seed ordinary access with known cases of unusual timing, exceptional access, broad access, and access across unexpected organizational boundaries. The product's monitoring, or a reference rule set applied to its export, flags every seeded case for review and identifies the entries behind it. Flags raised by the ordinary access stay within the deployment's declared review volume.  
**Open:** [AUD-Q01](#audit-access-logging-and-monitoring), [IAM-Q04](#identity-authentication-and-authorization).

### AUD-006 — Administrative and configuration audit
**Category:** Core  
**Status:** Proposed  
Changes to permissions, security settings, clinical configuration, terminology, decision-support rules, and other safety-relevant configuration shall be auditable.

**Verify:** Change one item in each of these classes, and in every other class the deployment declares safety-relevant, through each change path: the administration interface, the API, configuration import or deployment, and terminology update. Each change has an audit entry identifying the individual or technical identity and anyone acted for; the time; the item; its prior and new values or versions; the approval or reason where the deployment requires one; and when the change takes effect. Secret values are recorded only as identifiers or fingerprints. Refused and failed changes are recorded with their outcome, and no entry records a change that did not happen. Replaying the entries in order from a known baseline reproduces the configuration in effect. A change made directly in storage, bypassing these paths, is detected at the tamper-evidence level the deployment declares.  
**Open:** [ADM-Q02](#administration-and-configuration), [AUD-Q03](#audit-access-logging-and-monitoring).

### AUD-007 — Patient access to access history
**Category:** Core / Jurisdiction-specific  
**Status:** Proposed  
The system shall produce a patient's access history from the access log. The jurisdiction profile and deployment configuration determine whether patients and representatives receive it, through which channel, which entries it includes, how staff are identified, and after what delay.

**Verify:** Under each supported configuration, request one patient's access history for a chosen period. It contains every logged access to that patient in the period except entries the configuration excludes, and nothing about other patients. Staff are identified at the configured level of detail, and entries newer than the configured delay are omitted. Excluded entries remain in the access log, and each disclosure is itself logged with the configuration version it used. With the patient channel disabled, patient requests are refused while authorized staff can still produce the history. A representative receives it only when both the configuration and their authorization allow it.  
**Open:** [AUD-Q05](#audit-access-logging-and-monitoring), [SE-1177-Q04](sweden.md#1177).

### Open questions

- **AUD-Q01:** Is access-monitoring functionality part of the product or an external security capability?
- **AUD-Q02:** What retention periods apply to different forms of audit information?
- **AUD-Q03:** What level of tamper evidence is required?
- **AUD-Q04:** Which audit data may itself contain sensitive patient information?
- **AUD-Q05:** Which channels, entries, staff details, exclusions, and delays for patient access history does each jurisdiction profile require or permit?

---

## User surfaces and assistants

People use the product through a graphical client and through AI assistants that act on their behalf. Both are clients of one action interface; the rules live behind it, not in either surface. The form of that interface, its protocol, and the technology behind it remain open.

Informative: in 1.7 million voluntary safety reports from Pennsylvania and a multi-hospital system in 2013–2016, 557 explicitly suggested that EHR usability contributed to possible patient harm, concentrated in order placement, medication administration, review of results, and documentation ([Howe et al., JAMA 2018](https://pubmed.ncbi.nlm.nih.gov/29584833/)). In a randomized trial covering 901,776 ordering sessions, requiring prescribers to re-enter the patient's identity before ordering reduced wrong-patient orders (odds ratio 0.60) more than a confirmation alert did (0.84) ([Adelman et al., JAMIA 2013](https://psnet.ahrq.gov/issue/understanding-and-preventing-wrong-patient-electronic-orders-randomized-controlled-trial)).

### SUR-001 — Single action interface
**Category:** Core  
**Status:** Proposed  
Every action a user can take, and every read of patient information, shall be available through one product interface that applies authorization, validation, workflow rules, and audit. Graphical clients, assistants, integrations, and administration tools act only through it; no surface holds privileges or rules of its own.

**Verify:** For each action in an implemented workflow, act as the same user in the same context through the graphical client and through an assistant or scripted client. Both give the same permitted or refused outcome, the same state change, and equivalent audit entries that differ only in the recorded surface. Each surface's deployed credentials grant no access to storage or to module internals; an attempt to use them that way is refused.  
**Open:** [SUR-Q01](#user-surfaces-and-assistants), [SUR-Q02](#user-surfaces-and-assistants).

### SUR-002 — Confirmation bound to what was shown
**Category:** Core  
**Status:** Proposed  
An action with clinical or legal effect shall take effect only for the patient, the item revisions, and the content the confirming person was shown. If any of them changed in between, the action is refused and the person is shown what changed.

**Verify:** Prepare an order for patient A, switch the session to patient B in another window, then confirm: the order is placed for A or refused, never for B. Change a result revision between display and review sign-off: sign-off is refused and the new revision shown. Repeat both with the action prepared by an assistant and confirmed by the person; the outcomes are the same.  
**Open:** [DOC-Q01](clinical-requirements.md#clinical-documentation).

### SUR-003 — Patient identity re-verification
**Category:** Core / Deployment-specific  
**Status:** Proposed  
For actions the deployment designates as high-risk, such as ordering or prescribing, the product shall support requiring the person to re-verify the patient's identity by active input, not only by acknowledging a prompt.

**Verify:** With ordering designated, place an order through each surface: confirmation requires the person to enter identifying information that matches the patient, and a mismatch blocks the order. With the designation removed, no re-verification is required. The designation is recorded as safety-relevant configuration under [AUD-006](#aud-006--administrative-and-configuration-audit).  
**Open:** [SUR-Q01](#user-surfaces-and-assistants).

### AGT-001 — Delegated identity
**Category:** Core  
**Status:** Proposed  
An assistant shall act only on behalf of an identified person, within a session that person started, and hold no standing access of its own. Every read and action records the person, the assistant and its version, and the surface.

**Verify:** An assistant request without a delegating person is refused. Reads and actions through an assistant appear in the access and audit logs with the person, assistant, version, and surface, as [AUD-002](#aud-002--access-log-context) requires for anyone acted for. After the person's session ends or their access changes under [IAM-008](#iam-008--authorization-lifecycle), the assistant's queued and retried requests are decided on the new state.  
**Open:** [AGT-Q01](#user-surfaces-and-assistants).

### AGT-002 — Access no wider than the person's
**Category:** Core  
**Status:** Proposed  
An assistant's reads, searches, and summaries shall be authorized as the delegating person's in the current context, and a deployment may narrow them further. Exceptional access, such as emergency access outside a care relationship, requires the person's own explicit action. Every patient record an assistant reads is a logged disclosure, whether or not its content is shown to the person.

**Verify:** Ask an assistant about a patient the person may not access: the request is refused and logged as denied. Ask for a search across patients: results and counts include only patients the person may access, as [IAM-003](#iam-003--need-based-access) requires. The assistant cannot invoke exceptional access. An assistant reading many records in a short period is flagged by monitoring under [AUD-005](#aud-005--risk-based-review).  
**Open:** [IAM-Q04](#identity-authentication-and-authorization).

### AGT-003 — Person confirms consequential actions
**Category:** Core  
**Status:** Proposed  
An assistant may read, summarize, and prepare drafts. Signing, ordering, prescribing, completing a review, sending information to a patient or another provider, and changing access or consent shall take effect only when the delegating person confirms the prepared action under [SUR-002](#sur-002--confirmation-bound-to-what-was-shown). Any exception is decided per action and recorded in the clinical risk analysis.

**Verify:** Have an assistant attempt each listed action: each stays pending until the person confirms, and the confirmation shows the exact content. Unconfirmed drafts never appear as signed, sent, or completed. A confirmation the assistant attempts to give itself, including by operating the person's graphical client, is not accepted.  
**Open:** [AGT-Q02](#user-surfaces-and-assistants), [AGT-Q03](#user-surfaces-and-assistants).

### AGT-004 — Provenance of generated content
**Category:** Core  
**Status:** Proposed  
Content an assistant creates or changes shall be marked as assistant-generated, with the assistant version and the source revisions it used, until a person adopts it; adoption records who adopted it and when. The mark is retained in history and in exchange where the receiving format can carry it.

**Verify:** Have an assistant draft a note from three source entries. Before adoption, every view and export shows it as assistant-generated, identifying the assistant version and the three source revisions. After a person edits and adopts it, history shows both the generated draft and the adopted version, and who adopted it. A summary whose sources changed after generation shows that it is out of date.  
**Open:** [Q-AI-005](decisions.md#ai), [CDS-002](clinical-requirements.md#cds-002--traceability).

### Open questions

- **SUR-Q01:** Which surfaces does the first increment provide: a graphical client, an assistant, or both? For which roles and device classes ([NFR-UX-005](#nfr-ux-005--supported-device-classes))?
- **SUR-Q02:** What form does the action interface take, and how is it described to assistants? Decided with the technology stack.
- **AGT-Q01:** Is the assistant part of the product, an external general-purpose assistant acting through the action interface, or both? This decides regulatory responsibility ([REG-003](assurance.md#reg-003--scope-boundaries)) and where patient information is processed ([SE-AI-Q01](sweden.md#swedish-legal-and-regulatory-profile)).
- **AGT-Q02:** How does the product establish that a confirmation came from the person when an assistant can operate the person's graphical client? Candidates include step-up authentication and confirmation on a separate device.
- **AGT-Q03:** May an assistant complete any action without per-action confirmation, such as filing a normal result as reviewed?

---

## Administration and configuration

### ADM-001 — Controlled configuration
**Category:** Core / Deployment-specific  
**Status:** Proposed  
The system shall support controlled and traceable configuration of templates, terminology bindings, workflow rules, permissions, and other configurable behavior.

**Verify:** For templates, terminology bindings, workflow rules, permissions, and each other class the deployment declares configurable, attempt a change as an unauthorized user, submit a change that fails validation, and make a valid change. The unauthorized and invalid changes are refused and nothing takes effect. Where the deployment requires approval, a change takes effect only after an authorized approver other than its author approves it. A valid change takes effect only as a new, identified configuration version. Reverting restores the prior values as another new version and leaves the reverted change in the history.  
**Open:** [ADM-Q01](#administration-and-configuration), [ADM-Q02](#administration-and-configuration).

### ADM-002 — Configuration history
**Category:** Core  
**Status:** Proposed  
For safety-relevant configuration it shall be possible to determine what configuration was effective at a given historical point where this matters for understanding a clinical event.

**Verify:** Make a sequence of safety-relevant configuration changes, including one scheduled to take effect later and one reversal, and record clinical actions between them. For any chosen past time, the system returns the configuration versions and values then in effect; queries just before and just after a change's effective time return the versions on either side of it. Results match an independent record kept by the test and the versions [MOD-007](#mod-007--reproducible-configuration-context) retained on each action, and they are unchanged after later changes and an upgrade.  
**Open:** [MOD-Q05](#modularity-and-configuration).

### ADM-003 — Organizational separation
**Category:** Deployment-specific  
**Status:** Decision required  
If multiple healthcare providers share an installation, requirements for information, configuration, and access separation shall be explicitly defined.

### ADM-004 — Terminology management
**Category:** Core / Jurisdiction-specific  
**Status:** Proposed  
The system shall support controlled adoption and updating of externally maintained terminology and code systems.

**Verify:** For each code system the deployment declares, import a valid new release, a release that fails the publisher's integrity check or expected format, and a release from a source the deployment has not declared. The failing and undeclared releases are refused and nothing changes. Before an accepted release takes effect, the system reports the bindings, value sets, rules, and templates that use concepts it retires, changes, or replaces. The release takes effect as a new configuration version under [ADM-001](#adm-001--controlled-configuration), retaining its code system, release identifier, and source. Entries recorded earlier keep their original codes, code system versions, and display text; a code the release retires still displays with its original meaning and is marked inactive. New entries use the new release from its effective time. Reverting to the prior release leaves entries recorded under the new one unchanged.  
**Open:** [CLI-Q02](clinical-requirements.md#clinical-facts-and-health-information), [ADM-Q02](#administration-and-configuration).

### ADM-005 — Configuration boundaries
**Category:** Core  
**Status:** Proposed  
Configuration shall not be used to redefine clinically fundamental concepts in ways that make safety, interoperability, or testing dependent on arbitrary local interpretation.

**Verify:** For each concept the product declares fundamental, including patient identity, signed and corrected status, clinical and recording time, units of measure, and the distinctions of [INF-007](clinical-requirements.md#inf-007--unknown-and-absent-information), attempt through each configuration path to change its meaning: remap a status or code, change a unit or its conversion, alter a declared state transition, or record absent values as negative. Validation refuses each attempt, names the concept, and nothing takes effect. Changes within the declared limits, such as layout, display labels, and terminology bindings, are accepted, and a relabeled item still exports with its unchanged underlying concept. A change of meaning is accepted only as a versioned extension under [MOD-005](#mod-005--governed-extension). In each accepted configuration, the shared conformance tests pass unchanged, and content exported from the same clinical input matches the reference configuration apart from declared presentation elements.  
**Open:** [ADM-Q01](#administration-and-configuration), [MOD-Q03](#modularity-and-configuration).

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
