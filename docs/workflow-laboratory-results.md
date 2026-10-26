# Laboratory result loop

[Master specification](../SPECIFICATION.md) · **Status:** Outline for the first end-to-end slice; grounded in published Swedish routines and studies, not in practitioner review · **Date:** 2026-10-26

This document defines one workflow in enough depth to build and test it. It owns the workflow's states, rules, and failure cases; requirement statements stay in their owning documents and are linked by ID. Rules marked *draft* become requirements in [ORD](clinical-requirements.md#orders-investigations-and-results) once the slice is built and verified. [Scenarios](scenarios-laboratory-results.md) exercise the rules end to end.

## Why this slice

- It crosses most of the shared foundation: patient identity, ordering, external exchange, versioned results, review responsibility, correction, patient access, audit, and downtime.
- Missed result follow-up is common and harmful. Across 19 ambulatory studies, 6.8–62% of abnormal laboratory results were not followed up ([E1](#evidence)). Its harm comes from absent action, which specifications usually miss ([SAFE-004](assurance.md#safe-004--failure-modes)).
- The [repository probe](prototype-findings.md) and [case 2](record-model-comparison.md#case-2--corrected-result-after-review) already cover part of it.

Choosing it proposes resolving [ORD-009](clinical-requirements.md#ord-009--laboratory-medicine) as in scope for the first increment, limited as below.

## Scope

**Setting:** Swedish primary care (vårdcentral), adult patients with a verified personal identity number.

**In scope:** clinical chemistry requests from a visit; specimen collection at the clinic; analysis by the regional laboratory or a send-out laboratory; preliminary, final, and corrected results; review (*vidimering*) and follow-up; critical values; patient access to results; laboratory interface downtime.

**Out of scope for this slice:** microbiology, pathology, and point-of-care testing; order sets ([ORD-Q03](clinical-requirements.md#orders-investigations-and-results)); inpatient and emergency settings; reserve identities and protected personal data, except as listed failure cases; decision support beyond the laboratory's reference and critical flags.

## Actors

| Actor | Role in the slice |
|---|---|
| Ordering clinician | Requests the test; by default responsible for review and follow-up. |
| Nurse or assistant nurse | Collects and labels the specimen; receives critical-value calls; contacts patients. |
| Covering clinician | Monitors an absent colleague's results; handles what cannot wait. |
| Medical secretary or care administrator | Checks that every incoming result has a responsible reviewer; reminds and escalates when results wait too long. |
| Unit manager and medically responsible physician | Own monitoring arrangements and reassignment of orphaned work. |
| Laboratory | Accepts or rejects requests and specimens; issues and corrects results; phones critical values. |
| Out-of-hours physician service | Receives critical values when the clinic is closed. |
| Patient | Is informed of results; may see them in 1177 before review. |

## Journey

1. During a visit, the clinician requests tests for a stated indication.
2. The request is sent to the laboratory, electronically or, for some send-out tests, on paper.
3. The specimen is collected, labelled, and transported; the laboratory registers receipt.
4. The laboratory returns preliminary and then final results; critical values are also phoned.
5. A review obligation is assigned to the responsible clinician.
6. The clinician reviews the result version and records follow-up: no action, with reasoning if the result is abnormal; patient informed; new request; referral; or appointment.
7. The patient is informed as recorded.
8. The obligation closes when its follow-up is recorded.

## States (draft)

Each lifecycle is owned separately and linked, as proposed in the [foundational design](foundational-design.md#requests-work-and-outcomes).

| Lifecycle | States | Notes |
|---|---|---|
| Request | draft → sent → accepted · rejected → in progress → completed; cancelled; overdue | Cancellation after collection does not erase the specimen or any result. |
| Specimen | awaiting collection → collected → received → analysed; rejected or lost → recollection requested | Rejection reason comes from the laboratory. |
| Result (per observation) | preliminary → final → corrected (new version); entered in error | Each version is retained; arrival order does not define the current version. |
| Review obligation | open → reviewed → follow-up recorded → closed; reassigned; overdue | A review binds to one result version. A correction before review moves the open obligation to the newer version; after review it opens a new obligation (R4). |

## Rules (draft)

- **R1:** Every final or corrected result for a request has exactly one open or closed review obligation per version that requires review, with a named responsible person or team at all times.
- **R2:** Receiving, displaying, or publishing a result to the patient never marks it reviewed.
- **R3:** A review records the exact result version, the reviewer, the time, and the follow-up decision. A decision to take no action on an abnormal result includes its reasoning.
- **R4:** A correction after review creates one new obligation linked to the earlier review, and the corrected value is shown as unreviewed. A correction before review moves the open obligation to the corrected version and records the move in its history, so the reviewer always signs off the current version.
- **R5:** An obligation not closed within the deployment's declared time is escalated, first as a reminder to its owner, then to the unit's designated monitor or manager; it never expires silently. The Swedish routines examined use seven days.
- **R6:** A clinician leaving or becoming unavailable cannot leave an obligation without an owner. Planned absence requires handing over open obligations; unplanned absence lets a designated person reassign them.
- **R7:** A critical value reported by phone is recorded with who called, who received it, and when, and starts the critical-result path even if the electronic result has not yet arrived. A critical flag in the electronic result starts the same path when no call was recorded. Actions are recorded against the phoned value at once, but sign-off waits for the electronic result, because a review binds to a stored result version (R3); if none arrives, R10 flags the request.
- **R8:** A result that cannot be matched to a patient and request, or has no identifiable orderer, goes to a monitored unit queue, never to nobody and never attached by best guess.
- **R9:** Requests and results that are pending, failed, or of unknown delivery status are visible to the clinic until reconciled.
- **R10:** A sent request without a final result after its expected turnaround is flagged to the orderer and, if still unresolved, to the unit's designated monitor.
- **R11:** The follow-up decision records how and when the patient is informed, or that the patient agreed not to be informed of this result.
- **R12:** A critical value handled out of hours by another service appears to the responsible clinician on the next working day with the actions taken, and still requires their review.
- **R13:** A result the laboratory withholds, such as a haemolysed sample, creates no review obligation. It creates a recollection task owned by the unit's designated monitor and notifies the orderer. The request stays open, so R10 applies until a usable result arrives.
- **R14:** A result may be reviewed by an active physician at the ordering unit, or by staff whose role the deployment authorises to review their own orders, such as nurses for tests they ordered. Responsibility follows the ordering unit, not the unit where the patient is listed. Other attempts are refused and logged. This is the slice's stand-in for [IAM-004](platform-requirements.md#iam-004--context-sensitive-authorization).

## Failure and delay cases

| # | Case | Expected behavior | Owners |
|---|---|---|---|
| F1 | Duplicate result message | No duplicate result or obligation. | [INT-004](platform-requirements.md#int-004--reliable-state-changing-exchange) |
| F2 | Older version arrives after correction | Corrected version stays current; late message is retained as history. | [ORD-006](clinical-requirements.md#ord-006--result-review-and-follow-up), case 2 |
| F3 | Correction after review | R4. | [ORD-006](clinical-requirements.md#ord-006--result-review-and-follow-up) |
| F4 | Crash between storing result and creating obligation | After recovery, exactly one obligation exists. | [ORD-006](clinical-requirements.md#ord-006--result-review-and-follow-up) |
| F5 | Result without a matching request, or for an unknown patient | R8; laboratory notified where the interface supports it. | [PAT-001](clinical-requirements.md#pat-001--unambiguous-patient-identification), [INT-005](platform-requirements.md#int-005--provenance-of-imported-information) |
| F6 | Specimen rejected, haemolysed, or lost in transport | Request shows the reason; recollection is assigned and the patient contacted. | [ORD-002](clinical-requirements.md#ord-002--external-fulfillment) |
| F7 | Critical value phoned before electronic result | R7; the later electronic result links to the call. | [ORD-007](clinical-requirements.md#ord-007--critical-results) |
| F8 | Responsible clinician absent or gone | R5, R6. | [ORD-Q02](clinical-requirements.md#orders-investigations-and-results), [WF-004](clinical-requirements.md#wf-004--work-lists) |
| F9 | Request cancelled after collection | Results still arrive, are shown, and need review. | Request lifecycle |
| F10 | Laboratory interface down | R9; urgent results by phone; paper results reconciled afterwards without duplicates. | [NFR-AVL-004](platform-requirements.md#nfr-avl-004--downtime-procedures) |
| F11 | Patient records merged or split after results arrive | Results and obligations follow the corrected identity; history shows the move. | [PAT-005](clinical-requirements.md#pat-005--identity-correction-and-duplicate-resolution), [PAT-006](clinical-requirements.md#pat-006--reversal-of-incorrect-patient-merge) |
| F12 | Unit or reference range changes between results | Trend shows each value with its own unit and range; no silent conversion. | [ORD-004](clinical-requirements.md#ord-004--units-ranges-and-abnormality), [ORD-005](clinical-requirements.md#ord-005--trends) |
| F13 | Patient sees a result before clinician review | Staff can see that the result is visible to the patient and unreviewed. | [PRT-001](clinical-requirements.md#prt-001--patient-access-to-information), [SE-1177-Q03](sweden.md) |
| F14 | Reviewer lacks review authority for the result | R14: review refused and logged; obligation stays open and escalates. | [IAM-004](platform-requirements.md#iam-004--context-sensitive-authorization), [AUD-001](platform-requirements.md#aud-001--patient-information-access-logging) |
| F15 | Expected result never arrives | R10. | [ORD-002](clinical-requirements.md#ord-002--external-fulfillment) |
| F16 | Critical value reported out of hours to another service | R12. | [ORD-007](clinical-requirements.md#ord-007--critical-results) |
| F17 | Laboratory does not phone a repeated critical value | R7, by the electronic flag. | [ORD-007](clinical-requirements.md#ord-007--critical-results) |
| F18 | Abnormal result reviewed with no action and no reasoning | Review refused until reasoning is recorded (R3). | [ORD-006](clinical-requirements.md#ord-006--result-review-and-follow-up) |

## Information to capture

For each step, record actor, time, and source ([INF-002](clinical-requirements.md#inf-002--provenance)), distinguishing collection time from result and recording times ([INF-004](clinical-requirements.md#inf-004--clinical-time-and-recording-time)). Results keep code, unit, reference range, abnormal and critical flags, status, laboratory comments, and laboratory identity ([ORD-003](clinical-requirements.md#ord-003--results), [INF-006](clinical-requirements.md#inf-006--terminology-context)). Content details wait for the selected archetypes and Swedish information sets.

## Swedish practice

From the published sources listed under [Evidence](#evidence). Regions and laboratories differ; these are examples, not national rules.

- **Vidimering is set by regional routine, not by regulation.** The consolidated HSLF-FS 2016:40 does not use the term; it requires routines for signing journal entries (6 kap. 4 §) and lists incoming information among journal contents (5 kap. 5 §) ([E2](#evidence)).
- **Every incoming result is vidimerat**, normal or not, through the record system's unreviewed-results list ([E3](#evidence), [E4](#evidence)).
- **Deadlines and monitoring.** Region Värmland: vidimering within 7 days; clinicians check the list daily, at worst every two to three days; administrators look for results unreviewed after 7 days, remind the clinician, then inform the unit manager ([E3](#evidence)).
- **Patients are told.** Region Värmland: results are communicated to the patient unless otherwise agreed and documented; a decision not to act on an abnormal result should be documented ([E3](#evidence)).
- **Absence and departure.** Region Värmland: clear unreviewed results before planned leave; warn a covering colleague about expected abnormal results; local monitoring for absence over three days. Region Gotland: the work list passes to a colleague or locum, and is inherited by each following locum until empty; staff check daily that every incoming result has a named reviewer; the medically responsible physician and unit manager hold overall responsibility ([E3](#evidence), [E4](#evidence)).
- **Critical values.** The laboratory verifies the value, compares it with earlier results, and phones the ordering unit. If the unit cannot be reached, it calls an on-call service; in Stockholm, out-of-hours primary-care values go to the physician car service. Limits differ: potassium ≥6.0 mmol/L in Kungälv, >6.0 at Karolinska. Kungälv documents who gave the result, to whom, and when, in the laboratory system. Karolinska may not phone a value similar to one recently reported, and holds the orderer ultimately responsible for monitoring results ([E5](#evidence), [E6](#evidence), [E7](#evidence)).
- **Send-out tests** may be ordered on paper and answered by post or scan. In Region Jämtland Härjedalen, a result without a named orderer is attached to a placeholder orderer whose list must be monitored continuously ([E8](#evidence)).
- **Patient access.** In Stockholm, patients see clinical chemistry results in 1177 at the same time as staff, marked as unverified; some result types are not shown. Other regions differ ([E9](#evidence)).
- **System change is a real risk.** After a record-system change in Västernorrland, a parent reported children's results not visible in the record 4.5 months after they arrived ([E10](#evidence)).
- **Review is not follow-up.** IVO criticised a primary-care physician for not following PSA action limits in twelve cases, risking delayed investigation ([E11](#evidence)). A system can require a recorded decision; it cannot make the decision right.

## Open questions

- Which laboratory interface and message standard the first deployment uses, and whether the laboratory system or this product is authoritative for request status ([ORD-Q04](clinical-requirements.md#orders-investigations-and-results)).
- Which code system identifies analyses, and whether results reach NPÖ ([SE-NPO-Q01](sweden.md)).
- Which region's 1177 publication rules the first deployment follows ([SE-1177-Q03](sweden.md)).
- How the first laboratory reports haemolysed samples: withheld, or reported with a comment. Practice is set locally ([E12](#evidence)).

## Verification plan

1. Write **Verify** criteria for each draft rule in its owning requirement as the slice is built.
2. The [lab-loop prototype](../prototypes/lab-loop/README.md) runs S1–S10 and the remaining failure cases as automated tests, with simulated laboratory messages. Result content can be stored in the patched EHRbase as openEHR compositions; workflow state stays in memory. Building it settled R4's correction-before-review behavior and added R13 and R14.
3. Add F5, F10, and F13 after the interface and 1177 questions are answered.
4. Run the [scenarios](scenarios-laboratory-results.md) end to end as acceptance tests, recording expected and observed outcome per step.

## Evidence

- **E1:** Callen JL, Westbrook JI, Georgiou A, et al. [Failure to follow-up test results for ambulatory patients: a systematic review](https://pmc.ncbi.nlm.nih.gov/articles/PMC3445672/). J Gen Intern Med. 2012;27(10):1334–48.
- **E2:** Socialstyrelsen. [HSLF-FS 2016:40, consolidated](https://socialstyrelsen.se/kunskapsstod-och-regler/regler-och-riktlinjer/foreskrifter-och-allmanna-rad/konsoliderade-foreskrifter/201640-om-journalforing-och-behandling-av-personuppgifter-i-halso--och-sjukvarden/). Checked 2026-10-26.
- **E3:** Region Värmland. [Dokumentation, signering, vidimering och bevakning](https://vidadokument.regionvarmland.se/23725), RUT-23725 v4, valid 2025-10-28 to 2027-10-28.
- **E4:** Region Gotland. [Signering, vidimering, bevakning – TakeCare Primärvård](https://dokument.gotland.se/IntegrationService.svc/doc/content/2255), STY-02255 v11.0.
- **E5:** Regional laboratoriemedicin, Västra Götaland. [Medicinska larmgränser Klinisk Kemi Kungälv](https://labbutbud.vgregion.se/api/file/DOK-5320), DOK-5320-18, valid from 2026-03-11.
- **E6:** Karolinska Universitetslaboratoriet. [Larmgränser för hantering av kraftigt avvikande analysresultat](https://www.karolinska.se/4a13b7/globalassets/global/2-funktioner/funktion-kul/klinisk-kemi/kraftigt-avvikande-analysresultat/larmgranser-for-hantering-av-kraftigt-avvikande-analysresultat-inom-klinisk-kemi-kemi2463_7.pdf), KEMI2463-7, valid from 2025-11-24.
- **E7:** Karolinska. [Kraftigt avvikande resultat](https://www.karolinska.se/vard/funktion/funktion-medicinsk-diagnostik-karolinska/vardgivare/universitetslaboratoriet/vara-verksamheter-kul/klinisk-kemi/kraftigt-avvikande-resultat/).
- **E8:** Region Jämtland Härjedalen. [Beställning av skickeprover och central inmatning av provsvar](https://vardgivarwebb.regionjh.se/rest-api/centuri/document/5d405ada-ba79-550d-9e0c-9a32e8bd2a1d/45411), 45411-5, valid from 2026-02-23.
- **E9:** 1177 Stockholm. [Läs din journal via nätet](https://www.1177.se/stockholm/om-1177/nar-du-loggar-in-pa-1177.se/det-har-kan-du-gora-nar-du-loggat-in/las-din-journal/las-din-journal-via-natet/). Checked 2026-10-26.
- **E10:** SVT Nyheter Västernorrland. [Läkare: allvarliga vårdskador kopplas till problem med Cosmic](https://www.svt.se/nyheter/lokalt/vasternorrland/lakare-allvarliga-vardskador-kopplas-till-problem-med-cosmic), 2026-04-17.
- **E11:** SVT Nyheter Blekinge. [Prostataläkare får kritik – gav felaktiga cancerbesked](https://www.svt.se/nyheter/lokalt/blekinge/prostatalakare-far-kritik-gav-felaktiga-cancerbesked), 2020-05-09.
- **E12:** Lippi G, et al. [Practical recommendations for managing hemolyzed samples in clinical chemistry testing](https://www.degruyterbrill.com/document/doi/10.1515/cclm-2017-1104/html). Clin Chem Lab Med. 2018;56(5):718–27.
- **E13:** Karolinska Universitetssjukhuset. [Lex Maria-ärende K2021-4489](https://www.karolinska.se/om-oss/kvalitet-och-resultat/avvikelser-och-lex-maria/alla-lex-maria-arenden/2021/09/k2021-4489): mixed-up laboratory batches produced four incorrect reports, corrected late.
