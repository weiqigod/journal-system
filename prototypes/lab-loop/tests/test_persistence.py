"""Workflow state that survives a restart (SQLite), including crashes between the two stores."""

import os
import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path

from datetime import datetime

from lab_loop import LabLoop, ObligationStatus, ResultStatus, Role, SimulatedCrash
from lab_loop.model import Obligation, Staff
from lab_loop.service import _State
from lab_loop.store import WorkflowStore, decode, encode, rows

from .support import LAB, clinic, message, obligation_for

HERE = Path(__file__).resolve().parents[1]


class Encoding(unittest.TestCase):
    def test_values_keep_their_types(self):
        when = datetime(2026, 11, 2, 9, 30)
        obligation = Obligation("ob1", "anna", "vc", "req1", "K", "holm", when, critical=True,
                                history=[(when, "system", "assigned")])
        for value in [obligation, {"orderer", "unit"}, ("K", "Na"), ResultStatus.CORRECTED, when, None,
                      {"a": [1, 2]}]:
            decoded = decode(encode(value))
            self.assertEqual((decoded, type(decoded)), (value, type(value)))

    def test_removed_rows_are_deleted(self):
        handle, path = tempfile.mkstemp(suffix=".sqlite")
        os.close(handle)
        self.addCleanup(os.remove, path)
        store = WorkflowStore(path)
        before = _State()
        after = _State(staff={"holm": Staff("holm", "Dr Holm", Role.PHYSICIAN, "vc")})
        store.save(before, after)
        store.save(after, before)
        self.assertEqual(store.load(_State), None)
        store.close()


class Restart(unittest.TestCase):
    def setUp(self):
        handle, self.path = tempfile.mkstemp(suffix=".sqlite")
        os.close(handle)
        self.addCleanup(os.remove, self.path)

    def reopen(self, loop):
        loop.close()
        return LabLoop(loop.config, loop.clock, loop.records, self.path)

    def test_committed_work_survives_restart(self):
        loop = clinic(path=self.path)
        request = loop.order("anna", "holm", ("K",), LAB)
        result = loop.receive(message(loop, request.id, "K", 4.6, abnormal=True))
        ob = obligation_for(loop, result.id)
        loop.review(ob.id, "holm", "no_action", reasoning="known", inform="letter")
        before = rows(loop.db)
        loop = self.reopen(loop)
        self.assertEqual(rows(loop.db), before)
        self.assertEqual(loop.staff_view(result.id)["value"], 4.6)
        loop.record_patient_informed([ob.id], "sara", "letter")
        self.assertIs(self.reopen(loop).db.obligations[ob.id].status, ObligationStatus.CLOSED)

    def test_crash_before_commit_restarts_from_last_commit(self):
        loop = clinic(path=self.path)
        request = loop.order("anna", "holm", ("K",), LAB)
        committed = rows(loop.db)
        msg = message(loop, request.id, "K", 4.1)
        loop.fault = "before_commit"
        with self.assertRaises(SimulatedCrash):
            loop.receive(msg)
        loop = self.reopen(loop)
        self.assertEqual(rows(loop.db), committed)
        loop.receive(msg)
        self.assertEqual(len(loop.records.compositions(loop.db.ehrs["anna"][0])), 1)
        self.assertEqual(len(loop.obligations()), 1)

    def test_ids_continue_after_restart(self):
        loop = clinic(path=self.path)
        first = loop.order("anna", "holm", ("K",), LAB)
        loop = self.reopen(loop)
        second = loop.order("anna", "holm", ("K",), LAB)
        self.assertNotEqual(first.id, second.id)


@unittest.skipUnless(os.environ.get("LAB_LOOP_RECORDS") == "ehrbase", "needs a record store that outlives the process")
class ProcessKilledBetweenStores(unittest.TestCase):
    def test_kill_after_record_write_then_reconcile(self):
        handle, path = tempfile.mkstemp(suffix=".sqlite")
        os.close(handle)
        self.addCleanup(os.remove, path)
        loop = clinic(path=path)
        request = loop.order("anna", "holm", ("K",), LAB)
        ehr_id = loop.db.ehrs["anna"][0]
        loop.close()
        child = textwrap.dedent(f"""
            import os, sys
            from datetime import datetime
            sys.path.insert(0, {str(HERE)!r})
            from lab_loop import Clock, LabLoop, LabMessage, ResultStatus
            from lab_loop.records import EhrbaseRecordStore
            loop = LabLoop(clock=Clock(datetime(2026, 11, 2, 9, 0)), records=EhrbaseRecordStore(), path={path!r})
            loop._fault_point = lambda name: os._exit(9) if name == "after_record_written" else None
            loop.receive(LabMessage("m1", {LAB!r}, "vc", "TEST-ANNA", "K", 1, ResultStatus.FINAL, 4.1, "mmol/L",
                                    request_id={request.id!r}))
        """)
        self.assertEqual(subprocess.run([sys.executable, "-c", child]).returncode, 9)
        loop = LabLoop(loop.config, loop.clock, loop.records, path)
        self.assertEqual(loop.db.results, {})
        [orphan] = loop.records.compositions(ehr_id)
        loop.clock.advance(hours=2)
        [adopted] = loop.reconcile().adopted
        self.assertEqual(loop.db.results[adopted].current.version_uid, orphan)
        loop.close()
        reopened = LabLoop(loop.config, loop.clock, loop.records, path)
        self.assertEqual(len(reopened.obligations(result_id=adopted)), 1)


if __name__ == "__main__":
    unittest.main()
