# Laboratory result loop prototype

Prototype code, not production code. Work on it has stopped and it will not become the product: it keeps all workflow state in one process's memory, so it cannot scale, and no technology stack has been chosen for the product. It implements the draft rules of the [laboratory result loop](../../docs/workflow-laboratory-results.md) as a Python library and runs the [scenarios](../../docs/scenarios-laboratory-results.md) as automated tests. Its purpose is to show whether the rules hold together as software. It has no user interface, no network laboratory connection, and only synthetic patients. Laboratory reports can be received as FHIR documents.

Workflow state is kept in memory and, optionally, in a SQLite file that survives restarts. Result content goes to a clinical record store: an in-memory stand-in by default, or the patched EHRbase from the [record-model experiment](../record-model/fixes/README.md), which stores each result as an openEHR composition using that experiment's pinned laboratory template.

## Run

Python 3.11 or later, standard library only. From this directory, with the in-memory record store:

```sh
python3 -m unittest -v
```

Against EHRbase, first start the patched stack from the repository root (see the [record-model fixes](../record-model/fixes/README.md) for building the image):

```sh
docker compose -f prototypes/record-model/compose.yaml -f prototypes/record-model/fixes/compose.yaml up -d
```

Then, from this directory:

```sh
LAB_LOOP_RECORDS=ehrbase python3 -m unittest -v
```

`LAB_LOOP_STATE=sqlite` runs every test with workflow state in a temporary SQLite file, and checks after each commit that reloading the file reproduces the state exactly. It combines with either record store.

The observed runs used Python 3.13.7 and the `journal-ehrbase:2.36.0-fixed` image: 80 tests, all passing in all four combinations. One test, which kills a process between the two stores, runs only against EHRbase, since the in-memory record store does not outlive a process.

## Layout

- `lab_loop/model.py` — records: requests, result versions, review obligations, reviews, phone calls, tasks, intake queue, notifications, audit.
- `lab_loop/service.py` — operations and rules R1–R14. Each operation runs as one transaction and restores all workflow state if it fails.
- `lab_loop/records.py` — the record stores and the mapping between result content and the openEHR template.
- `lab_loop/fhir.py` — receives laboratory reports as FHIR R4 document Bundles.
- `lab_loop/store.py` — saves workflow state to SQLite.
- `tests/test_scenarios.py` — S1–S11, one test class per scenario.
- `tests/test_record_store.py` — the boundary between workflow and record store: content location, corrections as composition versions, late versions, concurrent record changes, crashes between the two stores, and merges.
- `tests/test_reconciliation.py` — R15: lost results and corrections adopted, late resends restoring flags, outside changes, missing entries, and entries without a known request.
- `tests/test_fhir.py` — FHIR reports: content and flags, duplicates, corrections, withheld results, unknown codes and patients, rejected Bundles, and a crash partway through a Bundle.
- `tests/test_persistence.py` — encoding, restarts, a crash before commit, and a process killed between the record write and the workflow commit.
- `tests/test_failure_cases.py` — failure cases not already covered by a scenario (F2, F4, F5, F9, F11, F12, F14), plus R1 ownership fallbacks, correction before review, R14 review authority, and refusals leaving no partial state.

## Coverage

| Rule or case | Tests |
|---|---|
| R1, R6, F8 | S1, S5, `R1AlwaysAnOwner` |
| R2, F13 | S7 |
| R3, F18 | S1, S6 |
| R4, F1, F2, F3 | S4, `F2LateOlderVersion`, `CorrectionBeforeReview` |
| R5 | S5 |
| R7, F7, F17 | S2, S2c |
| R13, F6 | S3 |
| R14, F14 | `R14ReviewAuthority`, `F14NoAccess` |
| R8, F5 | S8, `F5UnknownPatient` |
| R9, F10 | S10 |
| R10, F15 | S9 |
| R11 | S1 |
| R12, F16 | S2b |
| R15, F19, F20, F21 | `test_reconciliation.py` |
| R16, F23 | S11, `WithdrawnResults`, FHIR `entered-in-error` tests |
| F4 | `F4CrashBetweenResultAndObligation` |
| F9, F11, F12, F14 | matching `F…` classes |

Each rule and each record-store safeguard was also checked by disabling it in a copy of the code and confirming that at least one test fails, with both stores.

## Workflow and record store

The workflow keeps a reference to each result version, plus the status and flags its rules act on. Value, unit, reference range, comment, and status are written to the record store and read back from it for display and trends. A correction becomes a new version of the same composition, written with `If-Match` on the previous version.

The two stores do not share a transaction. The record write comes first; the workflow commits after. Each write carries a deterministic key (laboratory, request, analyte, laboratory version) in the composition's laboratory test identifier. Before writing, the workflow looks the key up among current versions. If the process fails after the record write, the workflow rolls back, and the retried message finds the existing version instead of writing a duplicate. This relies on the laboratory resending any message the system did not acknowledge; a successful `receive` is the acknowledgement.

If another writer changes a composition first, EHRbase returns 412 and the workflow operation fails without changes.

## What connecting to EHRbase showed

1. **The template has no element for the laboratory's abnormal and critical flags.** They exist only in the workflow index. A selected production template must carry the laboratory's interpretation.
2. **The template has no status for a withheld result.** It is stored as "Cancelled/Aborted", which is an approximation.
3. **Record versions follow arrival order.** A late older laboratory version cannot be stored as history without becoming the record's current version. The prototype keeps only the message. A real design needs the laboratory's version in the content, or a separate history.
4. **Compositions cannot move between EHRs.** After a patient merge, the surviving patient keeps references to both EHRs.
5. **A record written before a crash is safe only if the message is resent.** If the laboratory never resends, the composition exists with no workflow entry. The reconciliation job below handles this.
6. **The template requires the observation's state section,** which this mapping writes empty.


## Decisions made while building

Building the rules exposed four gaps in the workflow outline. They are now settled there:

1. **Correction before review** moves the open obligation to the corrected version (R4).
2. **A withheld result** creates a recollection task for the unit's monitor and notifies the orderer; the request stays open and can become overdue (R13).
3. **A phoned value** takes actions at once, but sign-off waits for the electronic result (R7).
4. **Review authority:** an active physician at the ordering unit, or staff the deployment authorises to review their own orders (R14). Config: `review_roles`, `review_own_orders_roles`.

Timing defaults are configuration: reminder at 7 days, escalation to the monitor and manager 2 days later; overdue requests go to the orderer at the expected time and to the monitor 3 days later.

## Reconciliation

`LabLoop.reconcile()` compares the current compositions in each known EHR with the workflow's result versions (R15). It is meant to run on a schedule; the prototype only provides the call.

| Found | Action |
|---|---|
| Composition with a workflow key but no workflow entry | Adopted as a result, or as a correction if it is newer than the workflow's version, with an owner. Treated as abnormal, since the flags are not in the record. The monitor is notified. |
| Laboratory later resends that version | Its flags replace the assumed ones; a critical flag starts the critical path. |
| Composition whose request the workflow does not know | Reported to the monitor; not adopted. Retrying the original intake files it without a duplicate. |
| Newer composition version not written by the workflow | Reported; not adopted. |
| Workflow version whose composition is gone | Reported. |

Entries younger than `reconcile_after` (default one hour) are skipped, because their message may still be resent. Every action is audited.

## Laboratory message format

`FhirLabAdapter` receives one laboratory report as a FHIR R4 document Bundle shaped after [HL7 Europe Laboratory Report 2.0.0](https://hl7.eu/fhir/laboratory/), the European guide being aligned with the EHDS laboratory report models. It is the prototype's choice, not a decision: which format the first Swedish laboratory sends is still open under [ORD-Q04](../../docs/clinical-requirements.md#orders-investigations-and-results).

| FHIR element | Workflow use |
|---|---|
| `Patient.identifier` with system `urn:oid:1.2.752.129.2.1.3.1` | Personnummer for matching the patient |
| `DiagnosticReport.basedOn` → `ServiceRequest.identifier` of type `PLAC` | The workflow's request ID |
| `ServiceRequest.requester` → `Organization.identifier` | The laboratory's customer code, mapped to the ordering unit |
| `DiagnosticReport.performer` → `Organization.name` | Laboratory |
| `Observation.code.coding` | Mapped to the test name through a configured table, so LOINC, NPU, or local codes can be used |
| `Observation.meta.versionId` | Laboratory version, which orders corrections |
| `Observation.status` | `preliminary`, `final`, `amended`/`corrected`, `cancelled` (withheld), and `entered-in-error` (withdrawn, R16) |
| `Observation.interpretation` | `H`, `L`, `A` are abnormal; `HH`, `LL`, `AA` are critical |
| `valueQuantity`, `referenceRange`, `note`, `dataAbsentReason` | Value, unit, range, and comment |

Each Observation becomes one message, identified by Bundle identifier, Observation ID, and version, so a resent Bundle yields only duplicates. The returned `ReceiveOutcome` is the acknowledgement: results stored, results held in the intake queue, and duplicates. A Bundle that is not a document, lacks a personnummer or performing laboratory, or references an Observation it does not contain is rejected whole with `MessageRejected`, and nothing is stored. An unknown analysis code, an unhandled status such as `registered`, or a missing version goes to the unit's intake queue with the reason. If processing stops partway through a Bundle, resending it stores only what is missing.

The tests use LOINC codes. The adapter reads only the elements above and does not validate Bundles against the guide's profiles; the HL7 validator would be the next step. The guide is based on FHIR R4, while the specification's [verification references](../../docs/verification-references.md) pin R5 for the record-model comparison.

Building it showed two more gaps in the workflow:

1. **A laboratory retraction (`entered-in-error`) had no rule.** R16 now covers it: in EHRbase the composition is deleted, which ends its current version while keeping earlier versions readable, and the clinician must acknowledge the withdrawal.
2. **An unknown analysis code is a normal event,** for example when a laboratory adds a test. It must not drop the result; it is held with the code so the mapping can be extended.

## Workflow persistence

With `LabLoop(..., path="workflow.sqlite")`, each committed operation writes the rows it changed in one SQLite transaction, and a new `LabLoop` on the same path resumes from the last commit. Rows are JSON documents keyed by collection and ID, such as `obligations/ob12`, readable with the sqlite3 shell. An operation interrupted before its commit leaves the file at the previous commit.

The test that kills a process shows the full chain: the child process writes a result to EHRbase and is killed before its workflow commit. After restart, the workflow has no trace of the result; reconciliation adopts the orphaned composition with an owner, and that survives a further restart.

Each commit compares the whole state with its value before the operation, so its cost grows with the amount of data. One process at a time may use a file; concurrent users are not supported.

## Not covered

Concurrent users and processes, sending orders to the laboratory, a network transport for reports, profile validation, 1177 publication, authentication, scheduling of the reconciliation job, and the user interface.
