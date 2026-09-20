# Repository findings

[Foundational design](foundational-design.md) · **Status:** Observed experiment; architecture remains provisional · **Date:** 2026-09-19

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

These are findings against this pinned implementation and configuration. They do not establish that the openEHR model is unsuitable. Neither the public README's claim to support the latest REST API nor this small test suite establishes full conformance to any release.

## Local patch verification

Both failures are resolved for the tested composition operations by a [local EHRbase source patch](../prototypes/record-model/fixes/README.md). It parses quoted version identifiers, binds them to the requested composition and server, and converts a collision on the expected history revision into a controlled conflict with rollback. Other database errors remain errors. The original release and evidence above are unchanged.

| Run | Result | Evidence |
|---|---|---|
| Patched server, quoted ETag | **Passed:** all 12 baseline checks plus 4 regression checks. | [Report](../prototypes/record-model/fixes/evidence/quoted.json) |
| Patched server, bare-version compatibility | **Passed:** all 16 checks. | [Report](../prototypes/record-model/fixes/evidence/bare.json) |
| Original server, same controlled update race | **Failed as expected:** both writers reached history insertion; responses were 200 and 500. | [Negative control](../prototypes/record-model/fixes/evidence/unpatched-control.json) |
| Patched server, abrupt termination and restart | **Passed:** acknowledged versions and current query retained. | [Restart](../prototypes/record-model/fixes/evidence/restart.json) |

The controlled races block both writers at history insertion before releasing them. The patched update returns 200/412; deletion returns 204/409. Historical content and revision counts remain correct, with no extra contribution or audit rows from the losing write. Eight malformed or nonmatching header cases leave data unchanged. An injected, unrelated database constraint violation returns 500, rolls back completely, and permits a successful retry after its removal.

The [build and evidence manifest](../prototypes/record-model/fixes/evidence/manifest.json) pins the local image and inputs. Archive comparison found changes only in the two intended classes and their nested classes. This is a bounded compilation against the released dependencies, not a full upstream rebuild or test-suite run. Other record types using the shared history code remain outside this regression coverage. Upstream submission and adoption remain open; the patch is maintained locally.

## Next experiment

Use the patched experiment to extend the shared cases to exact reviewed snapshots and attestations, durable correction-to-reassessment coordination, and item-level handover acceptance. Select maintained clinical archetypes with authoring sources, a concrete FHIR comparison server and profiles, and terminology/validator versions. Use the same expected outcomes for both candidates.

The three end-to-end [comparison cases](record-model-comparison.md) remain unverified. The restart result concerns acknowledged writes; interrupted transactions, repository/workflow crash boundaries, and backup restoration remain open.
