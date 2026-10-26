# Laboratory result loop

[Master specification](../SPECIFICATION.md) · **Status:** Outline for the first end-to-end slice; not reviewed by clinicians · **Date:** 2026-10-26

This document defines one workflow in enough depth to build and test it. It owns the workflow's states, rules, and failure cases; requirement statements stay in their owning documents and are linked by ID. Rules marked *draft* become requirements in [ORD](clinical-requirements.md#orders-investigations-and-results) after clinical review.

## Why this slice

- It crosses most of the shared foundation: patient identity, ordering, external exchange, versioned results, review responsibility, correction, patient access, audit, and downtime.
- Missed or delayed result follow-up is a recognized failure mode ([SAFE-004](assurance.md#safe-004--failure-modes)), and its harm comes from absence of action, which specifications usually miss.
- The [repository probe](prototype-findings.md) and [case 2](record-model-comparison.md#case-2--corrected-result-after-review) already cover part of it.

Choosing it proposes resolving [ORD-009](clinical-requirements.md#ord-009--laboratory-medicine) as in scope for the first increment, limited as below.

## Scope

**Setting:** Swedish primary care (vårdcentral), adult patients with a verified personal identity number.

**In scope:** clinical chemistry requests from a visit; specimen collection at the clinic; analysis by an external laboratory; preliminary, final, and corrected results; review and follow-up by a responsible clinician; critical values; patient access to results; laboratory interface downtime.

**Out of scope for this slice:** microbiology, pathology, and point-of-care testing; order sets ([ORD-Q03](clinical-requirements.md#orders-investigations-and-results)); inpatient and emergency settings; reserve identities and protected personal data, except as listed failure cases; decision support beyond reference-range flags.

## Actors

| Actor | Role in the slice |
|---|---|
| Ordering clinician | Requests the test; by default responsible for review and follow-up. |
| Nurse or assistant nurse | Collects and labels the specimen; may receive critical-value calls; contacts patients. |
| Covering clinician | Takes over review when the responsible clinician is absent. |
| Clinic manager or delegate | Owns reassignment of orphaned review work. |
| External laboratory | Accepts or rejects requests and specimens; issues and corrects results; phones critical values. |
| Patient | Is informed of results and follow-up; may see results through 1177. |

## Journey

1. During a visit, the clinician requests tests for a stated indication.
2. The request is sent to the laboratory and acknowledged.
3. The specimen is collected, labelled, and sent; the laboratory registers receipt.
4. The laboratory returns preliminary and then final results.
5. A review obligation is assigned to the responsible clinician.
6. The clinician reviews the result version and records follow-up: no action, patient informed, new request, referral, or appointment.
7. The patient is informed according to the recorded decision.
8. The obligation closes when its follow-up is recorded.

## States (draft)

Each lifecycle is owned separately and linked, as proposed in the [foundational design](foundational-design.md#requests-work-and-outcomes).

| Lifecycle | States | Notes |
|---|---|---|
| Request | draft → sent → accepted · rejected → in progress → completed; cancelled | Cancellation after collection does not erase the specimen or any result. |
| Specimen | awaiting collection → collected → received → analysed; rejected → recollection requested | Rejection reason comes from the laboratory. |
| Result (per observation) | preliminary → final → corrected (new version); entered in error | Each version is retained; arrival order does not define the current version. |
| Review obligation | open → reviewed → follow-up recorded → closed; reassigned; overdue; superseded by correction | A review binds to one result version. |

## Rules (draft)

- **R1:** Every final or corrected result for a request has exactly one open or closed review obligation per version that requires review, with a named responsible person or team at all times.
- **R2:** Receiving or displaying a result never marks it reviewed.
- **R3:** A review records the exact result version, the reviewer, the time, and the follow-up decision.
- **R4:** A correction after review creates one new obligation linked to the earlier review, and the corrected value is shown as unreviewed.
- **R5:** An obligation not closed within the deployment's declared time is escalated to the covering clinician or clinic manager; it never expires silently.
- **R6:** A clinician leaving or becoming unavailable cannot leave an obligation without an owner.
- **R7:** A critical value reported by phone is recorded with who called, who received it, and when, and starts the critical-result path even if the electronic result has not yet arrived.
- **R8:** A result that cannot be matched to a patient and request is held in a work queue, never attached by best guess.
- **R9:** Requests and results that are pending, failed, or of unknown delivery status are visible to the clinic until reconciled.

## Failure and delay cases

| # | Case | Expected behavior | Owners |
|---|---|---|---|
| F1 | Duplicate result message | No duplicate result or obligation. | [INT-004](platform-requirements.md#int-004--reliable-state-changing-exchange) |
| F2 | Older version arrives after correction | Corrected version stays current; late message is retained as history. | [ORD-006](clinical-requirements.md#ord-006--result-review-and-follow-up), case 2 |
| F3 | Correction after review | R4. | [ORD-006](clinical-requirements.md#ord-006--result-review-and-follow-up) |
| F4 | Crash between storing result and creating obligation | After recovery, exactly one obligation exists. | [ORD-006](clinical-requirements.md#ord-006--result-review-and-follow-up) |
| F5 | Result without a matching request, or for an unknown patient | R8; laboratory notified where the interface supports it. | [PAT-001](clinical-requirements.md#pat-001--unambiguous-patient-identification), [INT-005](platform-requirements.md#int-005--provenance-of-imported-information) |
| F6 | Specimen rejected | Request shows rejection and reason; recollection is assigned and the patient contacted. | [ORD-002](clinical-requirements.md#ord-002--external-fulfillment) |
| F7 | Critical value phoned before electronic result | R7; the later electronic result links to the call. | [ORD-007](clinical-requirements.md#ord-007--critical-results) |
| F8 | Responsible clinician absent or gone | R5, R6. | [ORD-Q02](clinical-requirements.md#orders-investigations-and-results), [WF-004](clinical-requirements.md#wf-004--work-lists) |
| F9 | Request cancelled after collection | Results still arrive, are shown, and need review. | Request lifecycle |
| F10 | Laboratory interface down | R9; downtime procedure used; paper or phoned results reconciled afterwards without duplicates. | [NFR-AVL-004](platform-requirements.md#nfr-avl-004--downtime-procedures) |
| F11 | Patient records merged or split after results arrive | Results and obligations follow the corrected identity; history shows the move. | [PAT-005](clinical-requirements.md#pat-005--identity-correction-and-duplicate-resolution), [PAT-006](clinical-requirements.md#pat-006--reversal-of-incorrect-patient-merge) |
| F12 | Unit or reference range changes between results | Trend shows each value with its own unit and range; no silent conversion. | [ORD-004](clinical-requirements.md#ord-004--units-ranges-and-abnormality), [ORD-005](clinical-requirements.md#ord-005--trends) |
| F13 | Patient sees a result before clinician review | Behavior follows the Swedish rule chosen for this information set. | [PRT-001](clinical-requirements.md#prt-001--patient-access-to-information), [SE-1177-Q03](sweden.md) |
| F14 | Reviewer lacks access to the patient | Review refused and logged; obligation stays open and escalates. | [IAM-004](platform-requirements.md#iam-004--context-sensitive-authorization), [AUD-001](platform-requirements.md#aud-001--patient-information-access-logging) |

## Information to capture

For each step, record actor, time, and source ([INF-002](clinical-requirements.md#inf-002--provenance)), distinguishing collection time from result and recording times ([INF-004](clinical-requirements.md#inf-004--clinical-time-and-recording-time)). Results keep code, unit, reference range, abnormal flag, status, and laboratory identity ([ORD-003](clinical-requirements.md#ord-003--results), [INF-006](clinical-requirements.md#inf-006--terminology-context)). Content details wait for the selected archetypes and Swedish information sets.

## Swedish context to confirm

- Which laboratory interface and message standard the first deployment uses, and whether the laboratory system or this product is authoritative for request status ([ORD-Q04](clinical-requirements.md#orders-investigations-and-results)).
- Which code system identifies analyses, and whether results reach NPÖ ([SE-NPO-Q01](sweden.md)).
- When results appear in 1177 and whether clinicians can delay them ([SE-1177-Q03](sweden.md)).
- What HSLF-FS 2016:40 and local practice require for acknowledging results (*vidimering*), and whether that differs from the follow-up record in R3.

## Questions for clinical review

1. Who is responsible for a result when the ordering clinician is a locum or has left?
2. What deadlines are acceptable for review of normal, abnormal, and critical results?
3. Is "reviewed, no action" a valid follow-up, and must normal results be reviewed individually?
4. Who informs the patient, how, and is that recorded?
5. Which failure cases above occur in practice, and which are missing?

## Verification plan

1. Write **Verify** criteria for each draft rule once reviewed, in its owning requirement.
2. Extend the prototype fixtures from case 2 to F1–F4, F7, and F9, which need no Swedish interface decision.
3. Add F5, F10, and F13 after the interface and 1177 questions are answered.
4. Run each case with a synthetic patient in a walkthrough with at least one primary-care clinician and nurse, and record findings against this document.
