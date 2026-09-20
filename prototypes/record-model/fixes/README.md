# Local EHRbase concurrency patch

This fixes the two [observed failures](../../../docs/prototype-findings.md) in our synthetic experiment. It is a project-maintained patch to EHRbase 2.36.0, not an upstream release or an adopted product dependency. The original image, probe, and failure evidence remain unchanged.

## Changes

The [source patch](ehrbase.patch) accepts the quoted version identifier returned in an ETag, retains bare-version compatibility, and checks the identifier against the requested composition and server. Weak validators and nonmatching identifiers fail; malformed headers fail without writes. This endpoint expects one version identifier, not a general HTTP validator list.

History insertion now selects the expected revision and handles a collision on the history primary key as a concurrency conflict. A losing update returns 412 and rolls back. Delete conflicts retain 409. Other database errors still propagate. The implementation does not retry or serialize clinical operations in a proxy.

## Reproduce

Prerequisites: Docker Compose, Git, and Python 3.11+. From the repository root:

```sh
docker compose -f prototypes/record-model/compose.yaml stop
python3 prototypes/record-model/fixes/build.py
docker compose -f prototypes/record-model/compose.yaml -f prototypes/record-model/fixes/compose.yaml up -d
python3 prototypes/record-model/fixes/probe_fixed.py --output prototypes/record-model/runs/fixed.json
```

The separate Compose project has its own database volume and uses the same localhost-only port. Its report records the actual image ID and build inputs; a moved image tag or changed source fails verification. Use fresh output filenames.

```sh
docker compose -f prototypes/record-model/compose.yaml -f prototypes/record-model/fixes/compose.yaml kill --signal SIGKILL ehrbase db
docker compose -f prototypes/record-model/compose.yaml -f prototypes/record-model/fixes/compose.yaml up -d
python3 prototypes/record-model/fixes/probe_fixed.py --verify-after-restart prototypes/record-model/runs/fixed.json --output prototypes/record-model/runs/fixed-restart.json
docker compose -f prototypes/record-model/compose.yaml -f prototypes/record-model/fixes/compose.yaml stop
```

For the negative control, start the original Compose project and run this probe with `--unpatched-control --if-match-mode bare-diagnostic`. It must report the original update-race failure. The diagnostic header isolates the history failure from the original quoted-header failure.

## Evidence and limits

The [evidence manifest](evidence/manifest.json) retains normal quoted-header and bare-compatibility runs, an unpatched control, restart verification, build provenance, and an archive comparison. The 12 baseline assertions are imported unchanged. Additional checks hold both writers at history insertion using a temporary database lock, check historical content and audit/contribution counts, exercise invalid headers, and inject an unrelated constraint failure. Test controls require the disposable database administrator; they are not application behavior.

The build compiles two changed source classes against the released image's exact dependency jars. Both base images are digest-pinned; the build commands run without network access after image retrieval. This is not a full Maven rebuild or the upstream test suite. Shared history code also serves other record types; this evidence covers compositions, including update and delete conflicts.

Unchanged source files are pinned by [source-lock.json](source-lock.json). Their Apache-2.0 [LICENSE](../upstream/ehrbase/LICENSE) and [NOTICE](../upstream/ehrbase/NOTICE) remain in the parent prototype. Clinical signing, repository/workflow coordination, full standards conformance, and production readiness remain unverified.
