"""Failure cases from docs/workflow-laboratory-results.md not already covered by a scenario."""

import unittest

from lab_loop import ObligationStatus, Refused, ResultStatus, Role, SimulatedCrash

from .support import LAB, UNIT, clinic, message, obligation_for


class F2LateOlderVersion(unittest.TestCase):
    def test_older_version_after_correction_is_history_only(self):
        loop = clinic()
        request = loop.order("anna", "holm", ("Hb",), LAB)
        corrected = message(loop, request.id, "Hb", 121, "g/L", seq=2, status=ResultStatus.CORRECTED)
        result = loop.receive(corrected)
        loop.receive(message(loop, request.id, "Hb", 135, "g/L", seq=1))
        self.assertEqual(loop.staff_view(result.id)["value"], 121)
        self.assertEqual(len(result.versions), 2)
        obligations = loop.obligations(result_id=result.id)
        self.assertEqual([o.lab_sequence for o in obligations], [2])


class CorrectionBeforeReview(unittest.TestCase):
    def test_open_obligation_moves_to_new_version_and_becomes_critical(self):
        loop = clinic()
        request = loop.order("bengt", "holm", ("K",), LAB)
        result = loop.receive(message(loop, request.id, "K", 5.4, abnormal=True))
        loop.receive(message(loop, request.id, "K", 6.5, seq=2, status=ResultStatus.CORRECTED,
                             abnormal=True, critical=True))
        [ob] = loop.obligations(result_id=result.id)
        self.assertEqual((ob.lab_sequence, ob.critical), (2, True))
        self.assertIn(ob.id, [n.ref for n in loop.notifications_for("holm", "critical")])
        review = loop.review(ob.id, "holm", "emergency", inform="phone")
        self.assertEqual(review.lab_sequence, 2)


class F4CrashBetweenResultAndObligation(unittest.TestCase):
    def test_retry_after_crash_leaves_exactly_one_obligation(self):
        loop = clinic()
        request = loop.order("anna", "holm", ("K",), LAB)
        msg = message(loop, request.id, "K", 4.1)
        loop.fault = "after_result_stored"
        with self.assertRaises(SimulatedCrash):
            loop.receive(msg)
        self.assertEqual((loop.db.results, loop.obligations()), ({}, []))
        result = loop.receive(msg)
        self.assertEqual(len(result.versions), 1)
        self.assertEqual(len(loop.obligations()), 1)


class F5UnknownPatient(unittest.TestCase):
    def test_result_for_unknown_patient_goes_to_queue(self):
        loop = clinic()
        request = loop.order("anna", "holm", ("K",), LAB)
        item = loop.receive(message(loop, request.id, "K", 4.0, patient="nobody"))
        self.assertEqual((item.reason, item.owner_id), ("unknown patient", "sara"))
        self.assertEqual(loop.db.results, {})

    def test_result_naming_another_patients_request_goes_to_queue(self):
        loop = clinic()
        request = loop.order("anna", "holm", ("K",), LAB)
        item = loop.receive(message(loop, request.id, "K", 4.0, patient="bengt"))
        self.assertEqual(item.reason, "patient does not match request")


class R1AlwaysAnOwner(unittest.TestCase):
    def test_result_without_orderer_is_owned_by_unit_monitor(self):
        loop = clinic()
        request = loop.order("anna", None, ("K",), LAB)
        result = loop.receive(message(loop, request.id, "K", 4.0))
        self.assertEqual(obligation_for(loop, result.id).owner_id, "sara")

    def test_departed_without_successor_chain_falls_back_to_monitor(self):
        loop = clinic()
        request = loop.order("anna", "nyberg", ("K",), LAB)
        loop.depart("nyberg", by="sara", handover_to="falk")
        with loop._transaction():  # account closed outside the departure routine
            loop.db.staff["falk"].active = False
        result = loop.receive(message(loop, request.id, "K", 4.0))
        self.assertEqual(obligation_for(loop, result.id).owner_id, "sara")


class F9CancelledAfterCollection(unittest.TestCase):
    def test_results_still_arrive_and_need_review(self):
        loop = clinic()
        request = loop.order("anna", "holm", ("K",), LAB)
        loop.collect(request.id, "eva")
        loop.cancel(request.id, "holm")
        result = loop.receive(message(loop, request.id, "K", 4.3))
        self.assertIs(obligation_for(loop, result.id).status, ObligationStatus.OPEN)


class F11PatientMerge(unittest.TestCase):
    def test_results_and_obligations_follow_surviving_identity(self):
        loop = clinic()
        loop.add_patient("anna2", "TEST-ANNA2", "Anna Berg (duplicate)", UNIT)
        request = loop.order("anna2", "holm", ("K",), LAB)
        result = loop.receive(message(loop, request.id, "K", 4.0))
        loop.merge_patients("anna2", "anna", by="sara")
        ob = obligation_for(loop, result.id)
        self.assertEqual((result.patient_id, ob.patient_id), ("anna", "anna"))
        self.assertIn("moved from patient anna2 by merge", [h[2] for h in ob.history])
        loop.review(ob.id, "holm", "no_action", inform="letter")


class F12UnitChange(unittest.TestCase):
    def test_trend_keeps_each_unit_and_range(self):
        loop = clinic()
        first = loop.order("anna", "holm", ("HbA1c",), LAB)
        loop.receive(message(loop, first.id, "HbA1c", 7.5, "%", reference_range="4.0–6.0"))
        loop.clock.advance(days=90)
        second = loop.order("anna", "holm", ("HbA1c",), LAB)
        loop.receive(message(loop, second.id, "HbA1c", 58, "mmol/mol", reference_range="31–46"))
        self.assertEqual([(r["value"], r["unit"], r["reference_range"]) for r in loop.trend("anna", "HbA1c")],
                         [(7.5, "%", "4.0–6.0"), (58, "mmol/mol", "31–46")])


class F14NoAccess(unittest.TestCase):
    def test_review_refused_logged_and_obligation_stays_open(self):
        loop = clinic()
        request = loop.order("anna", "holm", ("K",), LAB)
        ob = obligation_for(loop, loop.receive(message(loop, request.id, "K", 4.0)).id)
        with self.assertRaises(Refused):
            loop.review(ob.id, "olsson", "no_action", inform="letter")
        self.assertIs(ob.status, ObligationStatus.OPEN)
        self.assertEqual([(e.actor, e.action) for e in loop.db.audit if e.ref == ob.id],
                         [("olsson", "review refused: no access")])

    def test_non_physician_cannot_review(self):
        loop = clinic()
        request = loop.order("anna", "holm", ("K",), LAB)
        ob = obligation_for(loop, loop.receive(message(loop, request.id, "K", 4.0)).id)
        with self.assertRaises(Refused):
            loop.review(ob.id, "eva", "no_action", inform="letter")


class R14ReviewAuthority(unittest.TestCase):
    def _result(self, loop, patient, orderer):
        request = loop.order(patient, orderer, ("INR",), LAB)
        return obligation_for(loop, loop.receive(message(loop, request.id, "INR", 2.4, "")).id)

    def test_nurse_cannot_review_by_default(self):
        loop = clinic()
        ob = self._result(loop, "anna", "eva")
        with self.assertRaises(Refused):
            loop.review(ob.id, "eva", "no_action", inform="phone")

    def test_deployment_can_let_nurses_review_their_own_orders_only(self):
        loop = clinic(review_own_orders_roles=frozenset({Role.NURSE}))
        own = self._result(loop, "anna", "eva")
        loop.review(own.id, "eva", "no_action", inform="phone")
        loop.add_staff("nils", "Nils (nurse)", Role.NURSE, UNIT)
        other = self._result(loop, "bengt", "nils")
        with self.assertRaises(Refused):
            loop.review(other.id, "eva", "no_action", inform="phone")

    def test_ordering_unit_reviews_patient_listed_elsewhere(self):
        loop = clinic()
        loop.add_patient("gustav", "TEST-GUSTAV", "Gustav (visiting)", "other")
        ob = self._result(loop, "gustav", "holm")
        with self.assertRaises(Refused):
            loop.review(ob.id, "olsson", "no_action", inform="phone")
        loop.review(ob.id, "sand", "no_action", inform="phone")


class RefusalsChangeNothing(unittest.TestCase):
    def test_refused_review_leaves_no_partial_state(self):
        loop = clinic()
        request = loop.order("anna", "holm", ("eGFR",), LAB)
        ob = obligation_for(loop, loop.receive(message(loop, request.id, "eGFR", 40, abnormal=True)).id)
        before = (len(loop.db.reviews), len(loop.db.requests))
        with self.assertRaises(Refused):
            loop.review(ob.id, "holm", "no_action", inform="letter", follow_up={"tests": ["eGFR"]})
        self.assertEqual((len(loop.db.reviews), len(loop.db.requests)), before)


if __name__ == "__main__":
    unittest.main()
