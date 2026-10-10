#!/usr/bin/env python3
"""Compare the released and patched EHRbase archives; only the two patched classes may change."""
import argparse
import hashlib
import io
import json
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
JAR = "/app/ehrbase.jar"
# Nested library and the class the Dockerfile recompiles into it, including its nested classes.
PATCHED = {
    "BOOT-INF/lib/rest-openehr-2.36.0.jar": "org/ehrbase/rest/openehr/OpenehrCompositionController",
    "BOOT-INF/lib/service-2.36.0.jar": "org/ehrbase/repository/AbstractVersionedObjectRepository",
}


def extract(image, directory):
    container = subprocess.check_output(["docker", "create", image], text=True).strip()
    try:
        target = directory / f"{container}.jar"
        subprocess.run(["docker", "cp", f"{container}:{JAR}", str(target)], check=True, stdout=subprocess.DEVNULL)
        return target.read_bytes()
    finally:
        subprocess.run(["docker", "rm", container], check=True, stdout=subprocess.DEVNULL)


def listing(archive):
    return {info.filename: (info.CRC, info.file_size) for info in archive.infolist()}


def differing(before, after):
    return sorted(name for name in before.keys() | after.keys() if before.get(name) != after.get(name))


def intended(library, entry):
    prefix = PATCHED[library]
    return entry == prefix + ".class" or (entry.startswith(prefix + "$") and entry.endswith(".class"))


def compare(original, patched):
    with zipfile.ZipFile(io.BytesIO(original)) as before, zipfile.ZipFile(io.BytesIO(patched)) as after:
        outer_before, outer_after = listing(before), listing(after)
        changed_outer = differing(outer_before, outer_after)
        nested, unexpected = {}, [name for name in changed_outer if name not in PATCHED]
        for library in sorted(set(changed_outer) & PATCHED.keys()):
            with zipfile.ZipFile(io.BytesIO(before.read(library))) as old, \
                    zipfile.ZipFile(io.BytesIO(after.read(library))) as new:
                nested[library] = differing(listing(old), listing(new))
            unexpected += [f"{library}!/{entry}" for entry in nested[library] if not intended(library, entry)]
    complete = all(PATCHED[library] + ".class" in nested.get(library, []) for library in PATCHED)
    return {
        "unchanged_outer_entries": len(outer_before.keys() & outer_after.keys()) - len(set(changed_outer) & outer_before.keys()),
        "changed_nested_entries": nested,
        "unexpected_changes": unexpected,
        "status": "passed" if complete and not unexpected else "failed",
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--build-record", type=Path, default=ROOT / "runs/fixed-build.json")
    args = parser.parse_args()
    if args.output.exists():
        parser.error("Output already exists; use a fresh evidence filename")
    lock = json.loads((ROOT / "upstream.lock.json").read_text())
    record = json.loads(args.build_record.read_text())
    original_id = json.loads(subprocess.check_output(["docker", "image", "inspect", lock["ehrbase"]["image"]]))[0]["Id"]
    with tempfile.TemporaryDirectory(prefix="journal-ehrbase-archive-") as temporary:
        original = extract(lock["ehrbase"]["image"], Path(temporary))
        patched = extract(record["image_id"], Path(temporary))
    report = {
        "original_jar_sha256": hashlib.sha256(original).hexdigest(),
        "patched_jar_sha256": hashlib.sha256(patched).hexdigest(),
        **compare(original, patched),
        "original_image_id": original_id,
        "patched_image_id": record["image_id"],
        "build_record_sha256": hashlib.sha256(args.build_record.read_bytes()).hexdigest(),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n")
    print(report["status"], args.output)
    sys.exit(0 if report["status"] == "passed" else 1)
