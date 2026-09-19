#!/usr/bin/env python3
"""Live, synthetic-only repository checks against the pinned local Compose stack."""

import argparse
import base64
import copy
import hashlib
import json
import platform
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path


HERE = Path(__file__).resolve().parent
BASE = "http://127.0.0.1:18080/ehrbase/rest/openehr/v1"
AUTH = "Basic " + base64.b64encode(b"prototype:prototype-only").decode()
TEMPLATE = "65d9e89a-81d8-4344-afbe-88508d42dcfc"
CASES = {
    "authentication": ("Unauthenticated repository request is rejected", ["IAM-001"], "Prototype BASIC configuration; not clinical authorization"),
    "template": ("Stored OPT equals the pinned template", ["DOC-003"], "ITS-REST 1.0.3 Definition API: template upload/retrieval"),
    "ehr_creation": ("Two distinct synthetic EHRs are created", ["INF-001"], "ITS-REST 1.0.3 EHR API: create EHR"),
    "required_field": ("Missing mandatory composer is rejected without writing", ["DOC-001"], "RM 1.1.0 EHR: COMPOSITION; ITS-REST composition POST"),
    "extra_node": ("An element outside the template is rejected without writing", ["DOC-003"], "Pinned OPT and EHRbase check-for-extra-nodes configuration"),
    "create_read": ("Quantity, units and clinical time survive commit/read", ["INF-004", "ORD-004"], "RM 1.1.0 data types; ITS-REST composition POST/GET"),
    "ehr_scope": ("Composition lookup under a different EHR fails", ["INF-001"], "ITS-REST 1.0.3 EHR API: get composition"),
    "concurrent_update": ("Exactly one of two writes using the same version succeeds", ["DOC-005", "DOC-008"], "ITS-REST 1.0.3 EHR API: update composition, If-Match"),
    "history": ("Original and winning revisions remain independently retrievable", ["DOC-007", "DOC-008"], "RM 1.1.0 Common section 6; ITS-REST composition GET"),
    "stale_retry": ("Replaying the old update fails without creating another revision", ["INT-004"], "ITS-REST 1.0.3 EHR API: update composition, If-Match"),
    "query": ("Patient-filtered AQL returns the current version and no cross-EHR rows", ["DOC-009"], "QUERY 1.1.0 AQL: FROM/WHERE; ITS-REST Query API"),
    "audit": ("Version history has two revisions and an attributable contribution", ["INF-002", "DOC-008"], "RM 1.1.0 Common section 6; ITS-REST versioned composition/contribution GET"),
}


def digest(data):
    return hashlib.sha256(data).hexdigest()


def json_bytes(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def quantity(composition):
    """Locate the single retained synthetic quantity; fail on fixture drift."""
    found = []

    def visit(value):
        if isinstance(value, dict):
            if value.get("_type") == "DV_QUANTITY":
                found.append(value)
            for child in value.values():
                visit(child)
        elif isinstance(value, list):
            for child in value:
                visit(child)

    visit(composition)
    if len(found) != 1:
        raise ValueError(f"Expected one quantity, found {len(found)}")
    return found[0]


def xml_structure(data):
    def node(element):
        return (element.tag, sorted(element.attrib.items()), (element.text or "").strip(),
                [node(child) for child in element])
    return node(ET.fromstring(data))


class Probe:
    def __init__(self, output, previous=None, if_match_mode="etag"):
        self.output = output
        self.previous = previous
        self.if_match_mode = if_match_mode
        self.report = {
            "started_at": datetime.now(timezone.utc).isoformat(),
            "scope": "Repository mechanics only; no clinical signing, reassessment, or handover implementation",
            "status": "running",
            "if_match_mode": if_match_mode,
            "qualification": "bare-diagnostic explicitly removes ETag quotes to investigate other behavior; it cannot establish REST conformance",
            "inputs": {}, "checks": [], "exchanges": [],
        }
        cases = CASES if previous is None else {
            "restart_persistence": ("Both committed revisions and current query survive restart", ["TST-007", "DOC-008"], "Prototype persistence check; not backup/restore or interrupted-write recovery")
        }
        self.report["checks"] = [
            {"id": key, "expected": value[0], "requirements": value[1], "reference": value[2], "status": "not_run"}
            for key, value in cases.items()
        ]

    def check(self, key, condition, observed, abort=True):
        item = next(x for x in self.report["checks"] if x["id"] == key)
        item.update(status="passed" if condition else "failed", observed=observed)
        if not condition and abort:
            raise AssertionError(f"{key}: {observed}")
        print("PASS" if condition else "FAIL", key, flush=True)

    def request(self, method, path, body=None, headers=None, authorized=True):
        hdr = {"Accept": "application/json"}
        if authorized:
            hdr["Authorization"] = AUTH
        if isinstance(body, (dict, list)):
            body = json_bytes(body)
            hdr["Content-Type"] = "application/json"
        hdr.update(headers or {})
        request = urllib.request.Request(BASE + path, data=body, headers=hdr, method=method)
        try:
            response = urllib.request.urlopen(request, timeout=20)
        except urllib.error.HTTPError as error:
            response = error
        with response:
            raw = response.read()
            status = response.status
            response_headers = dict(response.headers)
        try:
            content = json.loads(raw)
        except (ValueError, UnicodeDecodeError):
            content = raw.decode(errors="replace")
        self.report["exchanges"].append({
            "method": method, "path": path,
            "request_headers": {k: v for k, v in hdr.items() if k.lower() != "authorization"},
            "request_body": body.decode() if body else None,
            "status": status, "response_headers": response_headers, "response_body": content,
        })
        return status, response_headers, content

    def expect(self, method, path, expected, **kwargs):
        status, headers, content = self.request(method, path, **kwargs)
        if status != expected:
            raise AssertionError(f"{method} {path}: expected {expected}, got {status}: {str(content)[:400]}")
        return headers, content

    def verify_inputs(self):
        lock = json.loads((HERE / "upstream.lock.json").read_text())
        for item in lock["artifacts"] + lock["fixtures"]:
            data = (HERE / item["path"]).read_bytes()
            if len(data) != item["bytes"] or digest(data) != item["sha256"]:
                raise AssertionError("Input hash mismatch: " + item["path"])
        # Refuse to run against an unrelated service occupying this port.
        ids = subprocess.check_output([
            "docker", "compose", "-f", str(HERE / "compose.yaml"), "ps", "-q"
        ], text=True).split()
        if len(ids) != 2:
            raise AssertionError("Expected this prototype's two running containers")
        containers = json.loads(subprocess.check_output(["docker", "inspect", *ids]))
        by_service = {c["Config"]["Labels"]["com.docker.compose.service"]: c for c in containers}
        for service, spec in [("ehrbase", lock["ehrbase"]), ("db", lock["postgres"])]:
            if by_service[service]["Config"]["Image"] != spec["image"]:
                raise AssertionError("Unexpected image: " + service)
        port = by_service["ehrbase"]["NetworkSettings"]["Ports"]["8080/tcp"]
        if port != [{"HostIp": "127.0.0.1", "HostPort": "18080"}]:
            raise AssertionError("Unexpected prototype API binding")
        self.report["inputs"] = {
            "upstream_lock_sha256": digest((HERE / "upstream.lock.json").read_bytes()),
            "compose_sha256": digest((HERE / "compose.yaml").read_bytes()),
            "probe_sha256": digest(Path(__file__).read_bytes()),
            "reference_manifest_sha256": digest((HERE.parents[1] / "references/manifest.json").read_bytes()),
            "python": platform.python_version(), "host_architecture": platform.machine(),
            "containers": {name: {"image_reference": c["Config"]["Image"], "image_id": c["Image"],
                                    "started_at": c["State"]["StartedAt"]} for name, c in by_service.items()},
        }

    def wait_ready(self):
        for attempt in range(30):
            try:
                status, _, _ = self.request("GET", "/definition/template/adl1.4")
                if status == 200:
                    return
                if status in (401, 403):
                    raise AssertionError("Prototype credentials rejected")
            except (urllib.error.URLError, ConnectionError, TimeoutError):
                pass
            time.sleep(1)
        raise AssertionError("Prototype did not become ready")

    def query(self, ehr_id):
        _, result = self.expect("POST", "/query/aql", 200, body={
            "q": "SELECT c/uid/value FROM EHR e CONTAINS COMPOSITION c WHERE e/ehr_id/value = $ehr_id",
            "query_parameters": {"ehr_id": ehr_id},
        })
        return result.get("rows", [])

    def scenario(self):
        status, _, _ = self.request("GET", "/definition/template/adl1.4", authorized=False)
        self.check("authentication", status == 401, {"status": status})

        opt = (HERE / "upstream/ehrbase/laboratory.opt").read_bytes()
        path = "/definition/template/adl1.4/" + TEMPLATE
        status, _, stored = self.request("GET", path, headers={"Accept": "application/xml"})
        if status == 404:
            self.expect("POST", "/definition/template/adl1.4", 201, body=opt,
                        headers={"Content-Type": "application/xml", "Accept": "application/xml"})
            _, stored = self.expect("GET", path, 200, headers={"Accept": "application/xml"})
        elif status != 200:
            raise AssertionError(f"Template retrieval returned {status}")
        self.check("template", xml_structure(opt) == xml_structure(stored), {"template_id": TEMPLATE})

        ids = []
        for _ in range(2):
            _, ehr = self.expect("POST", "/ehr", 201, headers={"Prefer": "return=representation"})
            ids.append(ehr["ehr_id"]["value"])
        ehr_id, other_ehr = ids
        self.check("ehr_creation", len(set(ids)) == 2, {"ehr_ids": ids})
        endpoint = f"/ehr/{ehr_id}/composition"
        fixture = json.loads((HERE / "fixtures/laboratory-v1.json").read_text())
        invalid = copy.deepcopy(fixture)
        del invalid["composer"]
        status, _, error = self.request("POST", endpoint, body=invalid)
        # REST composition POST specifies 400 for content that cannot form a valid
        # COMPOSITION, and 422 for a representable object failing template semantics.
        self.check("required_field", status == 400 and "composer" in str(error) and self.query(ehr_id) == [],
                   {"status": status, "error": error})

        invalid = copy.deepcopy(fixture)
        elements = invalid["content"][0]["data"]["events"][0]["data"]["items"]
        extra = copy.deepcopy(elements[0])
        extra["archetype_node_id"] = "at9999"
        extra["name"]["value"] = "Unmodelled synthetic field"
        elements.append(extra)
        status, _, error = self.request("POST", endpoint, body=invalid)
        self.check("extra_node", status == 422 and "at9999" in str(error) and self.query(ehr_id) == [],
                   {"status": status, "error": error})

        _, first = self.expect("POST", endpoint, 201, body=fixture, headers={"Prefer": "return=representation"})
        v1 = first["uid"]["value"]
        object_id = v1.split("::")[0]
        headers, first = self.expect("GET", endpoint + "/" + v1, 200)
        etag = next(value for key, value in headers.items() if key.lower() == "etag")
        self.check("create_read", quantity(first) == quantity(fixture) and
                   first["context"]["start_time"]["value"] == fixture["context"]["start_time"]["value"],
                   {"version": v1, "etag": etag, "quantity": quantity(first)})
        status, _, _ = self.request("GET", f"/ehr/{other_ehr}/composition/{v1}")
        self.check("ehr_scope", status == 404, {"status": status})

        barrier = threading.Barrier(2, timeout=5)

        def update(magnitude, concurrent=False):
            body = copy.deepcopy(first)
            body.pop("uid", None)
            quantity(body)["magnitude"] = magnitude
            condition = etag if self.if_match_mode == "etag" else v1
            if concurrent:
                barrier.wait()
            return magnitude, self.request("PUT", endpoint + "/" + object_id, body=body,
                                           headers={"If-Match": condition, "Prefer": "return=representation"})

        with ThreadPoolExecutor(max_workers=2) as pool:
            outcomes = list(pool.map(lambda value: update(value, concurrent=True), [23.0, 24.0]))
        self.check("concurrent_update", sorted(result[0] for _, result in outcomes) == [200, 412],
                   {"outcomes": [{"magnitude": m, "status": r[0]} for m, r in outcomes]},
                   abort=sum(r[0] == 200 for _, r in outcomes) != 1)
        winner_value, (_, _, winner) = next((m, r) for m, r in outcomes if r[0] == 200)
        v2 = winner["uid"]["value"]
        _, original = self.expect("GET", endpoint + "/" + v1, 200)
        _, current = self.expect("GET", endpoint + "/" + object_id, 200)
        self.check("history", original == first and quantity(current)["magnitude"] == winner_value
                   and v2 == object_id + "::journal-prototype.local::2" and current["uid"]["value"] == v2,
                   {"original_version": v1, "current_version": v2, "current_quantity": quantity(current)})

        _, retry = update(99.0)
        _, after_retry = self.expect("GET", endpoint + "/" + object_id, 200)
        self.check("stale_retry", retry[0] == 412 and after_retry == current, {"status": retry[0], "current_version": v2})
        rows, other_rows = self.query(ehr_id), self.query(other_ehr)
        self.check("query", rows == [[v2]] and other_rows == [], {"rows": rows, "other_ehr_rows": other_rows})

        versioned = f"/ehr/{ehr_id}/versioned_composition/{object_id}"
        _, history = self.expect("GET", versioned + "/revision_history", 200)
        _, version = self.expect("GET", versioned + "/version/" + v2, 200)
        revisions = [item["version_id"]["value"] for item in history["items"]]
        contribution_id = version["contribution"]["id"]["value"]
        _, contribution = self.expect("GET", f"/ehr/{ehr_id}/contribution/{contribution_id}", 200)
        self.check("audit", set(revisions) == {v1, v2} and len(revisions) == 2
                   and bool(version["commit_audit"]["committer"])
                   and v2 in [item["id"]["value"] for item in contribution["versions"]],
                   {"revisions": revisions, "contribution_id": contribution_id, "committer": version["commit_audit"]["committer"]})
        self.report["retained_state"] = {
            "ehr_id": ehr_id, "other_ehr_id": other_ehr, "object_id": object_id,
            "versions": [{"uid": v1, "sha256": digest(json_bytes(original))},
                         {"uid": v2, "sha256": digest(json_bytes(current))}],
            "current_uid": v2,
        }

    def verify_previous(self):
        previous = json.loads(self.previous.read_text())
        proved = {c["id"] for c in previous["checks"] if c["status"] == "passed"}
        if "retained_state" not in previous or not {"history", "query", "audit"} <= proved:
            raise AssertionError("Restart check needs previously verified history, query, and audit state")
        for key in ["upstream_lock_sha256", "compose_sha256", "probe_sha256", "reference_manifest_sha256"]:
            if previous["inputs"][key] != self.report["inputs"][key]:
                raise AssertionError("Restart check inputs changed: " + key)
        for service in ("ehrbase", "db"):
            if previous["inputs"]["containers"][service]["started_at"] == self.report["inputs"]["containers"][service]["started_at"]:
                raise AssertionError("Container was not restarted: " + service)
        self.report["previous_report_sha256"] = digest(self.previous.read_bytes())
        self.report["previous_failed_checks"] = [c["id"] for c in previous["checks"] if c["status"] == "failed"]
        self.report["if_match_mode"] = previous["if_match_mode"]
        state = previous["retained_state"]
        matching = []
        for version in state["versions"]:
            _, body = self.expect("GET", f'/ehr/{state["ehr_id"]}/composition/{version["uid"]}', 200)
            matching.append(digest(json_bytes(body)) == version["sha256"])
        rows = self.query(state["ehr_id"])
        self.check("restart_persistence", all(matching) and rows == [[state["current_uid"]]],
                   {"version_hashes_match": matching, "current_rows": rows})

    def run(self):
        try:
            self.verify_inputs()
            self.wait_ready()
            self.scenario() if self.previous is None else self.verify_previous()
            self.report["status"] = "passed" if all(c["status"] == "passed" for c in self.report["checks"]) else "failed"
        except Exception as error:
            self.report["status"] = "failed"
            self.report["failure"] = f"{type(error).__name__}: {error}"
            print(self.report["failure"], file=sys.stderr)
        finally:
            self.report["finished_at"] = datetime.now(timezone.utc).isoformat()
            self.output.parent.mkdir(parents=True, exist_ok=True)
            self.output.write_text(json.dumps(self.report, indent=2) + "\n")
        return 0 if self.report["status"] == "passed" else 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--verify-after-restart", type=Path)
    parser.add_argument("--if-match-mode", choices=["etag", "bare-diagnostic"], default="etag")
    args = parser.parse_args()
    if args.output.exists():
        parser.error("Output already exists; use a fresh evidence filename")
    sys.exit(Probe(args.output, args.verify_after_restart, args.if_match_mode).run())
