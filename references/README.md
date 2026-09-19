# Upstream verification references

Use the [verification guide](../docs/verification-references.md) to select material for a test. [manifest.json](manifest.json) records each snapshot's publisher, source URL, release, retrieval date, license, size, and SHA-256 digest. Paths in the manifest are relative to this directory.

`upstream/` contains unmodified HTML pages for text search and clause lookup. Images, stylesheets, scripts, and other linked resources are not mirrored; use the original URLs for complete rendered documents. This is a selected reference set, not a complete offline standards distribution.

## Attribution and maintenance

- openEHR documents are published by the openEHR Specification Program and retain their authorship and copyright notices. Their document license is [CC BY-ND 3.0](https://creativecommons.org/licenses/by-nd/3.0/).
- HL7® FHIR® documents are published by Health Level Seven International. The [retained license page](upstream/fhir/R5/license.html) describes CC0 and third-party notices. Inclusion does not imply endorsement or grant separate terminology rights.
- Keep upstream bytes unchanged. Put interpretations, proposed deviations, and test expectations in project documents.
- Refresh deliberately: review the release and content changes, record the new date and hashes, and identify affected tests. A URL containing a release name is not a substitute for a content digest.

## Check the local snapshots

Run from the repository root; this checks integrity only, not standards conformance:

```sh
python3 - <<'PY'
import hashlib, json
from pathlib import Path
root = Path('references')
artifacts = json.loads((root / 'manifest.json').read_text())['artifacts']
for item in artifacts:
    data = (root / item['path']).read_bytes()
    if len(data) != item['bytes'] or hashlib.sha256(data).hexdigest() != item['sha256']:
        raise SystemExit('Mismatch: ' + item['path'])
print(f'{len(artifacts)} reference snapshots verified')
PY
```
