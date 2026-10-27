"""Behavior at the boundary between workflow state and the clinical record store."""

import unittest

from lab_loop import ResultStatus, SimulatedCrash
from lab_loop.records import RecordConflict, ResultContent

from .support import LAB, UNIT, clinic, message, obligation_for


class ContentLivesInRecordStore(unittest.TestCase):
    def test_workflow_keeps_reference_not_value(self):
        loop = clinic()
        request = loop.order("anna", "holm", ("K",), LAB)
        result = loop.receive(message(loop, request.id, "K", 4.2, reference_range="3.5–4.4", comment="fasting"))
        version = result.current
        self.assertFalse(hasattr(version, "value"))
        stored = loop.records.read(result.ehr_id, version.version_uid)
        self.assertEqual((stored.analyte, stored.value, stored.unit, stored.reference_range, stored.comment,
                          stored.status, stored.request_id),
                         ("K", 4.2, "mmol/L", "3.5–4.4", "fasting", ResultStatus.FINAL, request.id))

    def test_withheld_result_is_recorded_without_value(self):
        loop = clinic()
        request = loop.order("anna", "holm", ("K",), LAB)
        result = loop.receive(message(loop, request.id, "K", None, status=ResultStatus.WITHHELD,
                                      comment="haemolysed sample"))
        stored = loop.content(result.id)
        self.assertEqual((stored.value, stored.status, stored.comment),
                         (None, ResultStatus.WITHHELD, "haemolysed sample"))


class CorrectionsAreRecordVersions(unittest.TestCase):
    def setUp(self):
        self.loop = loop = clinic()
        self.request = loop.order("bengt", "holm", ("creatinine",), LAB)
        self.result = loop.receive(message(loop, self.request.id, "creatinine", 98, "µmol/L"))
        loop.receive(message(loop, self.request.id, "creatinine", 210, "µmol/L", seq=2,
                             status=ResultStatus.CORRECTED, abnormal=True))

    def test_correction_is_new_version_of_same_composition(self):
        first, second = self.result.versions
        self.assertEqual(first.version_uid.split("::")[0], second.version_uid.split("::")[0])
        self.assertTrue(second.version_uid.endswith("::2"))
        self.assertEqual(self.loop.records.compositions(self.result.ehr_id), [second.version_uid])
        self.assertEqual(self.loop.content(self.result.id, 1).value, 98)
        self.assertEqual(self.loop.content(self.result.id).value, 210)

    def test_late_older_version_is_not_written(self):
        loop = self.loop
        late = message(loop, self.request.id, "creatinine", 98, "µmol/L", seq=1, message_id="late-1")
        loop.db.results[self.result.id].versions.pop(0)  # as if version 1 had never arrived
        loop.receive(late)
        self.assertIsNone(self.result.versions[-1].version_uid)
        self.assertIn("late-1", loop.db.late_messages)
        [current] = loop.records.compositions(self.result.ehr_id)
        self.assertEqual(loop.records.read(self.result.ehr_id, current).value, 210)

    def test_concurrent_record_change_fails_the_operation_cleanly(self):
        loop = self.loop
        head = self.result.current.version_uid
        other = ResultContent("other-writer", self.request.id, LAB, "creatinine", ResultStatus.CORRECTED, 199,
                              "µmol/L", None, "edited elsewhere", loop.now)
        loop.records.write(self.result.ehr_id, head, other)
        obligations = len(loop.obligations())
        with self.assertRaises(RecordConflict):
            loop.receive(message(loop, self.request.id, "creatinine", 205, "µmol/L", seq=3,
                                 status=ResultStatus.CORRECTED))
        result = loop.db.results[self.result.id]  # the rollback replaced workflow state
        self.assertEqual((len(result.versions), len(loop.obligations())), (2, obligations))


class CrashBetweenStores(unittest.TestCase):
    def test_crash_after_record_write_then_retry_writes_once(self):
        loop = clinic()
        request = loop.order("anna", "holm", ("K",), LAB)
        msg = message(loop, request.id, "K", 4.1)
        loop.fault = "after_record_written"
        with self.assertRaises(SimulatedCrash):
            loop.receive(msg)
        ehr_id = loop.db.ehrs["anna"][0]
        self.assertEqual((loop.db.results, loop.obligations()), ({}, []))
        [written] = loop.records.compositions(ehr_id)
        result = loop.receive(msg)
        self.assertEqual(loop.records.compositions(ehr_id), [written])
        self.assertEqual(result.current.version_uid, written)
        self.assertEqual(len(loop.obligations()), 1)

    def test_crash_during_correction_then_retry_writes_one_version(self):
        loop = clinic()
        request = loop.order("bengt", "holm", ("creatinine",), LAB)
        result = loop.receive(message(loop, request.id, "creatinine", 98, "µmol/L"))
        correction = message(loop, request.id, "creatinine", 210, "µmol/L", seq=2, status=ResultStatus.CORRECTED)
        loop.fault = "after_record_written"
        with self.assertRaises(SimulatedCrash):
            loop.receive(correction)
        loop.receive(correction)
        [current] = loop.records.compositions(result.ehr_id)
        self.assertTrue(current.endswith("::2"))
        self.assertEqual(loop.db.results[result.id].current.version_uid, current)



class WithdrawnResults(unittest.TestCase):
    def test_withdrawn_result_leaves_current_record_but_keeps_history(self):
        loop = clinic()
        request = loop.order("carl", "holm", ("ALT",), LAB)
        result = loop.receive(message(loop, request.id, "ALT", 3.1, "µkat/L"))
        uid = result.current.version_uid
        loop.fault = "after_record_written"
        withdrawal = message(loop, request.id, "ALT", None, "", seq=2, status=ResultStatus.ENTERED_IN_ERROR,
                             comment="sample identity uncertain")
        with self.assertRaises(SimulatedCrash):
            loop.receive(withdrawal)
        loop.receive(withdrawal)
        self.assertEqual(loop.records.compositions(result.ehr_id), [])
        self.assertEqual(loop.records.read(result.ehr_id, uid).value, 3.1)
        loop.clock.advance(days=1)
        self.assertEqual(loop.reconcile().missing, [])


class MergeAcrossRecords(unittest.TestCase):
    def test_duplicate_records_stay_readable_after_merge(self):
        loop = clinic()
        loop.add_patient("anna2", "TEST-ANNA2", "Anna Berg (duplicate)", UNIT)
        request = loop.order("anna2", "holm", ("K",), LAB)
        old = loop.receive(message(loop, request.id, "K", 4.0))
        loop.merge_patients("anna2", "anna", by="sara")
        self.assertEqual(loop.db.ehrs["anna"][1], old.ehr_id)
        self.assertEqual(loop.content(old.id).value, 4.0)
        new_request = loop.order("anna", "holm", ("K",), LAB)
        new = loop.receive(message(loop, new_request.id, "K", 4.3))
        self.assertEqual(new.ehr_id, loop.db.ehrs["anna"][0])
        self.assertEqual([row["value"] for row in loop.trend("anna", "K")], [4.0, 4.3])


if __name__ == "__main__":
    unittest.main()
