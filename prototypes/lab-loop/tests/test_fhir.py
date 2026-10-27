"""Laboratory reports received as FHIR R4 document Bundles (HL7 Europe Laboratory Report shape)."""

import copy
import unittest

from lab_loop import ObligationStatus, RequestStatus, ResultStatus, SimulatedCrash
from lab_loop.fhir import PERSONNUMMER, FhirLabAdapter, MessageRejected

from .support import LAB, UNIT, clinic, obligation_for

LOINC = "http://loinc.org"
ANALYTES = {(LOINC, "2823-3"): "K", (LOINC, "2951-2"): "Na", (LOINC, "2160-0"): "creatinine"}
CUSTOMERS = {"KUND-4711": UNIT}


def observation(id, code, value=None, unit="mmol/L", *, version=1, status="final", flags=(), low=None, high=None,
                note=None, absent=None):
    obs = {"resourceType": "Observation", "id": id, "meta": {"versionId": str(version)}, "status": status,
           "code": {"coding": [{"system": LOINC, "code": code}], "text": code},
           "subject": {"reference": "Patient/p1"}}
    if value is not None:
        obs["valueQuantity"] = {"value": value, "unit": unit, "system": "http://unitsofmeasure.org", "code": unit}
    if flags:
        obs["interpretation"] = [{"coding": [{"system": "http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation",
                                              "code": flag}]} for flag in flags]
    if low is not None:
        obs["referenceRange"] = [{"low": {"value": low}, "high": {"value": high}}]
    if note:
        obs["note"] = [{"text": note}]
    if absent:
        obs["dataAbsentReason"] = {"text": absent}
    return obs


def report(bundle_id, pnr, observations, request_id=None, customer="KUND-4711"):
    entries = [
        {"resourceType": "Composition", "id": "c1", "status": "final", "type": {"text": "Laboratory report"}},
        {"resourceType": "Patient", "id": "p1", "identifier": [{"system": PERSONNUMMER, "value": pnr}]},
        {"resourceType": "Organization", "id": "lab", "name": LAB},
        {"resourceType": "Organization", "id": "customer", "identifier": [{"value": customer}]},
        {"resourceType": "DiagnosticReport", "id": "r1", "status": "final", "subject": {"reference": "Patient/p1"},
         "performer": [{"reference": "Organization/lab"}],
         "result": [{"reference": f"Observation/{o['id']}"} for o in observations]},
        *observations,
    ]
    if request_id:
        entries.append({"resourceType": "ServiceRequest", "id": "sr1", "status": "active", "intent": "order",
                        "identifier": [{"type": {"coding": [{"code": "PLAC"}]}, "value": request_id}],
                        "requester": {"reference": "Organization/customer"}})
        entries[4]["basedOn"] = [{"reference": "ServiceRequest/sr1"}]
    return {"resourceType": "Bundle", "type": "document", "identifier": {"value": bundle_id},
            "entry": [{"fullUrl": f"urn:uuid:{bundle_id}-{i}", "resource": r} for i, r in enumerate(entries)]}


class FhirReceive(unittest.TestCase):
    def setUp(self):
        self.loop = clinic()
        self.adapter = FhirLabAdapter(self.loop, ANALYTES, CUSTOMERS, default_unit=UNIT)
        self.request = self.loop.order("bengt", "holm", ("K", "Na"), LAB)

    def bundle(self, bundle_id, observations, **kwargs):
        return report(bundle_id, "TEST-BENGT", observations, request_id=kwargs.pop("request_id", self.request.id),
                      **kwargs)

    def test_report_becomes_results_with_content_flags_and_range(self):
        outcome = self.adapter.receive(self.bundle("b1", [
            observation("k", "2823-3", 6.4, flags=["HH"], low=3.5, high=4.4, note="verified by repeat analysis"),
            observation("na", "2951-2", 139, low=137, high=145)]))
        self.assertEqual((len(outcome.results), outcome.held, outcome.duplicates), (2, [], 0))
        k = self.loop.db.results[outcome.results[0]]
        self.assertEqual((k.analyte, k.current.critical, k.current.abnormal), ("K", True, True))
        stored = self.loop.content(k.id)
        self.assertEqual((stored.value, stored.unit, stored.reference_range, stored.comment),
                         (6.4, "mmol/L", "3.5–4.4", "verified by repeat analysis"))
        self.assertTrue(obligation_for(self.loop, k.id).critical)
        self.assertIs(self.loop.db.requests[self.request.id].status, RequestStatus.COMPLETED)

    def test_resent_bundle_is_acknowledged_as_duplicates(self):
        bundle = self.bundle("b1", [observation("k", "2823-3", 4.2)])
        self.adapter.receive(bundle)
        outcome = self.adapter.receive(copy.deepcopy(bundle))
        self.assertEqual((outcome.results, outcome.duplicates), ([], 1))
        self.assertEqual(len(self.loop.obligations()), 1)

    def test_corrected_observation_is_a_new_version(self):
        self.adapter.receive(self.bundle("b1", [observation("k", "2823-3", 4.2)]))
        outcome = self.adapter.receive(self.bundle("b2", [observation("k", "2823-3", 5.9, version=2, status="corrected",
                                                                      flags=["H"])]))
        result_id = outcome.results[0]
        self.assertEqual(self.loop.staff_view(result_id)["value"], 5.9)
        self.assertIs(self.loop.staff_view(result_id)["status"], ResultStatus.CORRECTED)

    def test_cancelled_observation_is_withheld_with_reason(self):
        outcome = self.adapter.receive(self.bundle("b1", [
            observation("k", "2823-3", status="cancelled", absent="haemolysed sample, new sample requested")]))
        view = self.loop.staff_view(outcome.results[0])
        self.assertEqual((view["status"], view["comment"]),
                         (ResultStatus.WITHHELD, "haemolysed sample, new sample requested"))
        self.assertEqual([t.kind for t in self.loop.db.tasks.values()], ["recollect"])

    def test_unknown_analysis_code_is_held_not_dropped(self):
        unknown = observation("x", "99999-9", 1.0)
        outcome = self.adapter.receive(self.bundle("b1", [observation("k", "2823-3", 4.2), unknown]))
        self.assertEqual((len(outcome.results), len(outcome.held)), (1, 1))
        item = self.loop.db.intake[outcome.held[0]]
        self.assertEqual((item.owner_id, item.reason), ("sara", f"unknown analysis code {LOINC}|99999-9"))

    def test_entered_in_error_needs_manual_handling(self):
        outcome = self.adapter.receive(self.bundle("b1", [observation("k", "2823-3", 4.2, status="entered-in-error")]))
        self.assertIn("needs manual handling", self.loop.db.intake[outcome.held[0]].reason)

    def test_unknown_patient_and_missing_request_are_held(self):
        unknown = report("b1", "TEST-NOBODY", [observation("k", "2823-3", 4.2)], request_id=self.request.id)
        unsolicited = report("b2", "TEST-BENGT", [observation("k", "2823-3", 4.2)], customer="KUND-9999")
        reasons = [self.loop.db.intake[self.adapter.receive(b).held[0]].reason for b in (unknown, unsolicited)]
        self.assertEqual(reasons, ["unknown patient", "no matching request"])

    def test_structural_errors_reject_the_whole_bundle(self):
        good = self.bundle("b1", [observation("k", "2823-3", 4.2)])
        no_pnr = copy.deepcopy(good)
        no_pnr["entry"][1]["resource"]["identifier"] = []
        dangling = copy.deepcopy(good)
        dangling["entry"][4]["resource"]["result"].append({"reference": "Observation/missing"})
        for bad, issue in [({"resourceType": "Observation"}, "not a document Bundle"),
                           (no_pnr, "no personnummer"), (dangling, "Observation/missing")]:
            with self.assertRaises(MessageRejected) as raised:
                self.adapter.receive(bad)
            self.assertIn(issue, str(raised.exception))
        self.assertEqual((self.loop.db.results, self.loop.db.intake), ({}, {}))

    def test_crash_partway_through_bundle_then_resend_completes_once(self):
        bundle = self.bundle("b1", [observation("k", "2823-3", 4.2), observation("na", "2951-2", 139)])
        original = self.loop._store
        calls = []

        def crash_on_second(request, msg):
            calls.append(msg.analyte)
            if len(calls) == 2:
                raise SimulatedCrash("during second observation")
            return original(request, msg)

        self.loop._store = crash_on_second
        with self.assertRaises(SimulatedCrash):
            self.adapter.receive(bundle)
        self.loop._store = original
        outcome = self.adapter.receive(bundle)
        self.assertEqual((len(outcome.results), outcome.duplicates), (1, 1))
        self.assertEqual(len(self.loop.obligations()), 2)
        self.assertTrue(all(o.status is ObligationStatus.OPEN for o in self.loop.obligations()))


if __name__ == "__main__":
    unittest.main()
