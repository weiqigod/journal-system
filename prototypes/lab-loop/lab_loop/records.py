"""Clinical record stores for laboratory result content.

The workflow keeps references to result versions and the fields its rules
need; the result itself lives in a record store. `MemoryRecordStore` mirrors
the behavior the workflow relies on. `EhrbaseRecordStore` writes openEHR
compositions to the local patched EHRbase from prototypes/record-model, using
its pinned laboratory test template.

Every write carries a deterministic key in the composition's laboratory test
identifier. Before writing, the workflow looks the key up among current
versions, so a write repeated after a crash returns the existing version
instead of creating a duplicate.
"""

from __future__ import annotations

import base64
import copy
import json
import urllib.error
import urllib.request
import uuid
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from .model import ResultStatus

RECORD_MODEL = Path(__file__).resolve().parents[2] / "record-model"
TEMPLATE_ID = "65d9e89a-81d8-4344-afbe-88508d42dcfc"
LAB_OBSERVATION = "openEHR-EHR-OBSERVATION.laboratory_test.v0"

# Template codes for the panel's Result status (at0005); no code exists for a withheld result.
STATUS_CODES = {
    ResultStatus.PRELIMINARY: ("at0008", "Interim"),
    ResultStatus.FINAL: ("at0009", "Final"),
    ResultStatus.CORRECTED: ("at0010", "Amended"),
    ResultStatus.WITHHELD: ("at0011", "Cancelled/Aborted"),
}


class RecordConflict(Exception):
    """The composition changed since the expected version."""


@dataclass(frozen=True)
class ResultContent:
    key: str
    request_id: str
    laboratory: str
    analyte: str
    status: ResultStatus
    value: float | None
    unit: str | None
    reference_range: str | None
    comment: str | None
    recorded_at: datetime


def object_id(version_uid: str) -> str:
    return version_uid.split("::")[0]


class MemoryRecordStore:
    def __init__(self):
        self._versions: dict[str, list[tuple[str, ResultContent]]] = {}
        self._ehrs: dict[str, list[str]] = {}

    def create_ehr(self) -> str:
        ehr_id = str(uuid.uuid4())
        self._ehrs[ehr_id] = []
        return ehr_id

    def write(self, ehr_id: str, expected: str | None, content: ResultContent) -> str:
        if expected is None:
            oid = str(uuid.uuid4())
            self._ehrs[ehr_id].append(oid)
            self._versions[oid] = []
        else:
            oid = object_id(expected)
            if self._versions[oid][-1][0] != expected:
                raise RecordConflict(self._versions[oid][-1][0])
        uid = f"{oid}::memory::{len(self._versions[oid]) + 1}"
        self._versions[oid].append((uid, content))
        return uid

    def find(self, ehr_id: str, key: str) -> str | None:
        return next((versions[-1][0] for oid in self._ehrs[ehr_id]
                     for versions in [self._versions[oid]] if versions[-1][1].key == key), None)

    def read(self, ehr_id: str, version_uid: str) -> ResultContent:
        return next(content for uid, content in self._versions[object_id(version_uid)] if uid == version_uid)

    def compositions(self, ehr_id: str) -> list[str]:
        return [self._versions[oid][-1][0] for oid in self._ehrs[ehr_id]]


class EhrbaseRecordStore:
    def __init__(self, base: str = "http://127.0.0.1:18080/ehrbase/rest/openehr/v1",
                 user: str = "prototype", password: str = "prototype-only"):
        self.base = base
        self.auth = "Basic " + base64.b64encode(f"{user}:{password}".encode()).decode()
        self.fixture = json.loads((RECORD_MODEL / "fixtures/laboratory-v1.json").read_text())
        status, _, _ = self._request("GET", f"/definition/template/adl1.4/{TEMPLATE_ID}")
        if status == 404:
            opt = (RECORD_MODEL / "upstream/ehrbase/laboratory.opt").read_bytes()
            self._expect("POST", "/definition/template/adl1.4", 201, body=opt,
                         headers={"Content-Type": "application/xml"})

    def create_ehr(self) -> str:
        _, ehr = self._expect("POST", "/ehr", 201, headers={"Prefer": "return=representation"})
        return ehr["ehr_id"]["value"]

    def write(self, ehr_id: str, expected: str | None, content: ResultContent) -> str:
        body = self._composition(content)
        headers = {"Prefer": "return=representation"}
        if expected is None:
            _, created = self._expect("POST", f"/ehr/{ehr_id}/composition", 201, body=body, headers=headers)
            return created["uid"]["value"]
        status, response_headers, updated = self._request(
            "PUT", f"/ehr/{ehr_id}/composition/{object_id(expected)}", body=body,
            headers={**headers, "If-Match": f'"{expected}"'})
        if status == 412:
            raise RecordConflict(response_headers.get("ETag"))
        if status != 200:
            raise RuntimeError(f"update failed: {status} {str(updated)[:300]}")
        return updated["uid"]["value"]

    def find(self, ehr_id: str, key: str) -> str | None:
        rows = self._query(
            f"SELECT c/uid/value FROM EHR e CONTAINS COMPOSITION c CONTAINS OBSERVATION o[{LAB_OBSERVATION}] "
            "WHERE e/ehr_id/value = $ehr AND o/protocol[at0004]/items[at0068]/value/id = $key",
            ehr=ehr_id, key=key)
        return rows[0][0] if rows else None

    def read(self, ehr_id: str, version_uid: str) -> ResultContent:
        _, composition = self._expect("GET", f"/ehr/{ehr_id}/composition/{version_uid}", 200)
        return self._content(composition)

    def compositions(self, ehr_id: str) -> list[str]:
        rows = self._query("SELECT c/uid/value FROM EHR e CONTAINS COMPOSITION c WHERE e/ehr_id/value = $ehr",
                           ehr=ehr_id)
        return [row[0] for row in rows]

    # Mapping between ResultContent and the template

    def _composition(self, content: ResultContent) -> dict:
        composition = copy.deepcopy(self.fixture)
        time = {"_type": "DV_DATE_TIME", "value": content.recorded_at.isoformat()}
        composition["composer"] = {"_type": "PARTY_IDENTIFIED", "name": content.laboratory}
        composition["context"]["start_time"] = time
        observation = composition["content"][0]
        observation["data"]["origin"] = time
        event = observation["data"]["events"][0]
        event["time"] = time
        event["state"]["items"] = []
        test_name, panel = event["data"]["items"]
        test_name["value"]["value"] = content.analyte
        code, text = STATUS_CODES[content.status]
        items = [_element("Result status", "at0005", {
            "_type": "DV_CODED_TEXT", "value": text,
            "defining_code": {"_type": "CODE_PHRASE", "terminology_id": {"_type": "TERMINOLOGY_ID", "value": "local"},
                              "code_string": code}})]
        if content.value is not None:
            items.insert(0, _element("Result value", "at0001",
                                     {"_type": "DV_QUANTITY", "units": content.unit, "magnitude": float(content.value)}))
        if content.comment:
            items.append(_element("Comment", "at0003", {"_type": "DV_TEXT", "value": content.comment}))
        if content.reference_range:
            items.append(_element("Reference range guidance", "at0004",
                                  {"_type": "DV_TEXT", "value": content.reference_range}))
        panel["items"][0]["items"] = items
        identifier, request, point_of_care = observation["protocol"]["items"]
        identifier["value"]["id"] = content.key
        requested_name, requester_id, _ = request["items"]
        requested_name["value"]["value"] = content.analyte
        requester_id["value"]["id"] = content.request_id
        request["items"] = [requested_name, requester_id]
        point_of_care["value"]["value"] = False
        return composition

    def _content(self, composition: dict) -> ResultContent:
        observation = composition["content"][0]
        test_name, panel = observation["data"]["events"][0]["data"]["items"]
        fields = {item["archetype_node_id"]: item["value"] for item in panel["items"][0]["items"]}
        status_code = fields["at0005"]["defining_code"]["code_string"]
        identifier, request, _ = observation["protocol"]["items"]
        quantity = fields.get("at0001")
        return ResultContent(
            key=identifier["value"]["id"], request_id=request["items"][1]["value"]["id"],
            laboratory=composition["composer"]["name"], analyte=test_name["value"]["value"],
            status=next(s for s, (code, _) in STATUS_CODES.items() if code == status_code),
            value=quantity["magnitude"] if quantity else None, unit=quantity["units"] if quantity else None,
            reference_range=fields.get("at0004", {}).get("value"), comment=fields.get("at0003", {}).get("value"),
            recorded_at=datetime.fromisoformat(composition["context"]["start_time"]["value"]))

    # HTTP

    def _query(self, aql: str, **parameters) -> list:
        _, result = self._expect("POST", "/query/aql", 200, body={"q": aql, "query_parameters": parameters})
        return result.get("rows", [])

    def _request(self, method: str, path: str, body=None, headers: dict | None = None):
        all_headers = {"Accept": "application/json", "Authorization": self.auth}
        if isinstance(body, (dict, list)):
            body = json.dumps(body).encode()
            all_headers["Content-Type"] = "application/json"
        all_headers.update(headers or {})
        request = urllib.request.Request(self.base + path, data=body, headers=all_headers, method=method)
        try:
            response = urllib.request.urlopen(request, timeout=20)
        except urllib.error.HTTPError as error:
            response = error
        with response:
            raw = response.read()
            try:
                content = json.loads(raw)
            except ValueError:
                content = raw.decode(errors="replace")
            return response.status, dict(response.headers), content

    def _expect(self, method: str, path: str, expected: int, **kwargs):
        status, headers, content = self._request(method, path, **kwargs)
        if status != expected:
            raise RuntimeError(f"{method} {path}: expected {expected}, got {status}: {str(content)[:300]}")
        return headers, content


def _element(name: str, node_id: str, value: dict) -> dict:
    return {"_type": "ELEMENT", "name": {"_type": "DV_TEXT", "value": name}, "archetype_node_id": node_id,
            "value": value}

