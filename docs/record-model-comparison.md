# Clinical record model comparison

[Foundational design](foundational-design.md) · **Status:** Exploratory assessment · **Date:** 2026-09-19

**Recommendation:** Prototype openEHR clinical content with product-owned workflow behavior and FHIR exchange first; retain a FHIR-native implementation as the comparison. A fully product-owned clinical model remains an alternative if both impose unacceptable constraints. This is a recommendation for investigation, not an adopted architecture.

## Scope and evidence

This is a specification-based walkthrough of three synthetic cases, not an implementation benchmark. No server, clinical template, or mapping has been tested. All candidates remain unverified against the cases.

Reviewed references: FHIR R5 5.0.0; openEHR BASE 1.2.0, RM 1.1.0, and REST 1.0.3. These are comparison baselines, not a selection of Swedish interface versions. Resource support, history retention, attestation APIs, and transaction behavior need confirmation in concrete implementations.

The [verification reference set](verification-references.md) retains selected source documents and maps their use to the cases below.

| Candidate | Authoritative clinical content | Workflow responsibility |
|---|---|---|
| FHIR-native | Profiled resources, retained versions, and frozen documents where appropriate. | Product operations enforce transitions; workflow state can use FHIR resources. |
| openEHR-based | Archetyped and templated compositions in a versioned repository. | Product operations coordinate work and reference clinical versions; persistence location remains open. |
| Product-owned | Typed domain records, revisions, and evidence designed by this project. | Product operations and workflow state, with maintained mappings to exchange standards. |

For every candidate, direct storage APIs need controls preventing callers from bypassing clinical operations. The comparisons below distinguish standard mechanisms from product behavior we would implement.

## Case 1 — Concurrent signing

**Fixture:** Clinician A reviews document D revision 4, including result R revision 1 and its presented interpretation. The reviewed snapshot identifies included versions and the template/rendering definition. Clinician B changes D to revision 5 before A confirms.

**Expected:** Confirmation of D4 as current fails visibly. After reviewing the new snapshot, A can confirm it; later amendments retain that confirmation's original scope. Repeat with only R changing: for this case, R freshness is an explicit precondition, so stale confirmation also fails. A failed attempt creates no successful attestation.

Signing here means accountable clinical confirmation. Cryptographic signatures are a separate design choice. Deliberate attestation of historical content would be a separately identified operation.

| Candidate | Available mechanism | Product work and limitation |
|---|---|---|
| FHIR-native | `If-Match` protects a resource update; a document Bundle contains frozen resource versions. `Composition.attester` concerns the presented form. [HTTP](https://hl7.org/fhir/R5/http.html#concurrency), [documents](https://hl7.org/fhir/R5/documents.html). | Build a consistent reviewed snapshot, define attested content, and atomically check required versions when confirming. Checking Composition alone does not check its separately updated references. |
| openEHR-based | Composition updates require the preceding version; the model associates attestations with exact versions or contained items. [REST](https://specifications.openehr.org/releases/ITS-REST/Release-1.0.3/ehr.html), [attestation model, §6.2.8](https://specifications.openehr.org/releases/RM/Release-1.1.0/common.html). | Verify the server's attestation operation and concurrency guarantees. References outside that composition still need snapshot and freshness rules; versioning alone does not enforce our current-content signing policy. |
| Product-owned | Design a snapshot manifest, immutable revisions, conditional confirmation, and an attestation record. | Implement and verify the whole contract, including rendering, retries, retention, and export of evidence. A revision counter alone is insufficient. |

**Finding:** Preserve the reviewed presentation and the intended attestation scope, as well as data versions. A cryptographic signature cannot compensate for an incorrectly assembled snapshot.

## Case 2 — Corrected result after review

**Fixture:** Laboratory report R1 contains observation O1. A clinician records review V1 against those exact versions. The laboratory sends correction R2/O2, repeats the correction message, then delivers an old R1 message late.

**Expected:** R1/O1 and V1 remain retrievable. R2/O2 becomes current according to source revision/supersession rules, without marking it reviewed. One new reassessment obligation is linked to the correction and a responsible recipient. Duplicate delivery creates no additional obligation; late R1 does not restore the old current state. Repeat with a crash between saving the correction and scheduling reassessment.

| Candidate | Available mechanism | Product work and limitation |
|---|---|---|
| FHIR-native | DiagnosticReport represents corrected/amended status and linked results; references can identify exact historical versions. Same-server transactions can group changes. [Report](https://hl7.org/fhir/R5/diagnosticreport.html), [references](https://hl7.org/fhir/R5/references.html), [transactions](https://hl7.org/fhir/R5/http.html#transaction). | Keep report, observation, and review links consistent; define source ordering and deduplication. A corrected status does not itself create or assign reassessment. External stores and notifications remain outside the transaction. |
| openEHR-based | Versioned compositions preserve predecessor and audit information; contributions group version changes in an EHR. [Change control, §6](https://specifications.openehr.org/releases/RM/Release-1.1.0/common.html). | Define report boundaries and stable identities for results inside compositions. Clinical correction status belongs in content, distinct from version lifecycle. Prove durable coordination with the review workflow. |
| Product-owned | Model ReportRevision, ObservationRevision, Review, and Reassessment with explicit relationships. | Implement source reconciliation, historical queries, transaction boundaries, and standard mappings; protect against partial report/observation updates. |

**Finding:** Review belongs to a specific result version. Arrival order is not clinical authority. The record model and the reassessment mechanism need a demonstrable recovery protocol.

## Case 3 — Hospital-to-home-care handover

**Fixture:** A hospital sends transfer H1 to a home-care team, including a care-plan snapshot, medication context, an outstanding investigation, and named responsibility for each pending item. The receiving team explicitly accepts assigned work, but the acknowledgement is lost. Repeat with rejection, stale H1 after H2, revoked access before retry, and a corrected result after transfer.

**Expected:** Transport receipt and clinical acceptance remain distinct. An authoritative transfer record tracks snapshot, item-level acceptance, current responsibility, and outstanding acknowledgements. Retries preserve the transfer identity and do not duplicate work. The sender retains transfer follow-up until acceptance is reconciled or a defined fallback takes responsibility. Stale acceptance cannot silently apply to H2. Fresh restrictions govern subsequent disclosures; corrected results reach the responsible recipient.

| Candidate | Available mechanism | Product work and limitation |
|---|---|---|
| FHIR-native | Care information can be linked to Tasks representing assignment and progress. Task supports requested, received, and accepted states. [Task](https://hl7.org/fhir/R5/task.html). | Profile the exchange and define acceptance semantics, transfer authority, permissions, retries, and escalation. Task states alone do not provide a cross-provider agreement or distributed transaction. |
| openEHR-based | Compositions can represent instructions, actions, and care information. [EHR model](https://specifications.openehr.org/releases/RM/Release-1.1.0/ehr.html). | Define the transfer protocol and workflow state, plus mappings where the receiver uses another model. Do not assume a clinical repository supplies the operational workflow engine. |
| Product-owned | Define a transfer aggregate containing work-item assignments, snapshots, acknowledgements, and responsibility transitions. | Implement the protocol and mappings, including recovery and authority across independently operated systems. |

openEHR also published a separate Task Planning model; PROC 1.7.0 is marked **retired**. Its existence is not evidence of a supported workflow engine for this design. [Specification status](https://specifications.openehr.org/releases/PROC/Release-1.7.0/task_planning.html).

**Finding:** Exchanging a clinical document and transferring responsibility are separate operations. No candidate establishes safe handover merely by storing the corresponding records.

## Assessment and proposed direction

All three appear capable of representing these cases with additional application behavior. The walkthrough does not establish a runtime winner. The distinction is which contracts we maintain ourselves.

| Candidate | Why pursue it | Main cost or risk to test |
|---|---|---|
| FHIR-native | Common representation for clinical exchange and workflow resources. | Profile governance, exact document/review scope, version retention, and consistent behavior across resource boundaries. |
| openEHR-based | Defined content-modelling and versioning framework suited to evaluating our broad, configurable clinical scope. | Template authoring, result identity within compositions, FHIR mapping, repository operation, and coordination with workflow persistence. |
| Product-owned | Direct control of aggregate boundaries, transactions, and application behavior. | We own clinical model evolution, provenance, history, interoperability mappings, and migration contracts. |

My preference for the first openEHR prototype rests on reusing clinical content definitions independently of application code. That separation is explicit in its architecture. Whether it reduces our actual maintenance work remains unmeasured. [BASE architecture, §4.1.1](https://specifications.openehr.org/releases/BASE/Release-1.2.0/architecture_overview.html).

Use product modules to own clinical operations and responsibility, and adapters for each required exchange version. Keep one authoritative representation of each clinical item; FHIR exports and workflow references would not become competing editable copies of openEHR content. This preference selects neither a repository product nor a language.

**Material risk:** A repository commit and a separate workflow-database commit are not automatically atomic. The proposed single application may still operate multiple storage services. Either place inseparable state changes within a supported transaction boundary or use durable operation tracking and reconciliation with explicit intermediate states. An ordinary database write followed by an HTTP call is insufficient evidence of reliable coordination.

## Prototype decision checks

Use the same fixtures and expected outcomes above for both standards-based candidates. Select and pin concrete server versions and supported APIs before running them.

1. Exercise both signing races and retrieve the exact previously confirmed presentation after a template change.
2. Inject duplicate, late, and corrected results; restart at every persistence boundary and account for all review obligations.
3. Exercise accepted, rejected, stale, and lost-acknowledgement transfers; verify responsibility and current access rules.
4. Export/import the supported clinical content through a declared FHIR profile, preserving identity, time, units, source, revision relationships, and explicit mapping losses. Do not claim that exchange transfers attestation validity automatically.
5. Record required custom code, content definitions, migration effort, deployment dependencies, and unresolved correctness gaps. Prefer the model that meets the cases with maintainable definitions and demonstrable recovery.

A failed invariant needs repair or rejection of that implementation. If openEHR introduces excessive mapping or coordination burden, prefer FHIR-native content. Revisit a product-owned clinical model only with concrete gaps that justify its additional ownership. Existing product questions remain open until the comparison has implementation evidence.
