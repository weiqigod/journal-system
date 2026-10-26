# Journal System

An open-source, modular clinical information system aiming for comprehensive coverage across countries and care settings. Sweden is the first target.

**Approach:** Map the full scope, build working increments, and verify them against scenarios grounded in published regulations, routines, and incident reports.

**Stage:** Specification, a record-store experiment, and a laboratory workflow prototype; no clinical application yet. Implementation order, module boundaries, and product technology remain open.

## Specification

- [Master specification](SPECIFICATION.md)
- [Coverage map and gaps](docs/coverage.md)
- [Prototype findings and evidence](docs/prototype-findings.md)
- [Run the repository experiment](prototypes/record-model/README.md)
- [Run the laboratory result loop prototype](prototypes/lab-loop/README.md)
- [Earlier draft — v0.2](clinical_information_system_specification_v0.2.md)

**Next:** The [laboratory result loop](docs/workflow-laboratory-results.md) has a [prototype](prototypes/lab-loop/README.md) passing its [scenarios](docs/scenarios-laboratory-results.md); settle the decisions it lists, then connect it to a record store and a laboratory message format. Continue filling the wider coverage gaps alongside it.

## License

- **Code, scripts, and configuration** in `prototypes/`: [EUPL-1.2](LICENSE).
- **Specification and documentation**, the Markdown files in the repository root and `docs/`: [CC BY 4.0](LICENSE-DOCS).
- **Copied upstream material** keeps its original license: everything under `references/upstream/`, and the files listed in `prototypes/record-model/upstream.lock.json` and `prototypes/record-model/fixes/source-lock.json`. The manifests record each license.
- **The EHRbase source patch** (`prototypes/record-model/fixes/ehrbase.patch`) changes Apache-2.0 code and is also offered under Apache-2.0, so it can be submitted upstream.
