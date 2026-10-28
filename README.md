# Journal System

An open-source, modular clinical information system aiming for comprehensive coverage across countries and care settings. Sweden is the first target.

**Approach:** Map the full scope, build working increments, and verify them against scenarios grounded in published regulations, routines, and incident reports.

**Stage:** Specification, a record-store experiment, and a laboratory workflow prototype; no clinical application yet. The [development approach](SPECIFICATION.md#development-approach) is adopted: C# backend on ASP.NET Core with Dapper, Svelte frontend in TypeScript on SvelteKit, PostgreSQL, NUnit and Vitest for tests, an openEHR record model implemented by the project and checked by a validation harness, clean architecture, object orientation, domain-driven design, test-driven development, and vertical slices. Implementation order, module boundaries, and the rest of the technology remain open.

## Specification

- [Master specification](SPECIFICATION.md)
- [Coverage map and gaps](docs/coverage.md)
- [Prototype findings and evidence](docs/prototype-findings.md)
- [Run the repository experiment](prototypes/record-model/README.md)
- [Run the laboratory result loop prototype](prototypes/lab-loop/README.md)
- [Earlier draft — v0.2](clinical_information_system_specification_v0.2.md)

**Next:** Decide the roadmap, the backlog, the rest of the technology stack, the openEHR scope, and the [validation harness](docs/openehr-validation.md) design ([open development questions](docs/decisions.md#development)). No product code is written until those are settled. Work on the [laboratory result loop prototype](prototypes/lab-loop/README.md) has stopped: it tested the [workflow rules](docs/workflow-laboratory-results.md) against its [scenarios](docs/scenarios-laboratory-results.md) and EHRbase, and its findings are in [prototype findings](docs/prototype-findings.md). It is not designed to scale and is not the start of the product. Continue filling the wider coverage gaps alongside these decisions.

## License

- **Code, scripts, and configuration** in `prototypes/`: [EUPL-1.2](LICENSE).
- **Specification and documentation**, the Markdown files in the repository root and `docs/`: [CC BY 4.0](LICENSE-DOCS).
- **Copied upstream material** keeps its original license: everything under `references/upstream/`, and the files listed in `prototypes/record-model/upstream.lock.json` and `prototypes/record-model/fixes/source-lock.json`. The manifests record each license.
- **The EHRbase source patch** (`prototypes/record-model/fixes/ehrbase.patch`) changes Apache-2.0 code and is also offered under Apache-2.0, so it can be submitted upstream.
