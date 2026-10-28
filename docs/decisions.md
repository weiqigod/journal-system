# Decision index

[Master specification](../SPECIFICATION.md) · Draft supporting specification.

Cross-domain decisions are listed below. References point to the domain question that owns the wording and resolution; existing IDs are retained for traceability. Product breadth is adopted in the [master](../SPECIFICATION.md#product-direction); remaining scope questions concern detail, implementation order, or module and integration boundaries.

The [foundational design exploration](foundational-design.md) proposes answers for shared ownership, record history, workflow coordination, and configuration. The [record model comparison](record-model-comparison.md) recommends an openEHR-based prototype compared with FHIR-native content. This is a specification-based assessment; architecture and question resolutions remain provisional pending implementation evidence.

## Product and care settings

- **Q-PROD-001:** Which care settings and roles do the first increments' scenarios cover, and which remain unexercised?
- **Q-PROD-002:** Resolved direction: a comprehensive clinical information system, built incrementally. Which workflows form the first usable increment remains open.
- **Q-PROD-003:** See [ACT-Q01](terminology.md#open-question-act-q01).
- **Q-PROD-004:** Which inpatient workflows and dependencies should be developed together?
- **Q-PROD-005:** Which emergency and prehospital workflows require dedicated behavior?
- **Q-PROD-006:** Which primary-care workflows exercise the shared foundation and continuity across settings?
- **Q-PROD-007:** Which mental-health workflows require dedicated functionality or controls?
- **Q-PROD-008:** See [ENC-Q02](clinical-requirements.md#organization-care-context-and-encounters).
- **Q-PROD-009:** Which operating-theatre planning responsibilities belong in product modules versus specialist integrations?
- **Q-PROD-010:** Which billing, reimbursement, and revenue-cycle responsibilities belong in product modules versus integrations and jurisdiction profiles?

## Product generality

- **Q-GEN-001:** Which clinical meanings and guarantees must remain consistent across supported configurations, and which capabilities form the minimum shared foundation?
- **Q-GEN-002:** Which variation should be handled as jurisdiction profiles?
- **Q-GEN-003:** Which variation should be handled as care-setting-specific capability?
- **Q-GEN-004:** Which variation should be deployment configuration?
- **Q-GEN-005:** See [JUR-Q01](platform-requirements.md#jurisdiction-profiles).
- **Q-GEN-006:** What evidence is sufficient to conclude that a concept is general rather than Sweden-specific?
- **Q-GEN-007:** See [MOD-Q01](platform-requirements.md#modularity-and-configuration), [MOD-Q02](platform-requirements.md#modularity-and-configuration), [MOD-Q05](platform-requirements.md#modularity-and-configuration).
- **Q-GEN-008:** See [LOC-Q01](platform-requirements.md#internationalization-and-localization), [LOC-Q02](platform-requirements.md#internationalization-and-localization).

## Clinical information

- **Q-INF-001:** See [CLI-Q01](clinical-requirements.md#clinical-facts-and-health-information).
- **Q-INF-002:** See [CLI-Q02](clinical-requirements.md#clinical-facts-and-health-information).
- **Q-INF-003:** How are conflicting sources reconciled? Ownership and authority: see [CLI-Q03](clinical-requirements.md#clinical-facts-and-health-information), [INF-Q03](clinical-requirements.md#information-requirements).
- **Q-INF-004:** Which information states and provenance distinctions must users be able to see?
- **Q-INF-005:** Which clinical information must remain available in its original representation?

## Interoperability

- **Q-INT-001:** See [INT-Q01](platform-requirements.md#interoperability).
- **Q-INT-002:** Which national Swedish services are mandatory for the first deployment?
- **Q-INT-003:** Which international standards must be supported initially?
- **Q-INT-004:** See [INT-Q03](platform-requirements.md#interoperability).
- **Q-INT-005:** Which conformance and certification programs must be passed before production use?

## Security and privacy

- **Q-SEC-001:** See [IAM-Q01](platform-requirements.md#identity-authentication-and-authorization).
- **Q-SEC-002:** Which factors determine authorization to patient information?
- **Q-SEC-003:** Which consent and restriction rules are enforced locally versus externally? Sources: see [CON-Q02](clinical-requirements.md#consent-restrictions-and-patient-choices).
- **Q-SEC-004:** Which access and audit information must be retained? Retention periods: see [AUD-Q02](platform-requirements.md#audit-access-logging-and-monitoring).
- **Q-SEC-005:** Under what controlled circumstances may support personnel access patient information?
- **Q-SEC-006:** How is access to one's own or a related person's record handled when healthcare personnel are also patients?

## Regulation and patient safety

- **Q-REG-001:** What is the formal intended purpose of the first product release?
- **Q-REG-002:** Which parts of the product may be regulated medical software?
- **Q-REG-003:** Which quality-system and lifecycle requirements apply?
- **Q-REG-004:** How are locally configured clinical rules governed and validated?
- **Q-REG-005:** How are regulatory requirements separated between the general product and a jurisdiction-specific deployment?

## Operation

- **Q-OPS-001:** Which delivery models must be supported?
- **Q-OPS-002:** See [AVL-Q01](platform-requirements.md#availability-and-continuity).
- **Q-OPS-003:** What recovery objectives are required?
- **Q-OPS-004:** Is offline operation required?
- **Q-OPS-005:** See [SCL-Q01](platform-requirements.md#scalability).
- **Q-OPS-006:** How are clinically significant upgrades introduced safely?

## AI

- **Q-AI-001:** Is AI-assisted documentation in scope?
- **Q-AI-002:** May the system generate summaries of clinical information?
- **Q-AI-003:** May AI generate suggestions concerning diagnosis, medication, investigations, or treatment?
- **Q-AI-004:** Which AI capabilities are clinical decision support and which are administrative assistance?
- **Q-AI-005:** What verification, provenance, versioning, and human-review requirements apply to AI-generated clinical content? Proposed in [AGT-001](platform-requirements.md#agt-001--delegated-identity)–[AGT-004](platform-requirements.md#agt-004--provenance-of-generated-content).
- **Q-AI-006:** See [AGT-Q01](platform-requirements.md#user-surfaces-and-assistants).

## Development

These decisions come before any product code; see the [master](../SPECIFICATION.md#recommended-next-specification-work). The [interaction surfaces](../SPECIFICATION.md#interaction-surfaces) direction constrains them.

- **Q-DEV-001:** What development philosophy does the project follow? Resolved: clean architecture, object orientation, domain-driven design, test-driven development, and delivery in vertical slices ([development approach](../SPECIFICATION.md#development-approach)). How increments are chosen and released remains open.
- **Q-DEV-002:** What is the roadmap: the order of workflows and the first usable increment ([Q-PROD-002](#product-and-care-settings))?
- **Q-DEV-003:** How is the backlog kept, and how does it trace to requirements and scenarios?
- **Q-DEV-004:** Which language, database, framework, and record model does the product use? Resolved: C# for all backend code, with ASP.NET Core and Dapper; Svelte with TypeScript and SvelteKit for the frontend; PostgreSQL as the database; NUnit for backend tests and Vitest for frontend tests; openEHR as the record model, with the project implementing its own repository instead of running EHRbase, validated by a required [harness](openehr-validation.md). Other libraries (for example sign-in, background work, database migrations, and end-to-end testing), the record model, and the technology of the assistant surface remain open ([SUR-Q02](platform-requirements.md#user-surfaces-and-assistants), [SCL-Q01](platform-requirements.md#scalability)).
- **Q-DEV-005:** Which parts of openEHR does the implementation cover? Resolved in part: it targets the current releases ([target releases](openehr-validation.md#target-releases)) and uses ADL 2. Open: the AQL scope, JSON and XML formats, and the conformance profile claimed.
- **Q-DEV-006:** Does the implementation expose the openEHR REST API? External test catalogues such as Veredictum need it ([harness tooling](openehr-validation.md#tooling)).
- **Q-DEV-007:** Is the proposed [validation harness](openehr-validation.md) design adopted, and which external tools does it use: Veredictum, Archie?
