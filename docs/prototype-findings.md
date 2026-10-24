# Repository findings

[Foundational design](foundational-design.md) · **Status:** Observed experiment; architecture remains provisional · **Date:** 2026-09-19 · **Updated:** 2026-10-10

The first [executable probe](../prototypes/record-model/README.md) exercised EHRbase 2.36.0 with PostgreSQL 16.15 on arm64, using digest-pinned images and a pinned upstream laboratory test template. Inputs and evidence are recorded in the [source lock](../prototypes/record-model/upstream.lock.json) and [run manifest](../prototypes/record-model/evidence/manifest.json). The template is an Initial test fixture, not a selected production clinical model.

## Results

| Run | Result | Evidence |
|---|---|---|
| Quoted `If-Match`, copied from the server's `ETag` | **Failed:** 7 checks passed, 1 failed, 4 not run. Both updates returned 400. | [HTTP exchanges](../prototypes/record-model/evidence/2026-09-19-etag.json) |
| Unquoted version, explicit diagnostic mode | **Failed in all three runs:** 11 checks passed and 1 failed per run. One concurrent writer received 200; the other received 500. | [Run 1](../prototypes/record-model/evidence/2026-09-19-bare-1.json), [run 2](../prototypes/record-model/evidence/2026-09-19-bare-2.json), [run 3](../prototypes/record-model/evidence/2026-09-19-bare-3.json) |
| Abrupt termination of both containers, followed by restart | **Passed:** both acknowledged revisions retained identical content hashes; AQL returned the same current revision. | [Restart check](../prototypes/record-model/evidence/2026-09-19-restart.json) |

Successful diagnostic checks covered required-field and template rejection without writes, quantity/unit/time retention, lookup under the correct EHR, immutable prior content, stale retry rejection, patient-filtered current queries, and version/contribution audit links. A shared test account and two synthetic EHRs do not establish clinical authorization or tenant isolation.

## Original failures

**P1 — Quoted version preconditions fail.** The server emits a quoted ETag but returns `400 / UUID string too large` when that value is used in `If-Match`. Removing only the quotes allows the update. The retained [REST overview](../references/upstream/openehr/ITS-REST-1.0.3/overview.html) documents quoted headers under “If-Match and accidental overwrites.” The normal test retains this failure; diagnostic mode labels the workaround explicitly.

**P2 — A simultaneous stale writer receives an internal error.** With the diagnostic header, synchronized writes based on the same revision produce one successful update and one 500 in all three recorded runs. The [server log](../prototypes/record-model/evidence/2026-09-19-race-server.log) records a duplicate key on `comp_version_history_pkey`. The retained REST contract requires 412 when the precondition is false. A later stale retry does return 412. History checks found exactly the original and winning revisions; these runs did not show a lost update or extra committed revision.

The extended [negative control](../prototypes/record-model/fixes/evidence/unpatched-control.json) of 2026-10-10 found three more failures in the same release, again with the diagnostic header.

**P3 — A conditional update can change a different composition.** When the request body has no `uid`, the server updates the composition named in `If-Match` and ignores the one in the URL. `PUT …/composition/A` with `If-Match` naming composition B in the same EHR returned 200 and created B version 2; A was unchanged. In a clinical record, this is a write to an item the caller did not address.

**P4 — Concurrent deletes and restores also receive internal errors.** Under the same database gate, a losing delete collides on `comp_version_history_pkey`. A losing update of a deleted composition collides on `comp_version_pkey`. The [server log](../prototypes/record-model/fixes/evidence/unpatched-control-server.log) records both. Row counts showed no extra committed revision.

**P5 — Version conflicts omit the latest version.** REST 1.0.3 returns the latest version in `ETag` and `Location` with 412 for updates and 409 for deletes. None of the recorded conflicts include them, including the stale retries in the [original runs](../prototypes/record-model/evidence/2026-09-19-bare-1.json). A client must re-read before it can review the newer version.

These are findings against this pinned implementation and configuration. They do not establish that the openEHR model is unsuitable. Neither the public README's claim to support the latest REST API nor this small test suite establishes full conformance to any release.

## Local patch verification

P1–P5 are resolved for the tested composition operations by a [local EHRbase source patch](../prototypes/record-model/fixes/README.md). It parses quoted version identifiers and binds them to the requested composition and server. A missing composition returns 404. Collisions on the expected history revision, and on an open deletion record, become controlled conflicts with rollback. Each conflict reports the latest version in `ETag` and `Location`. Other database errors remain errors. The original release and evidence above are unchanged. This revision supersedes the patch evidence recorded at commit `52bddd4`, which predated P3–P5.

| Run | Result | Evidence |
|---|---|---|
| Patched server, quoted ETag | **Passed:** all 12 baseline checks plus 6 regression checks. | [Report](../prototypes/record-model/fixes/evidence/quoted.json) |
| Patched server, bare-version compatibility | **Passed:** all 18 checks. | [Report](../prototypes/record-model/fixes/evidence/bare.json) |
| Original server, same URL-binding case and controlled races | **Failed as expected:** 11 checks passed and 5 failed. The URL-binding update returned 200; the losing update, delete, and restore writers each received 500. | [Negative control](../prototypes/record-model/fixes/evidence/unpatched-control.json) |
| Patched server, abrupt termination and restart | **Passed:** acknowledged versions and current query retained. | [Restart](../prototypes/record-model/fixes/evidence/restart.json) |

The controlled races hold both writers at their first history write before releasing them. Patched updates return 200/412, deletes 204/409, and restores of a deleted composition 200/412. Each conflict reports the winning version in `ETag` and `Location`. Historical revisions remain correct, and the winner's content is current. No losing write adds a contribution, audit, head, or history row. An `If-Match` naming another composition returns 412 and changes neither composition. Of nine header cases, four malformed headers return 400 and a missing composition returns 404. The four nonmatching headers return 412 with the latest version. None writes. An injected, unrelated database constraint violation returns 500, rolls back completely, and permits a successful retry after its removal.

The [build and evidence manifest](../prototypes/record-model/fixes/evidence/manifest.json) pins the local image and inputs. A [scripted archive comparison](../prototypes/record-model/fixes/compare_archive.py) found changes only in the two intended classes and their nested classes. This is a bounded compilation against the released dependencies, not a full upstream rebuild or test-suite run. Other record types using the shared history code remain outside this regression coverage. Upstream submission and adoption remain open; the patch is maintained locally.

## Next experiment

Use the patched experiment to extend the shared cases to exact reviewed snapshots and attestations, durable correction-to-reassessment coordination, and item-level handover acceptance. Select maintained clinical archetypes with authoring sources, a concrete FHIR comparison server and profiles, and terminology/validator versions. Use the same expected outcomes for both candidates. Its pass/fail criteria are the **Verify** statements of [DOC-005](clinical-requirements.md#doc-005--signing-and-confirmation), [DOC-007](clinical-requirements.md#doc-007--correction-and-amendment), [DOC-008](clinical-requirements.md#doc-008--change-history), [ORD-006](clinical-requirements.md#ord-006--result-review-and-follow-up), [WF-005](clinical-requirements.md#wf-005--handover), and [INT-004](platform-requirements.md#int-004--reliable-state-changing-exchange).

The three end-to-end [comparison cases](record-model-comparison.md) remain unverified. The restart result concerns acknowledged writes; interrupted transactions, repository/workflow crash boundaries, and backup restoration remain open.
