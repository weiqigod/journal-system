# openEHR validation harness

[Master specification](../SPECIFICATION.md#development-approach) · **Status:** Harness required; design proposed · **Date:** 2026-10-28

The project implements its own openEHR repository instead of running EHRbase, as part of the C# backend on PostgreSQL. The [development approach](../SPECIFICATION.md#development-approach) requires a harness that systematically validates that implementation. This document proposes what the harness checks and how. The design is not adopted; its open choices are [Q-DEV-005–007](decisions.md#development).

## What the harness establishes

For any build, the harness reports which claimed behaviors pass, which fail, and which are untested, and names the source each check rests on. It checks two kinds of obligation separately:

- **openEHR conformance:** behavior the released openEHR specifications define.
- **Product obligations:** behavior the project adds on top, such as signing, correction, and result review in [DOC-005](clinical-requirements.md#doc-005--signing-and-confirmation), [DOC-007](clinical-requirements.md#doc-007--correction-and-amendment), [DOC-008](clinical-requirements.md#doc-008--change-history), and [ORD-006](clinical-requirements.md#ord-006--result-review-and-follow-up). A conforming repository does not establish these.

## Sources of expected behavior

Listed by authority. When sources disagree, the higher one decides and the disagreement is recorded.

| Source | Standing | Use |
|---|---|---|
| Released openEHR specifications: RM, BASE, AM, QUERY (AQL), ITS-REST, ITS-JSON, ITS-XML | Normative | Every conformance case cites a release and clause. [ITS-REST 1.1.0](https://specifications.openehr.org/releases/ITS-REST/Release-1.1.0/) was released on 19 July 2026; the [verification references](verification-references.md) pin 1.0.3. |
| Machine-readable contracts published with them: ITS-REST OpenAPI, ITS-JSON schemas, ITS-XML schemas | Normative as published; frozen at a commit | Every request and response the harness exchanges is validated against them. |
| [openEHR Platform Conformance Test Schedule](https://specifications.openehr.org/releases/CNF/latest/platform_test_schedule.html) and [platform profiles](https://specifications.openehr.org/releases/CNF/latest/profiles.html) | In development; no stable release | Coverage checklist. Its case IDs, such as `I_DEFINITION_ADL14.validate_opt-valid_opt`, are cross-referenced. The template definition, EHR, composition, contribution, directory, and data-validation sections have cases; the stored-query definition, query, demographic, admin, and message sections are mostly placeholders. |
| [Veredictum](https://github.com/rubentalstra/Veredictum) | Independent tool, version 0.x, not approved by the openEHR Specification Editorial Committee | Run unchanged against the implementation's REST API. Its catalogue held 1,146 specification-cited cases when read on 2026-10-28, and it records every exchange. Its reports are not certification. |
| EHRbase, the [patched build](../prototypes/record-model/fixes/README.md) from the repository experiment | Another implementation, with known defects | Differential reference: the same request sequences go to both servers, and each difference is settled against the specification. |
| [Archie](https://github.com/openEHR/archie) | Java library implementing the RM and ADL 2, with validation of instances against operational templates | Second opinion on whether an instance should be accepted. Its README does not describe ADL 1.4 template validation, so its use depends on the template format chosen. |
| Product requirements and the [repository findings](prototype-findings.md) | Project-owned | The requirements above, and P1–P5 from the EHRbase probe, are regression cases from the first slice. |

[EHRbase's integration tests](https://github.com/ehrbase/integration-tests) are tightly coupled to EHRbase's default configuration, by their own README, and include EHRbase-specific features. Individual cases may be adapted after checking them against the specification.

## Kinds of checks

| Check | What it establishes | How |
|---|---|---|
| Specification cases | Each claimed operation behaves as its clause states, including errors. | One small case per behavior over the REST API, with expected status, headers, and body. |
| Contract validation | No exchanged message violates the published schemas. | Validate all harness traffic against the OpenAPI and JSON or XML schemas. |
| Template validation corpus | The repository accepts exactly the instances a template allows. | For each constraint in each test template (occurrences, cardinality, existence, data type, primitive constraint), one valid instance at the boundary and one that breaks only that constraint, plus minimal and maximal instances. Compare decisions with Archie where the format allows. |
| Round trip | Stored content comes back unchanged. | Compare retrieved instances with submitted ones, element by element, excluding server-assigned values. |
| Version history | Versions, contributions, and audit stay consistent under any sequence of operations. | Generate operation sequences (create, update, delete, restore, stale writes) and compare the repository's history with a simple reference model after each step. |
| Concurrency and failure | Races and crashes do not lose acknowledged writes, add versions, or produce internal errors. | Hold concurrent writers at the same history point, as the EHRbase probe did, and terminate the process at each persistence boundary before restarting. |
| Query corpus | AQL returns the right rows. | A fixed synthetic data set with expected results per query, also run against EHRbase. |
| Differential runs | Divergence from another implementation is noticed and explained. | Same sequences against EHRbase, with identifiers and timestamps normalized. |

## Run rules

- Every case cites its source (release and clause, external case ID, or requirement ID) and states its expected outcome before it is run.
- A run records the build, configuration, harness version, input hashes, every exchange, and each observed outcome. Failures stay in the record; known failures are marked, not removed.
- The implementation declares what it claims: specification releases, conformance profile, and formats. A coverage matrix lists each operation and clause in that scope as passing, failing, not yet implemented, or not applicable with a reason. Parts not claimed are reported as not claimed.
- Where the specification is silent or contradictory, the chosen behavior is recorded with the clause in an ambiguity register.
- Each vertical slice adds its cases before its implementation, and the whole harness runs on every change.
- Passing the harness is not openEHR certification. None is offered, and the conformance specifications have no stable release.

## Tooling

The project's own cases are written in C# with NUnit, per the development approach. Veredictum, EHRbase, and Archie would run as separate pinned reference tools, not product code; whether to use them is [Q-DEV-007](decisions.md#development).

Veredictum and REST differential runs need the implementation to expose the openEHR REST API. Without it, the harness can run only its own cases through internal interfaces. That is [Q-DEV-006](decisions.md#development).

## Starting material in this repository

- Pinned openEHR specification pages and their manifest: [verification references](verification-references.md).
- The EHRbase probe and patch suites: 18 checks, including P1–P5 ([findings](prototype-findings.md)).
- The patched EHRbase image, `journal-ehrbase:2.36.0-fixed`, for differential runs.
- The laboratory test template and synthetic fixture. The template's lifecycle is Initial; it tests mechanics, not clinical suitability.
- The [lab-loop findings](../prototypes/lab-loop/README.md#what-connecting-to-ehrbase-showed) on what that template lacks.
