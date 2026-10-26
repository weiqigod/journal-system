# Laboratory result loop prototype

Prototype code, not production code. It implements the draft rules of the [laboratory result loop](../../docs/workflow-laboratory-results.md) as an in-memory Python library and runs the [scenarios](../../docs/scenarios-laboratory-results.md) as automated tests. Its purpose is to show whether the rules hold together as software. It has no user interface, no real laboratory interface, no persistent storage, and only synthetic patients.

## Run

Python 3.11 or later, standard library only. From this directory:

```sh
python3 -m unittest -v
```

The observed run used Python 3.13.7: 38 tests, all passing.

## Layout

- `lab_loop/model.py` — records: requests, result versions, review obligations, reviews, phone calls, tasks, intake queue, notifications, audit.
- `lab_loop/service.py` — operations and rules R1–R12. Each operation runs as one transaction and restores all state if it fails.
- `tests/test_scenarios.py` — S1–S10, one test class per scenario.
- `tests/test_failure_cases.py` — failure cases not already covered by a scenario (F2, F4, F5, F9, F11, F12, F14), plus R1 ownership fallbacks, correction before review, and refusals leaving no partial state.

## Coverage

| Rule or case | Tests |
|---|---|
| R1, R6, F8 | S1, S5, `R1AlwaysAnOwner` |
| R2, F13 | S7 |
| R3, F18 | S1, S6 |
| R4, F1, F2, F3 | S4, `F2LateOlderVersion`, `CorrectionBeforeReview` |
| R5 | S5 |
| R7, F7, F17 | S2, S2c |
| R8, F5 | S8, `F5UnknownPatient` |
| R9, F10 | S10 |
| R10, F15 | S9 |
| R11 | S1 |
| R12, F16 | S2b |
| F4 | `F4CrashBetweenResultAndObligation` |
| F6 | S3 |
| F9, F11, F12, F14 | matching `F…` classes |

Each rule was also checked by disabling it in a copy of the code and confirming that at least one test fails.

## Decisions the specification left open

Building the rules required choices the workflow does not yet state. They are assumptions of this prototype:

1. **A correction before review moves the open obligation to the newer version** instead of closing one and opening another. The workflow's state table lists "superseded by correction"; one obligation per result with a version pointer proved simpler and still satisfies R1.
2. **A withheld result creates no review obligation.** It creates a recollection task for the unit's monitor, and the request stays open until a usable result arrives.
3. **A phoned value cannot be reviewed until the electronic result arrives.** Actions can be recorded against it at once.
4. **Only a physician at the patient's listed unit may review.** This stands in for the authorization rules of [IAM-004](../../docs/platform-requirements.md#iam-004--context-sensitive-authorization).
5. **Escalation timing:** reminder at 7 days, escalation to the monitor and manager 2 days later; overdue requests go to the orderer at the expected time and to the monitor 3 days later. All are configuration.

## Not covered

Persistence across restarts, concurrent users, a real laboratory message format, 1177 publication, authentication, and the user interface.
