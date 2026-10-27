"""R15: reconciliation between the record store and workflow state."""

import unittest
from datetime import datetime

from lab_loop import ObligationStatus, Refused, ResultStatus, SimulatedCrash
from lab_loop.records import ResultContent

from .support import LAB, UNIT, clinic, message, obligation_for


def crash_after_record_write(loop, msg):
    loop.fault = "after_record_written"
    try:
        loop.receive(msg)
    except SimulatedCrash:
        pass


class LostMessageAdopted(unittest.TestCase):
    def setUp(self):
        self.loop = loop = clinic()
        self.request = loop.order("anna", "holm", ("K",), LAB)
        self.msg = message(loop, self.request.id, "K", 4.1)
        crash_after_record_write(loop, self.msg)
        self.ehr_id = loop.db.ehrs["anna"][0]

    def test_recent_entry_is_left_for_the_retry(self):
        self.loop.clock.advance(minutes=30)
        report = self.loop.reconcile()
        self.assertEqual((report.adopted, report.unmatched), ([], []))
        self.assertEqual(self.loop.db.results, {})

    def test_entry_without_retry_is_adopted_with_an_owner(self):
        loop = self.loop
        loop.clock.advance(hours=2)
        report = loop.reconcile()
        [result_id] = report.adopted
        ob = obligation_for(loop, result_id)
        self.assertEqual((ob.owner_id, ob.status), ("holm", ObligationStatus.OPEN))
        self.assertIn("recovered from record store", ob.history[-1][2])
        self.assertEqual([n.ref for n in loop.notifications_for("sara", "reconciliation")], [result_id])
        self.assertEqual(len(loop.records.compositions(self.ehr_id)), 1)
        self.assertEqual(loop.content(result_id).value, 4.1)
        self.assertEqual(loop.reconcile().adopted, [])

    def test_adopted_result_is_treated_as_abnormal(self):
        loop = self.loop
        loop.clock.advance(hours=2)
        [result_id] = loop.reconcile().adopted
        ob = obligation_for(loop, result_id)
        with self.assertRaises(Refused):
            loop.review(ob.id, "holm", "no_action", inform="letter")

    def test_late_resend_restores_flags_without_duplicates(self):
        loop = self.loop
        loop.clock.advance(hours=2)
        [result_id] = loop.reconcile().adopted
        resent = message(loop, self.request.id, "K", 4.1, abnormal=False, critical=True)
        loop.receive(resent)
        version = loop.db.results[result_id].current
        self.assertEqual((version.abnormal, version.critical, version.reconciled), (False, True, False))
        [ob] = loop.obligations(result_id=result_id)
        self.assertTrue(ob.critical)
        self.assertIn(ob.id, [n.ref for n in loop.notifications_for("holm", "critical")])
        self.assertEqual(len(loop.records.compositions(self.ehr_id)), 1)


class LostCorrectionAdopted(unittest.TestCase):
    def test_correction_written_before_crash_is_adopted_as_correction(self):
        loop = clinic()
        request = loop.order("bengt", "holm", ("creatinine",), LAB)
        result = loop.receive(message(loop, request.id, "creatinine", 98, "µmol/L"))
        review = loop.review(obligation_for(loop, result.id).id, "holm", "no_action", inform="letter")
        crash_after_record_write(loop, message(loop, request.id, "creatinine", 210, "µmol/L", seq=2,
                                               status=ResultStatus.CORRECTED))
        loop.clock.advance(hours=2)
        self.assertEqual(loop.reconcile().adopted, [result.id])
        current = loop.db.results[result.id].current
        self.assertEqual((current.lab_sequence, loop.content(result.id).value), (2, 210))
        [new] = loop.obligations(result_id=result.id, status=ObligationStatus.OPEN)
        self.assertEqual(new.prior_review_id, review.id)


class Reported(unittest.TestCase):
    def test_change_by_another_writer_is_reported_not_adopted(self):
        loop = clinic()
        request = loop.order("anna", "holm", ("K",), LAB)
        result = loop.receive(message(loop, request.id, "K", 4.1))
        other = ResultContent("edited-elsewhere", request.id, LAB, "K", ResultStatus.CORRECTED, 4.7, "mmol/L",
                              None, None, loop.now)
        uid = loop.records.write(result.ehr_id, result.current.version_uid, other)
        loop.clock.advance(hours=2)
        report = loop.reconcile()
        self.assertEqual((report.changed_outside, report.adopted), ([uid], []))
        self.assertEqual(len(loop.db.results[result.id].versions), 1)
        self.assertIn(result.id, [n.ref for n in loop.notifications_for("sara", "reconciliation")])

    def test_missing_record_entry_is_reported(self):
        loop = clinic()
        request = loop.order("anna", "holm", ("K",), LAB)
        result = loop.receive(message(loop, request.id, "K", 4.1))
        loop.records.delete(result.ehr_id, result.current.version_uid)
        report = loop.reconcile()
        self.assertEqual(report.missing, [result.id])
        self.assertEqual([(e.action, e.ref) for e in loop.db.audit if e.actor == "reconciliation"],
                         [("record entry missing", result.id)])

    def test_entry_without_known_request_is_reported_then_filed_once(self):
        loop = clinic()
        loop.clock.set(datetime(2026, 11, 23, 9, 0))
        item = loop.receive(message(loop, None, "rare antibody", None, "titre", patient="frida",
                                    source="scanned", comment="positive 1:320"))
        loop.fault = "after_record_written"
        with self.assertRaises(SimulatedCrash):
            loop.file_intake(item.id, "frida", owner_id="holm", by="sara")
        loop.clock.advance(hours=2)
        report = loop.reconcile()
        self.assertEqual((len(report.unmatched), report.adopted), (1, []))
        result = loop.file_intake(item.id, "frida", owner_id="holm", by="sara")
        self.assertEqual(loop.records.compositions(result.ehr_id), [result.current.version_uid])
        self.assertEqual(loop.reconcile(), type(report)())


class Consistent(unittest.TestCase):
    def test_consistent_stores_produce_an_empty_report(self):
        loop = clinic()
        loop.add_patient("anna2", "TEST-ANNA2", "Anna Berg (duplicate)", UNIT)
        for patient in ("anna", "anna2"):
            request = loop.order(patient, "holm", ("K",), LAB)
            loop.receive(message(loop, request.id, "K", 4.0))
        loop.merge_patients("anna2", "anna", by="sara")
        loop.clock.advance(days=1)
        self.assertEqual(loop.reconcile(), type(loop.reconcile())())


if __name__ == "__main__":
    unittest.main()
