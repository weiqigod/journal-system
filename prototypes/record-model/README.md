# Clinical record repository experiment

Executable evidence for the [record-model comparison](../../docs/record-model-comparison.md). Read the [findings](../../docs/prototype-findings.md) before interpreting results. This is a synthetic repository probe, not a clinical application or an adopted product stack. The project has since adopted openEHR and implements its own repository instead of running EHRbase; these checks and the patched image are starting material for the [validation harness](../../docs/openehr-validation.md).

A [local source patch and regression suite](fixes/README.md) now resolve the observed failures for the tested composition operations. The commands below reproduce the original unpatched baseline.

## Reproduce

Prerequisites: Docker Compose and Python 3.11+. The observed run used Python 3.13.7 on arm64. Images are pinned by digest; [upstream.lock.json](upstream.lock.json) pins the source documents, SQL bootstrap, OPT, and synthetic fixture. The harness verifies those hashes and the running container images before sending requests.

From the repository root:

```sh
docker compose -f prototypes/record-model/compose.yaml up -d
python3 prototypes/record-model/probe.py --output prototypes/record-model/runs/etag.json
```

The quoted-ETag check currently fails against EHRbase 2.36.0. Exit 1 is a failed check, not success. Reports retain completed, failed, and unexecuted checks plus HTTP exchanges; existing output files are never overwritten.

To investigate the remaining behavior with an explicit compatibility workaround:

```sh
python3 prototypes/record-model/probe.py --if-match-mode bare-diagnostic --output prototypes/record-model/runs/bare.json
```

This mode removes the quotes from `If-Match`. It still exposes a concurrent-update response failure. The report remains failed even when subsequent history and audit checks pass.

After a report contains verified retained state, test persistence across abrupt process termination:

```sh
docker compose -f prototypes/record-model/compose.yaml kill --signal SIGKILL ehrbase db
docker compose -f prototypes/record-model/compose.yaml up -d
python3 prototypes/record-model/probe.py --verify-after-restart prototypes/record-model/runs/bare.json --output prototypes/record-model/runs/restart.json
```

This terminates only this experiment's containers. The restart probe requires changed container start times and unchanged input hashes, then compares both retained versions and the current query result. It does not test backup restoration or a crash during an in-flight write.

```sh
docker compose -f prototypes/record-model/compose.yaml stop
```

The API binds only to `127.0.0.1:18080`; PostgreSQL has no host port. All credentials are public, disposable test values. The database volume remains for inspection. Use fresh report filenames for subsequent runs; each scenario creates new synthetic EHRs.

## Scope and provenance

- `upstream/ehrbase/` contains unchanged files from the pinned source commit, with its LICENSE and NOTICE. The laboratory OPT has lifecycle **Initial** and embeds older archetypes. It exercises repository mechanics; clinical suitability, original template authoring sources, and model maintenance remain unverified.
- `fixtures/laboratory-v1.json` is a project-edited generator example, reduced to a synthetic 22 mm measurement with a fixed clinical time and synthetic author. It makes no diagnostic claim. Metadata still declares RM 1.0.4; the server implements RM 1.1.0. This is not full RM 1.1.0 coverage.
- Invalid instances are explicit mutations: missing composer and an extra element outside the OPT. A valid commit, rejection details, and empty pre-commit queries guard against false-positive rejection tests.
- `evidence/` retains the reviewed runs; scratch runs are ignored by Git. Reports deliberately keep failures. Their digests are listed in [evidence/manifest.json](evidence/manifest.json).

Signing, freshness across multiple records, result reassessment, transfer responsibility, FHIR mapping, clinical authorization, terminology validation, performance, backup/restore, and model portability are not implemented by this probe.
