"""Laboratory reports as FHIR R4 document Bundles, following HL7 Europe Laboratory Report 2.0.0.

A report arrives as one Bundle holding a DiagnosticReport, its Observations,
the Patient, the ServiceRequest it answers, and the performing Organization.
Each Observation becomes one LabMessage. Only the elements the workflow uses
are read; the Bundle is not validated against the guide's profiles.

A structurally unusable Bundle is rejected whole, so the laboratory must
correct and resend it. A usable Bundle whose content cannot be matched, such
as an unknown analysis code, is accepted and the affected results go to the
unit's intake queue.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .model import IntakeItem, LabMessage, ResultStatus

PERSONNUMMER = "urn:oid:1.2.752.129.2.1.3.1"
INTERPRETATION = "http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation"
CRITICAL = {"HH", "LL", "AA"}
ABNORMAL = CRITICAL | {"H", "L", "A"}
STATUS = {
    "preliminary": ResultStatus.PRELIMINARY,
    "final": ResultStatus.FINAL,
    "amended": ResultStatus.CORRECTED,
    "corrected": ResultStatus.CORRECTED,
    "cancelled": ResultStatus.WITHHELD,
}


class MessageRejected(Exception):
    """The Bundle cannot be processed at all; nothing was stored."""

    def __init__(self, issues: list[str]):
        super().__init__("; ".join(issues))
        self.issues = issues


@dataclass
class ReceiveOutcome:
    """The acknowledgement for one Bundle."""

    results: list[str] = field(default_factory=list)
    held: list[str] = field(default_factory=list)
    duplicates: int = 0


class FhirLabAdapter:
    def __init__(self, loop, analytes: dict[tuple[str, str], str], customer_units: dict[str, str],
                 default_unit: str):
        """`analytes` maps (code system, code) to the test names used in requests.
        `customer_units` maps the laboratory's customer code for an ordering unit to that unit."""
        self.loop = loop
        self.analytes = analytes
        self.customer_units = customer_units
        self.default_unit = default_unit

    def receive(self, bundle: dict) -> ReceiveOutcome:
        outcome = ReceiveOutcome()
        for msg in self.parse(bundle):
            stored = self.loop.receive(msg)
            if stored is None:
                outcome.duplicates += 1
            elif isinstance(stored, IntakeItem):
                outcome.held.append(stored.id)
            else:
                outcome.results.append(stored.id)
        return outcome

    def parse(self, bundle: dict) -> list[LabMessage]:
        issues = []
        if bundle.get("resourceType") != "Bundle" or bundle.get("type") != "document":
            raise MessageRejected(["not a document Bundle"])
        bundle_id = (bundle.get("identifier") or {}).get("value")
        if not bundle_id:
            issues.append("Bundle.identifier missing")
        resources = {}
        for entry in bundle.get("entry", []):
            resource = entry.get("resource", {})
            for key in (entry.get("fullUrl"), f"{resource.get('resourceType')}/{resource.get('id')}"):
                if key:
                    resources[key] = resource
        reports = [r for r in resources.values() if r.get("resourceType") == "DiagnosticReport"]
        reports = list({id(r): r for r in reports}.values())
        if len(reports) != 1:
            issues.append(f"expected one DiagnosticReport, found {len(reports)}")
        if issues:
            raise MessageRejected(issues)
        report = reports[0]
        patient = resources.get(report.get("subject", {}).get("reference", ""))
        pnr = _identifier(patient, PERSONNUMMER) if patient else None
        if not pnr:
            raise MessageRejected(["DiagnosticReport.subject has no personnummer"])
        laboratory = (resources.get(_first_reference(report.get("performer"))) or {}).get("name")
        if not laboratory:
            raise MessageRejected(["DiagnosticReport.performer has no named Organization"])
        service_request = resources.get(_first_reference(report.get("basedOn")))
        request_id = _placer_identifier(service_request)
        requester = resources.get((service_request or {}).get("requester", {}).get("reference", ""))
        unit_id = self.customer_units.get(_identifier(requester, None) or "", self.default_unit)

        messages = []
        for ref in report.get("result", []):
            observation = resources.get(ref.get("reference", ""))
            if observation is None:
                raise MessageRejected([f"result {ref.get('reference')} is not in the Bundle"])
            messages.append(self._message(bundle_id, observation, laboratory, unit_id, pnr, request_id))
        if not messages:
            raise MessageRejected(["DiagnosticReport has no results"])
        return messages

    def _message(self, bundle_id, observation, laboratory, unit_id, pnr, request_id) -> LabMessage:
        problems = []
        codings = observation.get("code", {}).get("coding", [])
        analyte = next((self.analytes[(c.get("system"), c.get("code"))] for c in codings
                        if (c.get("system"), c.get("code")) in self.analytes), None)
        if analyte is None:
            analyte = observation.get("code", {}).get("text") or "unknown analysis"
            problems.append("unknown analysis code " + ", ".join(f"{c.get('system')}|{c.get('code')}" for c in codings))
        status = STATUS.get(observation.get("status"))
        if status is None:
            status = ResultStatus.PRELIMINARY
            problems.append(f"laboratory status {observation.get('status')!r} needs manual handling")
        version = observation.get("meta", {}).get("versionId", "")
        if not str(version).isdigit():
            problems.append("Observation.meta.versionId missing")
        quantity = observation.get("valueQuantity")
        flags = {c.get("code") for i in observation.get("interpretation", []) for c in i.get("coding", [])
                 if c.get("system") == INTERPRETATION}
        comment = "; ".join(filter(None, [*(n.get("text") for n in observation.get("note", [])),
                                          observation.get("dataAbsentReason", {}).get("text")])) or None
        return LabMessage(
            message_id=f"{bundle_id}/{observation.get('id')}/{version}", laboratory=laboratory, unit_id=unit_id,
            patient_pnr=pnr, analyte=analyte, lab_sequence=int(version) if str(version).isdigit() else 0,
            status=status, value=quantity.get("value") if quantity else None,
            unit=(quantity or {}).get("code") or (quantity or {}).get("unit") or "",
            reference_range=_reference_range(observation), abnormal=bool(flags & ABNORMAL),
            critical=bool(flags & CRITICAL), comment=comment, request_id=request_id,
            problem="; ".join(problems) or None)


def _first_reference(references) -> str:
    return (references or [{}])[0].get("reference", "")


def _identifier(resource: dict | None, system: str | None) -> str | None:
    for identifier in (resource or {}).get("identifier", []):
        if system is None or identifier.get("system") == system:
            return identifier.get("value")
    return None


def _placer_identifier(service_request: dict | None) -> str | None:
    for identifier in (service_request or {}).get("identifier", []):
        codes = {c.get("code") for c in identifier.get("type", {}).get("coding", [])}
        if "PLAC" in codes:
            return identifier.get("value")
    return None


def _reference_range(observation: dict) -> str | None:
    ranges = observation.get("referenceRange", [])
    if not ranges:
        return None
    first = ranges[0]
    if first.get("text"):
        return first["text"]
    low, high = first.get("low", {}).get("value"), first.get("high", {}).get("value")
    return f"{low}–{high}" if low is not None and high is not None else None
