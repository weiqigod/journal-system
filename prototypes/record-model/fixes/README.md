# Local EHRbase concurrency patch

This fixes the [observed failures](../../../docs/prototype-findings.md) in our synthetic experiment. It is a project-maintained patch to EHRbase 2.36.0, not an upstream release or an adopted product dependency. The original image, probe, and failure evidence remain unchanged.

## Changes

The [source patch](ehrbase.patch) accepts the quoted version identifier returned in an ETag and retains bare-version compatibility. Upstream updates whichever composition `If-Match` names, ignoring the URL when the body has no `uid`; the patch requires the identifier to name the requested composition and server. A missing composition returns 404. Weak validators and nonmatching identifiers return 412. Malformed headers, including an object identifier without a version, return 400 without writes. This endpoint expects one version identifier, not a general HTTP validator list.

History insertion now selects the expected revision and handles a collision on the history primary key as a concurrency conflict. A losing update returns 412 and a losing delete 409; both roll back. Updating a deleted composition closes its deletion record only while that record is still open, so a concurrent restore loses with 412 instead of colliding on the current-version key. Other database errors still propagate. The implementation does not retry or serialize clinical operations in a proxy.

Version conflicts report the latest version identifier in `ETag` and `Location`, as ITS-REST 1.0.3 requires. The server looks it up after the failed write has rolled back; it names the version to review, not a reservation.

## Reproduce

Prerequisites: Docker Compose, Git, and Python 3.11+. Run the [baseline experiment](../README.md) once first; the archive comparison reads its pinned image. From the repository root:

```sh
docker compose -f prototypes/record-model/compose.yaml stop
python3 prototypes/record-model/fixes/build.py
python3 prototypes/record-model/fixes/compare_archive.py --output prototypes/record-model/runs/fixed-archive.json
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

For the negative control, start the original Compose project and run this probe with `--unpatched-control --if-match-mode bare-diagnostic`. It runs the URL-binding case and all three controlled races against the original image. Each must fail, as must the original update race. The diagnostic header isolates these failures from the original quoted-header failure.

## Evidence and limits

The [evidence manifest](evidence/manifest.json) retains normal quoted-header and bare-compatibility runs, an unpatched control with its server log, restart verification, build provenance, and an archive comparison. The 12 baseline assertions are imported unchanged. Additional checks hold both writers at their first history write using a temporary database lock: for update, delete, and restore of a deleted composition. They check statuses, conflict headers, current and historical content, and head, history, contribution, and audit row counts. Other checks bind `If-Match` to the URL, exercise malformed and nonmatching headers, and inject an unrelated constraint failure. Test controls require the disposable database administrator; they are not application behavior.

The build compiles two changed source classes against the released image's exact dependency jars. Both base images are digest-pinned; the build commands run without network access after image retrieval. This is not a full Maven rebuild or the upstream test suite. [compare_archive.py](compare_archive.py) checks that only the two patched classes and their nested classes differ from the released archive. Shared history code also serves other record types; this evidence covers compositions, including update, delete, and restore conflicts.

Unchanged source files are pinned by [source-lock.json](source-lock.json). Their Apache-2.0 [LICENSE](../upstream/ehrbase/LICENSE) and [NOTICE](../upstream/ehrbase/NOTICE) remain in the parent prototype. Clinical signing, repository/workflow coordination, full standards conformance, and production readiness remain unverified.
