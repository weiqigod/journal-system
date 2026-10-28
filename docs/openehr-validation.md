# openEHR validation harness

[Master specification](../SPECIFICATION.md#development-approach) · **Status:** Harness required; design proposed · **Date:** 2026-10-28

The project implements its own openEHR repository as part of the C# backend on PostgreSQL. The [development approach](../SPECIFICATION.md#development-approach) requires a harness that systematically validates that implementation against the current openEHR releases. This document proposes what the harness checks and how. The design is not adopted; its open choices are [Q-DEV-005–007](decisions.md#development).

## Target releases

The implementation and harness target the current released openEHR specifications. On 2026-10-28 these are:

| Component | Release | Published |
|---|---|---|
| BASE | 1.2.0 | 9 April 2021 |
| RM | 1.1.0 | 29 September 2020 |
| AM | 2.3.0 | 20 March 2024 |
| QUERY (AQL) | 1.1.0 | 14 May 2021 |
| ITS-REST | 1.1.0 | 19 July 2026 |
| ITS-XML | 2.0.0 | 26 April 2021 |
| TERM | 3.0.0 | 26 June 2023 |

Source: [openEHR releases](https://specifications.openehr.org/releases). ITS-JSON is published without a release number on that page; its schemas are pinned by commit. A new openEHR release is a reason to review this target.

AM 2.3.0 contains two archetype formalisms, both marked STABLE: ADL 2 with AOM 2, which is the current formalism, and ADL 1.4 with AOM 1.4. Its operational template format for ADL 2, OPT 2, is still in DEVELOPMENT. ITS-REST 1.1.0 defines template endpoints for both. The implementation uses ADL 2.

The implementation covers all of AQL 1.1.0, built slice by slice. Parts not yet built are reported as not yet implemented.

## What the harness establishes

For any build, the harness reports which claimed behaviors pass, which fail, and which are untested, and names the source each check rests on. It checks two kinds of obligation separately:

- **openEHR conformance:** behavior the target releases define.
- **Product obligations:** behavior the project adds on top, such as signing, correction, and result review in [DOC-005](clinical-requirements.md#doc-005--signing-and-confirmation), [DOC-007](clinical-requirements.md#doc-007--correction-and-amendment), [DOC-008](clinical-requirements.md#doc-008--change-history), and [ORD-006](clinical-requirements.md#ord-006--result-review-and-follow-up). A conforming repository does not establish these.

## Sources of expected behavior

Listed by authority. When sources disagree, the higher one decides and the disagreement is recorded.

| Source | Standing | Use |
|---|---|---|
| The target releases above | Normative | Every conformance case cites a release and clause. Local copies are in the [reference pack](verification-references.md). |
| Machine-readable contracts for those releases: ITS-REST OpenAPI, ITS-JSON schemas, ITS-XML schemas | Normative as published; frozen at a commit | Every request and response the harness exchanges is validated against them. |
| [openEHR Platform Conformance Test Schedule](https://specifications.openehr.org/releases/CNF/latest/platform_test_schedule.html) and [platform profiles](https://specifications.openehr.org/releases/CNF/latest/profiles.html) | In development; no stable release | Coverage checklist. Its case IDs, such as `I_DEFINITION_ADL14.validate_opt-valid_opt`, are cross-referenced. The template definition, EHR, composition, contribution, directory, and data-validation sections have cases; the stored-query definition, query, demographic, admin, and message sections are mostly placeholders. |
| [Veredictum](https://github.com/rubentalstra/Veredictum) | Independent tool, version 0.x, not approved by the openEHR Specification Editorial Committee | Run against the implementation's REST API. Each of its cases declares the specification versions it applies to; only cases covering the target releases count. Its catalogue held 1,146 specification-cited cases when read on 2026-10-28. Its reports are not certification. |
| [Archie](https://github.com/openEHR/archie) | Java library implementing the RM and ADL 2, with validation of instances against operational templates | Second opinion on whether an instance should be accepted. |
| Product requirements | Project-owned | Cases for the requirements above and those added by each slice. |

Implementations that do not state support for the target releases are not used as references. EHRbase's release notes mention neither ITS-REST 1.1.0 nor ADL 2, and the project's earlier EHRbase experiment used REST 1.0.3 and an ADL 1.4 template.

## Kinds of checks

| Check | What it establishes | How |
|---|---|---|
| Specification cases | Each claimed operation behaves as its clause states, including errors. | One small case per behavior over the REST API, with expected status, headers, and body. |
| Contract validation | No exchanged message violates the published schemas. | Validate all harness traffic against the OpenAPI and JSON or XML schemas. |
| Template validation corpus | The repository accepts exactly the instances a template allows. | For each constraint in each test template (occurrences, cardinality, existence, data type, primitive constraint), one valid instance at the boundary and one that breaks only that constraint, plus minimal and maximal instances. Compare decisions with Archie. |
| Round trip | Stored content comes back unchanged. | Compare retrieved instances with submitted ones, element by element, excluding server-assigned values. |
| Version history | Versions, contributions, and audit stay consistent under any sequence of operations. | Generate operation sequences (create, update, delete, restore, stale writes) and compare the repository's history with a simple reference model after each step. |
| Concurrency and failure | Races and crashes do not lose acknowledged writes, add versions, or produce internal errors. | Hold concurrent writers at the same history point before releasing them, and terminate the process at each persistence boundary before restarting. |
| Query corpus | AQL returns the right rows. | A fixed synthetic data set with expected results per query, derived from the AQL specification. |

## Run rules

- Every case cites its source (release and clause, external case ID, or requirement ID) and states its expected outcome before it is run.
- A run records the build, configuration, harness version, input hashes, every exchange, and each observed outcome. Failures stay in the record; known failures are marked, not removed.
- The implementation declares what it claims: releases, conformance profile, and formats. A coverage matrix lists each operation and clause in that scope as passing, failing, not yet implemented, or not applicable with a reason. Parts not claimed are reported as not claimed.
- Where the specification is silent or contradictory, the chosen behavior is recorded with the clause in an ambiguity register.
- Each vertical slice adds its cases before its implementation, and the whole harness runs on every change.
- Passing the harness is not openEHR certification. None is offered, and the conformance specifications have no stable release.

## Tooling

The project's own cases are written in C# with NUnit, per the development approach. Veredictum and Archie would run as separate pinned tools, not product code; whether to use them is [Q-DEV-007](decisions.md#development).

Veredictum needs the implementation to expose the openEHR REST API. Without it, the harness can run only its own cases through internal interfaces. That is [Q-DEV-006](decisions.md#development).
