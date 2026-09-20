#!/usr/bin/env python3
"""Build and record the local EHRbase patch without changing the baseline image."""
import hashlib
import json
import shutil
import subprocess
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
IMAGE = "journal-ehrbase:2.36.0-fixed"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_inputs():
    lock = json.loads((HERE / "source-lock.json").read_text())
    for item in lock["artifacts"]:
        path = HERE / item["path"]
        if path.stat().st_size != item["bytes"] or digest(path) != item["sha256"]:
            raise ValueError("Upstream source mismatch: " + item["path"])
    paths = ["Dockerfile", "ehrbase.patch", "source-lock.json", "build.py"]
    paths += [item["path"] for item in lock["artifacts"]]
    return {path: digest(HERE / path) for path in paths}


if __name__ == "__main__":
    inputs = build_inputs()
    with tempfile.TemporaryDirectory(prefix="journal-ehrbase-build-") as temporary:
        context = Path(temporary)
        source = context / "source"
        source.mkdir()
        lock = json.loads((HERE / "source-lock.json").read_text())
        for item in lock["artifacts"]:
            path = context / item["source_path"]
            path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(HERE / item["path"], path)
        subprocess.run(["git", "apply", "--check", str(HERE / "ehrbase.patch")], cwd=context, check=True)
        subprocess.run(["git", "apply", str(HERE / "ehrbase.patch")], cwd=context, check=True)
        for item in lock["artifacts"]:
            shutil.copyfile(context / item["source_path"], source / Path(item["path"]).name)
        shutil.copyfile(HERE / "Dockerfile", context / "Dockerfile")
        subprocess.run(["docker", "build", "--network=none", "-t", IMAGE, str(context)], check=True)
    info = json.loads(subprocess.check_output(["docker", "image", "inspect", IMAGE]))[0]
    record = {"image": IMAGE, "image_id": info["Id"], "architecture": info["Architecture"], "inputs": inputs}
    output = HERE.parent / "runs/fixed-build.json"
    output.parent.mkdir(exist_ok=True)
    output.write_text(json.dumps(record, indent=2) + "\n")
    print(output)
