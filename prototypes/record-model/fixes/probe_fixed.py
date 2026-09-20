#!/usr/bin/env python3
"""Run unchanged baseline assertions plus controlled concurrency regressions."""
import argparse
import copy
import json
import select
import subprocess
import sys
import threading
import time
import uuid
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import build

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT))
import probe as baseline


class FixedProbe(baseline.Probe):
    def __init__(self, output, previous, mode, build_record, control):
        super().__init__(output, previous, mode)
        self.build_record = build_record
        self.control = control
        self.compose = ["docker", "compose", "-f", str(ROOT / "compose.yaml")]
        if not control:
            self.compose += ["-f", str(HERE / "compose.yaml")]
        self.report["runtime_variant"] = "unpatched-control" if control else "local-source-patch"
        if previous is None:
            cases = [("forced_update_race", "Both writers reach history insertion; one succeeds and one returns 412")]
            if not control:
                cases += [
                    ("header_preconditions", "Invalid or nonmatching version headers create no writes"),
                    ("unrelated_database_error", "An unrelated constraint violation remains an error and rolls back"),
                    ("forced_delete_race", "Concurrent deletes retain one deletion and return a controlled conflict"),
                ]
            self.report["checks"] += [
                {"id": key, "expected": expected, "status": "not_run"} for key, expected in cases
            ]

    def verify_inputs(self):
        lock = json.loads((ROOT / "upstream.lock.json").read_text())
        for item in lock["artifacts"] + lock["fixtures"]:
            raw = (ROOT / item["path"]).read_bytes()
            if len(raw) != item["bytes"] or baseline.digest(raw) != item["sha256"]:
                raise AssertionError("Input mismatch: " + item["path"])
        record = json.loads(self.build_record.read_text())
        if record["inputs"] != build.build_inputs():
            raise AssertionError("Rebuild the patched image after changing build inputs")
        ids = subprocess.check_output(self.compose + ["ps", "-q"], text=True).split()
        if len(ids) != 2:
            raise AssertionError("Expected this experiment's two running containers")
        containers = json.loads(subprocess.check_output(["docker", "inspect", *ids]))
        by_service = {c["Config"]["Labels"]["com.docker.compose.service"]: c for c in containers}
        expected = lock["ehrbase"]["image"] if self.control else record["image"]
        if by_service["ehrbase"]["Config"]["Image"] != expected:
            raise AssertionError("Unexpected EHRbase image reference")
        if not self.control and by_service["ehrbase"]["Image"] != record["image_id"]:
            raise AssertionError("Running image does not match the recorded build")
        if by_service["db"]["Config"]["Image"] != lock["postgres"]["image"]:
            raise AssertionError("Unexpected PostgreSQL image")
        if by_service["ehrbase"]["NetworkSettings"]["Ports"]["8080/tcp"] != [
            {"HostIp": "127.0.0.1", "HostPort": "18080"}
        ]:
            raise AssertionError("Unexpected API binding")
        paths = {
            "upstream_lock_sha256": ROOT / "upstream.lock.json",
            "compose_sha256": ROOT / "compose.yaml",
            "probe_sha256": Path(__file__),
            "reference_manifest_sha256": ROOT.parents[1] / "references/manifest.json",
            "baseline_probe_sha256": ROOT / "probe.py",
            "fixed_compose_sha256": HERE / "compose.yaml",
            "build_record_sha256": self.build_record,
        }
        self.report["inputs"] = {key: build.digest(path) for key, path in paths.items()}
        self.report["inputs"]["containers"] = {
            name: {"image_reference": c["Config"]["Image"], "image_id": c["Image"],
                   "started_at": c["State"]["StartedAt"]} for name, c in by_service.items()
        }

    def sql(self, statement):
        result = subprocess.check_output(
            self.compose + ["exec", "-T", "db", "psql", "-X", "-qAt", "-v", "ON_ERROR_STOP=1",
                            "-U", "ehrbase", "-d", "ehrbase", "-c", statement], text=True, timeout=15
        ).strip()
        self.report.setdefault("database_controls", []).append({"sql": statement, "result": result})
        return result

    def counts(self):
        return json.loads(self.sql("SELECT json_build_array("
            "(SELECT count(*) FROM ehr.comp_version),"
            "(SELECT count(*) FROM ehr.comp_version_history),"
            "(SELECT count(*) FROM ehr.contribution),"
            "(SELECT count(*) FROM ehr.audit_details))"))

    def fresh(self):
        _, ehr = self.expect("POST", "/ehr", 201, headers={"Prefer": "return=representation"})
        endpoint = f'/ehr/{ehr["ehr_id"]["value"]}/composition'
        fixture = json.loads((ROOT / "fixtures/laboratory-v1.json").read_text())
        _, first = self.expect("POST", endpoint, 201, body=fixture, headers={"Prefer": "return=representation"})
        version = first["uid"]["value"]
        object_id = version.split("::")[0]
        _, first = self.expect("GET", endpoint + "/" + version, 200)
        return endpoint, object_id, version, first

    def put(self, endpoint, object_id, version, first, value=25.0, header=None):
        body = copy.deepcopy(first)
        body.pop("uid", None)
        baseline.quantity(body)["magnitude"] = value
        if header is None:
            header = version if self.if_match_mode == "bare-diagnostic" else f'"{version}"'
        return self.request("PUT", endpoint + "/" + object_id, body=body,
                            headers={"If-Match": header, "Prefer": "return=representation"})

    def forced_race(self, operation):
        endpoint, object_id, version, first = self.fresh()
        before = self.counts()
        gate = subprocess.Popen(
            self.compose + ["exec", "-T", "db", "psql", "-X", "-qAt", "-v", "ON_ERROR_STOP=1",
                            "-U", "ehrbase", "-d", "ehrbase"],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
        )
        # SHARE permits reads, but blocks both history INSERTs after their version checks.
        lock_sql = "BEGIN; SET LOCAL lock_timeout = '5s'; LOCK TABLE ehr.comp_version_history IN SHARE MODE;"
        gate.stdin.write(lock_sql + "\n\\echo gate-ready\n")
        gate.stdin.flush()
        waiting = 0
        barrier = threading.Barrier(2, timeout=5)

        def write(value):
            barrier.wait()
            if operation == "update":
                return self.put(endpoint, object_id, version, first, value)[0]
            return self.request("DELETE", endpoint + "/" + version)[0]

        try:
            if not select.select([gate.stdout], [], [], 8)[0] or gate.stdout.readline().strip() != "gate-ready":
                raise AssertionError("Database gate did not become ready")
            with ThreadPoolExecutor(max_workers=2) as pool:
                futures = [pool.submit(write, value) for value in (31.0, 32.0)]
                try:
                    deadline = time.monotonic() + 8
                    while time.monotonic() < deadline:
                        waiting = int(self.sql("SELECT count(*) FROM pg_locks WHERE "
                            "relation = 'ehr.comp_version_history'::regclass "
                            "AND mode = 'RowExclusiveLock' AND NOT granted"))
                        if waiting == 2:
                            break
                        time.sleep(0.05)
                finally:
                    gate.communicate("ROLLBACK;\n\\q\n", timeout=10)
                statuses = sorted(f.result(timeout=25) for f in futures)
        finally:
            if gate.poll() is None:
                gate.communicate("ROLLBACK;\n\\q\n", timeout=10)
        after = self.counts()
        delta = [new - old for old, new in zip(before, after)]
        _, original = self.expect("GET", endpoint + "/" + version, 200)
        _, history = self.expect("GET", endpoint.replace("/composition", "/versioned_composition")
                                 + "/" + object_id + "/revision_history", 200)
        revisions = sorted(item["version_id"]["value"] for item in history["items"])
        expected_versions = [version, version.rsplit("::", 1)[0] + "::2"]
        expected_statuses = [200, 412] if operation == "update" else [204, 409]
        expected_delta = [0, 1, 1, 2] if operation == "update" else [-1, 2, 1, 2]
        self.check("forced_" + operation + "_race",
                   waiting == 2 and statuses == expected_statuses and delta == expected_delta
                   and original == first and revisions == expected_versions,
                   {"gate_sql": lock_sql, "blocked_writers": waiting, "statuses": statuses,
                    "row_delta_order": ["head", "history", "contribution", "audit"], "row_delta": delta,
                    "original_unchanged": original == first, "revisions": revisions}, abort=False)

    def header_preconditions(self):
        endpoint, object_id, version, first = self.fresh()
        before = self.counts()
        cases = [
            ("weak", 'W/"' + version + '"', object_id, 412),
            ("unterminated", '"' + version, object_id, 400),
            ("multiple", f'"{version}", "{version}"', object_id, 400),
            ("empty", "", object_id, 400),
            ("other object", f'"{uuid.uuid4()}::journal-prototype.local::1"', object_id, 412),
            ("other system", '"' + version.replace("journal-prototype.local", "another.system") + '"', object_id, 412),
            ("future version", '"' + version.rsplit("::", 1)[0] + '::2"', object_id, 412),
            ("other URL object", f'"{version}"', str(uuid.uuid4()), 412),
        ]
        observed = []
        for name, header, target, expected in cases:
            status, _, _ = self.put(endpoint, target, version, first, header=header)
            observed.append({"case": name, "status": status, "expected": expected})
        _, after = self.expect("GET", endpoint + "/" + object_id, 200)
        self.check("header_preconditions", all(x["status"] == x["expected"] for x in observed)
                   and after == first and before == self.counts(), {"cases": observed, "content_unchanged": after == first})

    def database_error(self):
        endpoint, object_id, version, first = self.fresh()
        before = self.counts()
        # Only this fresh composition is affected; always remove the injected constraint.
        self.sql(f"ALTER TABLE ehr.comp_version_history ADD CONSTRAINT journal_test_fault "
                 f"CHECK (vo_id <> '{object_id}'::uuid) NOT VALID")
        try:
            status, _, _ = self.put(endpoint, object_id, version, first)
        finally:
            self.sql("ALTER TABLE ehr.comp_version_history DROP CONSTRAINT journal_test_fault")
        _, after = self.expect("GET", endpoint + "/" + object_id, 200)
        unchanged = after == first and before == self.counts()
        retry_status, _, _ = self.put(endpoint, object_id, version, first)
        self.check("unrelated_database_error", status == 500 and unchanged and retry_status == 200,
                   {"injected_error_status": status, "no_partial_writes": unchanged, "retry_status": retry_status})

    def scenario(self):
        super().scenario()
        self.forced_race("update")
        if not self.control:
            self.header_preconditions()
            self.database_error()
            self.forced_race("delete")

    def verify_previous(self):
        previous = json.loads(self.previous.read_text())
        if previous["runtime_variant"] != self.report["runtime_variant"]:
            raise AssertionError("Restart runtime variant changed")
        for key, value in previous["inputs"].items():
            if key != "containers" and value != self.report["inputs"][key]:
                raise AssertionError("Restart input changed: " + key)
        super().verify_previous()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--verify-after-restart", type=Path)
    parser.add_argument("--build-record", type=Path, default=ROOT / "runs/fixed-build.json")
    parser.add_argument("--if-match-mode", choices=["etag", "bare-diagnostic"], default="etag")
    parser.add_argument("--unpatched-control", action="store_true")
    args = parser.parse_args()
    if args.output.exists():
        parser.error("Output already exists; use a fresh evidence filename")
    sys.exit(FixedProbe(args.output, args.verify_after_restart, args.if_match_mode,
                        args.build_record, args.unpatched_control).run())
