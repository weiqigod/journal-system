# Terminology and actors

[Master specification](../SPECIFICATION.md) · Draft supporting specification.

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
| Shared clinical foundation | The common capabilities and guarantees required by a supported product configuration; its minimum scope remains to be established. |
| Capability module | A selectable product capability with defined responsibilities and dependencies, without an assumed technical packaging or deployment model. |
| Care-setting profile | The capabilities, workflow expectations, and constraints associated with a supported care environment. |
| Localization | Adaptation of language and presentation to a supported user or deployment context while preserving clinical meaning. |
| Supported configuration | A specified combination of product and module versions, profiles, integrations, and deployment settings with evidence for its intended use. |

---

## Actors

The following actors guide broad workflow coverage. Their detailed needs and the order in which their workflows become usable remain open.

- physicians,
- nurses,
- nursing assistants,
- paramedics and other prehospital staff,
- midwives,
- dentists and dental staff,
- radiographers and laboratory professionals,
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
- family members and informal carers,
- legally authorized representatives,
- external healthcare providers,
- external systems and technical clients.

### Open question ACT-Q01

Which workflows, permissions, and organizational variations does each role need, and which can be exercised in the next implementation increment?
