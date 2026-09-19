# Regulation, safety, verification, and migration

[Master specification](../SPECIFICATION.md) · Draft supporting specification.

## Regulatory and legal requirements management

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

- **REG-Q01:** Who holds the applicable manufacturer and operational responsibilities for the first deployment used in actual care?
- **REG-Q02:** Which capabilities may independently trigger medical-device regulation?
- **REG-Q03:** Which quality-management obligations apply to the first release?
- **REG-Q04:** Which regulatory assessments must be repeated for each jurisdiction?

---

## Clinical risk management and patient safety

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

## Testing and verification

The [verification references](verification-references.md) connect selected external contracts to the foundational prototype cases and record which supporting test material still needs selection.

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
**Category:** Core / Care-setting-specific  
**Status:** Proposed  
Representative care workers shall exercise critical end-to-end workflows in realistic scenarios, with findings addressed and the workflows rechecked before use in actual care.

**Verify:** For each critical workflow, evidence identifies the build and configuration, participant role, scenario, expected and observed outcome, and resolution and recheck of safety or correctness defects. Unresolved such defects block the affected workflow's use in actual care.  
**Open:** [ACT-Q01](terminology.md#open-question-act-q01), [Q-PROD-001](decisions.md#product-and-care-settings).

### TST-009 — Configuration verification
**Status:** Proposed  
Safety-relevant deployment configuration shall be verified before activation and after material change.

### Practitioner testing and dogfooding

The development feedback loop starts with people working in care who are available to test. Early sessions use synthetic patients, a separate test environment, and simulated external services. Participants try ordinary work, interruptions, handovers, and recovery from mistakes; findings record the scenario, expected behavior, observed behavior, and impact, linked to a requirement or coverage gap.

Repeat scenarios after changes and turn reproducible defects into regression checks. Record which roles and settings were exercised and which remain unreviewed. These sessions guide development without a customer sign-off process. Readiness for actual care also needs the safety, privacy, integration, and operational evidence defined in this specification.

---

## Migration

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
