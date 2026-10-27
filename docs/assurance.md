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

**Verify:** For each capability and supported jurisdiction, a dated, versioned assessment records the intended purpose under [REG-001](#reg-001--intended-purpose); each instrument considered, including in the EU [Regulation (EU) 2017/745](http://data.europa.eu/eli/reg/2017/745/oj) (MDR), [Regulation (EU) 2017/746](http://data.europa.eu/eli/reg/2017/746/oj) (IVDR), [Regulation (EU) 2025/327](http://data.europa.eu/eli/reg/2025/327/oj) (EHDS), and for AI capabilities [Regulation (EU) 2024/1689](http://data.europa.eu/eli/reg/2024/1689/oj) (AI Act); the conclusion and class for each, with reasoning; and who reviewed it. A change to a capability's intended purpose or to an applicable instrument reopens the assessment before the next release.  
**Open:** [REG-Q02](#regulatory-and-legal-requirements-management), [REG-Q04](#regulatory-and-legal-requirements-management).

### REG-003 — Scope boundaries
**Status:** Proposed  
Where different capabilities have materially different regulatory obligations, their product and governance boundaries shall be made explicit.

### REG-004 — Compliance traceability
**Status:** Proposed  
Externally imposed requirements shall be traceable to the product requirements, evidence, controls, and release scope that satisfy them.

### REG-005 — European Health Data Space conformity
**Status:** Externally driven  
Where the product is placed on the market or put into service in the EU as an EHR system for priority categories of personal electronic health data, it shall include the European interoperability and logging software components and meet the EHDS essential requirements and common specifications for those categories from their application dates.

**Verify:** For each priority category the product processes, the technical documentation maps every Annex II essential requirement to product requirements and evidence. The interoperability component exchanges that category in the European electronic health record exchange format, and the logging component records health professionals' access in the specified format, each passing the applicable European digital testing environment. The conformity steps that Chapter III assigns to the responsible party are complete before the product is released for that category.  
**Open:** [REG-Q01](#regulatory-and-legal-requirements-management), [REG-Q05](#regulatory-and-legal-requirements-management), [REG-Q06](#regulatory-and-legal-requirements-management).

### EU instruments (informative)

[Regulation (EU) 2025/327](http://data.europa.eu/eli/reg/2025/327/oj) on the European Health Data Space applies generally from 26 March 2027. Its EHR-system obligations in Chapter III apply in stages under Article 105:

| Scope | From |
|---|---|
| Patient summaries, electronic prescriptions, electronic dispensations (Article 14(1)(a)–(c)) | 26 March 2029 |
| Imaging studies and reports, medical test results including laboratory results, discharge reports (Article 14(1)(d)–(f)) | 26 March 2031 |
| EHR systems developed in-house by healthcare providers or offered as a service (Article 26(2)) | 26 March 2031 |

- The two harmonised components are defined in Article 2 and required by Article 25. General-purpose software used in healthcare is excluded.
- The [laboratory result loop](workflow-laboratory-results.md) processes medical test results, so the 2031 date applies to it.
- The logging component sets an exchange format for access information. [AUD-001](platform-requirements.md#aud-001--patient-information-access-logging) still owns what access logging must record; the EHDS format is an external constraint to map to it.
- Under the MDR, software with a medical purpose for individual patients may qualify as a medical device. Record storage and display usually does not, but capabilities such as decision support or dose calculation may. Qualify each capability separately, using the Medical Device Coordination Group's [software guidance](https://health.ec.europa.eu/medical-devices-sector/new-regulations/guidance-mdcg-endorsed-documents-and-other-guidance_en) (MDCG 2019-11), and keep the boundaries explicit under [REG-003](#reg-003--scope-boundaries).
- Under the [AI Act](http://data.europa.eu/eli/reg/2024/1689/oj), an AI system that is itself a medical device or IVD, or a safety component of one, and that requires notified-body conformity assessment is high-risk under Article 6(1). Its obligations, including human oversight (Article 14), apply from 2 August 2028, as amended by [Regulation (EU) 2026/1744](http://data.europa.eu/eli/reg/2026/1744/oj); MDR and IVDR dates are unchanged. An assistant that drafts or summarizes may fall outside this, while one that suggests diagnoses, medication, or investigations may not. Qualify each assistant capability separately under [REG-003](#reg-003--scope-boundaries) and [AGT-003](platform-requirements.md#agt-003--person-confirms-consequential-actions).
- Medical devices and IVDs that claim interoperability with the harmonised components must also meet the EHDS requirements for them (Article 27).

### Open questions

- **REG-Q01:** Who holds the applicable manufacturer and operational responsibilities for the first deployment used in actual care?
- **REG-Q02:** Which capabilities may independently trigger medical-device regulation?
- **REG-Q03:** Which quality-management obligations apply to the first release?
- **REG-Q04:** Which regulatory assessments must be repeated for each jurisdiction?
- **REG-Q05:** Under the EHDS, is the open-source project a manufacturer placing an EHR system on the market, or does each healthcare provider that deploys it put an in-house system into service under Article 26(2) and hold the conformity obligations?
- **REG-Q06:** Which priority categories does the first increment process, and so which EHDS application dates and common specifications apply?
- **REG-Q07:** Does the [Cyber Resilience Act](http://data.europa.eu/eli/reg/2024/2847/oj) apply to the product or its distribution, given its provisions for open-source software and its relationship to EHDS and the MDR?

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
- an assistant action or generated content the person did not intend or check.

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

### Scenario-based verification

Development is verified against scenarios grounded in published sources: regulations, regional routines, laboratory and service instructions, incident reports, and studies. Each scenario cites its sources and states any assumption where they disagree or are silent. Scenarios use synthetic patients, a separate test environment, and simulated external services, and cover ordinary work, interruptions, handovers, and recovery from mistakes. Results record the scenario, expected and observed behavior, and impact, linked to a requirement or coverage gap. The [laboratory result scenarios](scenarios-laboratory-results.md) are the first set.

Repeat scenarios after changes and turn reproducible defects into regression checks. Record which roles and settings the scenarios cover and which remain unexercised. Readiness for actual care also needs [TST-008](#tst-008--clinical-workflow-validation) and the safety, privacy, integration, and operational evidence defined in this specification.

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
