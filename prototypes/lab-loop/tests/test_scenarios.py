"""Scenarios S1–S10 from docs/scenarios-laboratory-results.md, one test per Expect block."""

import unittest
from datetime import datetime, timedelta

from lab_loop import ObligationStatus, Refused, RequestStatus, ResultStatus

from .support import LAB, UNIT, clinic, message, obligation_for

OPEN, REVIEWED, CLOSED = ObligationStatus.OPEN, ObligationStatus.REVIEWED, ObligationStatus.CLOSED


class S1AnnualDiabetesCheck(unittest.TestCase):
    def setUp(self):
        self.loop = loop = clinic()
        self.request = loop.order("anna", "holm", ("HbA1c", "eGFR", "K", "lipids"), LAB)
        loop.clock.advance(days=1)
        loop.collect(self.request.id, "eva")
        loop.clock.advance(days=2)
        values = [("HbA1c", 58, "mmol/mol", False), ("eGFR", 52, "mL/min/1.73m²", True),
                  ("K", 4.6, "mmol/L", False), ("lipids", 2.4, "mmol/L", False)]
        self.obs = {}
        for analyte, value, unit, abnormal in values:
            result = loop.receive(message(loop, self.request.id, analyte, value, unit, abnormal=abnormal))
            self.obs[analyte] = obligation_for(loop, result.id)

    def test_each_result_gets_one_obligation_owned_by_the_orderer(self):
        self.assertEqual(len(self.loop.obligations()), 4)
        self.assertTrue(all(o.owner_id == "holm" and o.status is OPEN for o in self.obs.values()))
        self.assertIs(self.loop.db.requests[self.request.id].status, RequestStatus.COMPLETED)

    def test_normal_results_review_together_but_abnormal_needs_reasoning(self):
        ids = [o.id for o in self.obs.values()]
        outcome = self.loop.review_batch(ids, "holm", "no_action", inform="letter")
        refused = [ob_id for ob_id, r in outcome.items() if isinstance(r, Refused)]
        self.assertEqual(refused, [self.obs["eGFR"].id])
        self.assertIs(self.obs["eGFR"].status, OPEN)

    def test_follow_up_records_information_and_closes_when_letter_is_sent(self):
        self.loop.review_batch([self.obs[a].id for a in ("HbA1c", "K", "lipids")], "holm", "no_action",
                               inform="letter")
        recheck = self.loop.now + timedelta(days=90)
        review = self.loop.review(self.obs["eGFR"].id, "holm", "new_request",
                                  reasoning="no medication change; recheck creatinine", inform="letter",
                                  follow_up={"tests": ["creatinine"], "planned_for": recheck})
        self.assertTrue(all(o.status is REVIEWED for o in self.obs.values()))
        self.loop.record_patient_informed([o.id for o in self.obs.values()], "sara", "letter")
        self.assertTrue(all(o.status is CLOSED for o in self.obs.values()))
        planned = self.loop.db.requests[review.follow_up_request_id]
        self.assertIs(planned.status, RequestStatus.PLANNED)
        self.assertEqual((planned.sent_at, planned.linked_review_id), (recheck, review.id))
        self.loop.clock.set(recheck)
        self.loop.tick()
        self.assertIs(planned.status, RequestStatus.SENT)

    def test_review_without_patient_information_is_refused(self):
        with self.assertRaises(Refused):
            self.loop.review(self.obs["K"].id, "holm", "no_action")


class S2CriticalPotassiumFriday(unittest.TestCase):
    def setUp(self):
        self.loop = loop = clinic(start=datetime(2026, 11, 6, 8, 30))
        self.request = loop.order("bengt", "holm", ("K", "Na", "creatinine"), LAB)
        loop.collect(self.request.id, "eva")
        loop.clock.set(datetime(2026, 11, 6, 16, 40))
        self.call, self.ob = loop.record_phone_call(self.request.id, "K", 6.4, "mmol/L", caller="lab: Lena",
                                                    received_by="eva")

    def test_call_starts_critical_path_before_electronic_result(self):
        self.assertTrue(self.ob.critical)
        self.assertIsNone(self.ob.result_id)
        self.assertEqual(self.ob.owner_id, "holm")
        self.assertEqual(len(self.loop.notifications_for("holm", "critical")), 1)
        call = self.loop.db.calls[self.call.id]
        self.assertEqual((call.caller, call.received_by, call.at), ("lab: Lena", "eva", datetime(2026, 11, 6, 16, 40)))

    def test_electronic_result_links_to_call_without_second_alert(self):
        loop = self.loop
        loop.record_action(self.ob.id, "sand", "assessed by phone; sent to emergency department")
        loop.clock.set(datetime(2026, 11, 6, 17, 5))
        result = loop.receive(message(loop, self.request.id, "K", 6.4, abnormal=True, critical=True))
        self.assertEqual(self.ob.result_id, result.id)
        self.assertEqual(len(loop.obligations(analyte="K")), 1)
        self.assertEqual(len([n for n in loop.db.notifications if n.kind == "critical"]), 1)

    def test_monday_review_stays_with_orderer_and_shows_actions(self):
        loop = self.loop
        loop.record_action(self.ob.id, "sand", "sent to emergency department")
        loop.receive(message(loop, self.request.id, "K", 6.4, abnormal=True, critical=True))
        loop.clock.set(datetime(2026, 11, 9, 8, 15))
        self.assertIs(self.ob.status, OPEN)
        self.assertEqual(self.ob.actions[0][1:], ("sand", "sent to emergency department"))
        loop.review(self.ob.id, "holm", "emergency", reasoning="handled Friday by Dr Sand", inform="phone")
        self.assertIs(self.ob.status, REVIEWED)

    def test_s2b_out_of_hours_report_reaches_clinic_next_working_day(self):
        loop = clinic(start=datetime(2026, 11, 6, 8, 30))
        request = loop.order("bengt", "holm", ("K",), LAB)
        loop.clock.set(datetime(2026, 11, 6, 18, 30))
        _, ob = loop.record_phone_call(request.id, "K", 6.6, "mmol/L", caller="lab", received_by="on-call physician",
                                       service="Out-of-hours physician service", actions="patient contacted, sent to ED")
        self.assertEqual(loop.notifications_for("holm"), [])
        loop.clock.set(datetime(2026, 11, 9, 8, 0))
        self.assertEqual([n.kind for n in loop.notifications_for("holm")], ["critical handled elsewhere"])
        self.assertEqual(ob.handled_elsewhere, "Out-of-hours physician service")
        self.assertIs(ob.status, OPEN)

    def test_s2c_critical_flag_without_call_starts_critical_path(self):
        loop = self.loop
        loop.clock.advance(days=2)
        recheck = loop.order("bengt", "holm", ("K",), LAB)
        result = loop.receive(message(loop, recheck.id, "K", 6.2, abnormal=True, critical=True))
        ob = obligation_for(loop, result.id)
        self.assertTrue(ob.critical)
        self.assertIn("critical", [n.kind for n in loop.notifications_for("holm") if n.ref == ob.id])
        self.assertIn(ob.id, [n.ref for n in loop.notifications_for("sara", "critical")])


class S3HaemolysedSample(unittest.TestCase):
    def setUp(self):
        self.loop = loop = clinic()
        self.request = loop.order("anna", "holm", ("K", "creatinine"), LAB)
        self.k = loop.receive(message(loop, self.request.id, "K", None, status=ResultStatus.WITHHELD,
                                      comment="haemolysed sample, new sample requested"))
        loop.receive(message(loop, self.request.id, "creatinine", 88, "µmol/L"))

    def test_withheld_value_shows_reason_and_creates_recollection(self):
        view = self.loop.staff_view(self.k.id)
        self.assertIs(view["status"], ResultStatus.WITHHELD)
        self.assertEqual(view["comment"], "haemolysed sample, new sample requested")
        self.assertEqual(self.loop.obligations(analyte="K"), [])
        tasks = list(self.loop.db.tasks.values())
        self.assertEqual([(t.kind, t.request_id) for t in tasks], [("recollect", self.request.id)])
        self.assertIs(self.loop.db.requests[self.request.id].status, RequestStatus.SENT)

    def test_new_sample_completes_request(self):
        loop = self.loop
        loop.clock.advance(days=1)
        loop.receive(message(loop, self.request.id, "K", 4.8, seq=2))
        self.assertEqual(loop.staff_view(self.k.id)["value"], 4.8)
        self.assertEqual(len(loop.obligations(analyte="K")), 1)
        self.assertIs(loop.db.requests[self.request.id].status, RequestStatus.COMPLETED)

    def test_reported_with_comment_keeps_comment_in_trend(self):
        loop = clinic()
        request = loop.order("anna", "holm", ("K",), LAB)
        loop.receive(message(loop, request.id, "K", 5.9, comment="haemolysis may raise potassium"))
        self.assertEqual(loop.trend("anna", "K")[0]["comment"], "haemolysis may raise potassium")


class S4CorrectedAfterReview(unittest.TestCase):
    def setUp(self):
        self.loop = loop = clinic()
        self.request = loop.order("bengt", "holm", ("creatinine",), LAB)
        self.original = message(loop, self.request.id, "creatinine", 98, "µmol/L")
        self.result = loop.receive(self.original)
        self.first = obligation_for(loop, self.result.id)
        self.review = loop.review(self.first.id, "holm", "no_action", inform="1177 message")
        loop.clock.advance(days=3)
        self.correction = message(loop, self.request.id, "creatinine", 210, "µmol/L", seq=2,
                                  status=ResultStatus.CORRECTED, abnormal=True, comment="batch mix-up corrected")
        loop.receive(self.correction)

    def test_correction_is_current_and_unreviewed_with_one_new_obligation(self):
        view = self.loop.staff_view(self.result.id)
        self.assertEqual((view["value"], view["corrected"], view["reviewed"]), (210, True, False))
        new = [o for o in self.loop.obligations(result_id=self.result.id) if o.status is OPEN]
        self.assertEqual(len(new), 1)
        self.assertEqual(new[0].prior_review_id, self.review.id)
        self.assertEqual(self.loop.db.reviews[self.review.id].lab_sequence, 1)

    def test_duplicate_correction_and_resent_original_change_nothing(self):
        loop = self.loop
        self.assertIsNone(loop.receive(self.correction))
        resent = message(loop, self.request.id, "creatinine", 98, "µmol/L")
        loop.receive(resent)
        self.assertEqual(loop.staff_view(self.result.id)["value"], 210)
        self.assertEqual(len(loop.db.results[self.result.id].versions), 2)
        self.assertEqual(len(loop.obligations(result_id=self.result.id)), 2)


class S5LocumLeaves(unittest.TestCase):
    def setUp(self):
        self.loop = loop = clinic()
        self.requests = [loop.order(p, "nyberg", ("ALT",), LAB) for p in ("carl", "anna", "bengt")]
        loop.clock.set(datetime(2026, 11, 6, 16, 0))
        loop.depart("nyberg", by="sara")
        loop.clock.set(datetime(2026, 11, 7, 10, 0))
        self.carl = loop.receive(message(loop, self.requests[0].id, "ALT", 3.1, "µkat/L", abnormal=True))

    def test_results_after_departure_have_an_owner(self):
        self.assertEqual(obligation_for(self.loop, self.carl.id).owner_id, "sara")

    def test_handover_moves_work_and_keeps_history(self):
        loop = self.loop
        loop.clock.set(datetime(2026, 11, 9, 8, 0))
        loop.hand_over_orderer("nyberg", "falk", by="sara")
        ob = obligation_for(loop, self.carl.id)
        self.assertEqual(ob.owner_id, "falk")
        self.assertIn("handover of nyberg's results: sara -> falk", [h[2] for h in ob.history])
        later = loop.receive(message(loop, self.requests[1].id, "ALT", 0.5, "µkat/L"))
        self.assertEqual(obligation_for(loop, later.id).owner_id, "falk")

    def test_unreviewed_after_seven_days_reminds_then_escalates(self):
        loop = self.loop
        loop.hand_over_orderer("nyberg", "falk", by="sara")
        ob = obligation_for(loop, self.carl.id)
        loop.clock.advance(days=7)
        loop.tick()
        self.assertEqual([n.ref for n in loop.notifications_for("falk", "review reminder")], [ob.id])
        self.assertEqual(loop.notifications_for("maria"), [])
        loop.clock.advance(days=2)
        loop.tick()
        self.assertIn(ob.id, [n.ref for n in loop.notifications_for("maria", "review escalation")])
        self.assertIn(ob.id, [n.ref for n in loop.notifications_for("sara", "review escalation")])
        self.assertEqual(loop.open_longer_than(UNIT, timedelta(days=7)), {"falk": [ob.id]})

    def test_departure_with_handover_moves_open_work_directly(self):
        loop = clinic()
        request = loop.order("carl", "nyberg", ("ALT",), LAB)
        result = loop.receive(message(loop, request.id, "ALT", 0.4, "µkat/L"))
        loop.depart("nyberg", by="sara", handover_to="falk")
        self.assertEqual(obligation_for(loop, result.id).owner_id, "falk")


class S6ReviewedButNotActedOn(unittest.TestCase):
    def setUp(self):
        self.loop = loop = clinic()
        request = loop.order("david", "berg", ("PSA",), LAB)
        self.result = loop.receive(message(loop, request.id, "PSA", 6.8, "µg/L", abnormal=True))
        self.ob = obligation_for(loop, self.result.id)

    def test_no_action_requires_reasoning_and_is_reportable(self):
        with self.assertRaises(Refused):
            self.loop.review(self.ob.id, "berg", "no_action", inform="phone")
        self.loop.review(self.ob.id, "berg", "no_action", reasoning="patient asymptomatic", inform="phone")
        reported = self.loop.abnormal_without_action(UNIT)
        self.assertEqual([(r.reviewer_id, r.reasoning) for r in reported], [("berg", "patient asymptomatic")])


class S7PatientSeesItFirst(unittest.TestCase):
    def test_staff_see_patient_visibility_and_review_state(self):
        loop = clinic()
        request = loop.order("anna", "holm", ("eGFR",), LAB)
        result = loop.receive(message(loop, request.id, "eGFR", 52, "mL/min/1.73m²", abnormal=True))
        loop.clock.advance(days=2)
        view = loop.staff_view(result.id)
        self.assertEqual((view["visible_to_patient"], view["reviewed"], view["owner"]), (True, False, "holm"))
        ob = obligation_for(loop, result.id)
        loop.record_action(ob.id, "eva", "patient phoned, worried; asked Dr Holm to prioritise")
        self.assertEqual((ob.owner_id, ob.status), ("holm", OPEN))


class S8SendOutWithoutOrderer(unittest.TestCase):
    def setUp(self):
        self.loop = loop = clinic()
        self.posted = datetime(2026, 11, 20)
        loop.clock.set(datetime(2026, 11, 23, 9, 0))
        self.item = loop.receive(message(loop, None, "rare antibody", None, "titre", patient="frida",
                                         laboratory="University laboratory", source="scanned",
                                         document_received_at=self.posted, comment="positive 1:320"))

    def test_held_in_monitored_queue_not_attached(self):
        self.assertEqual((self.item.owner_id, self.item.reason), ("sara", "scanned document needs an identity check"))
        self.assertEqual(self.loop.db.results, {})
        self.assertEqual([n.kind for n in self.loop.notifications_for("sara")], ["intake"])

    def test_wrong_identity_refused_then_filed_with_owner_and_source(self):
        loop = self.loop
        with self.assertRaises(Refused):
            loop.file_intake(self.item.id, "anna", owner_id="holm", by="sara")
        result = loop.file_intake(self.item.id, "frida", owner_id="holm", by="sara")
        self.assertEqual((result.patient_id, obligation_for(loop, result.id).owner_id), ("frida", "holm"))
        version = result.current
        self.assertEqual((version.source, version.document_received_at, version.received_at),
                         ("scanned", self.posted, datetime(2026, 11, 23, 9, 0)))


class S9ResultNeverComes(unittest.TestCase):
    def test_overdue_requests_are_flagged_and_grouped(self):
        loop = clinic(start=datetime(2026, 3, 3, 9, 0))
        thyroid = [loop.order(p, "holm", ("TSH",), LAB) for p in ("frida", "anna")]
        sodium = loop.order("bengt", "holm", ("Na",), LAB)
        loop.receive(message(loop, sodium.id, "Na", 139))
        loop.clock.advance(days=3)
        loop.tick()
        self.assertEqual(sorted(n.ref for n in loop.notifications_for("holm", "result overdue")),
                         sorted(r.id for r in thyroid))
        self.assertEqual(loop.notifications_for("sara", "result overdue"), [])
        loop.clock.set(datetime(2026, 3, 17, 9, 0))
        loop.tick()
        self.assertEqual(len(loop.notifications_for("sara", "result overdue")), 2)
        self.assertEqual(loop.overdue_requests(UNIT), {(LAB, "TSH"): [r.id for r in thyroid]})

    def test_backlog_delivery_reaches_each_request_once(self):
        loop = clinic(start=datetime(2026, 3, 3, 9, 0))
        request = loop.order("frida", "holm", ("TSH",), LAB)
        loop.clock.advance(days=14)
        backlog = message(loop, request.id, "TSH", 2.1, "mIU/L")
        loop.receive(backlog)
        loop.receive(backlog)
        self.assertEqual(len(loop.obligations(request_id=request.id)), 1)
        self.assertEqual(loop.overdue_requests(UNIT), {})


class S10InterfaceDown(unittest.TestCase):
    def test_outage_requests_and_phoned_results_reconcile_once(self):
        loop = clinic()
        loop.set_interface(False, by="sara")
        requests = [loop.order(p, "holm", ("Na",), LAB) for p in ("bengt", "anna")]
        self.assertEqual({r.channel for r in requests}, {"paper"})
        _, phoned = loop.record_phone_call(requests[0].id, "Na", 118, "mmol/L", caller="lab", received_by="eva")
        loop.clock.advance(days=1)
        loop.set_interface(True, by="sara")
        for request, value, critical in [(requests[0], 118, True), (requests[1], 140, False)]:
            msg = message(loop, request.id, "Na", value, abnormal=critical, critical=critical)
            loop.receive(msg)
            loop.receive(msg)
        self.assertEqual(len(loop.obligations()), 2)
        self.assertIsNotNone(phoned.result_id)
        self.assertTrue(all(o.owner_id == "holm" and o.result_id for o in loop.obligations()))


if __name__ == "__main__":
    unittest.main()
