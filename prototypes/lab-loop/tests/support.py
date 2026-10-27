"""A synthetic primary-care unit shared by the tests."""

from __future__ import annotations

import atexit
import itertools
import os
import tempfile
from datetime import datetime

from lab_loop import Clock, Config, LabLoop, LabMessage, ResultStatus, Role
from lab_loop.records import EhrbaseRecordStore, MemoryRecordStore

MONDAY = datetime(2026, 11, 2, 9, 0)
LAB = "Klinisk kemi"
UNIT = "vc"

_message_ids = itertools.count(1)
_ehrbase = None


def record_store():
    """The in-memory store, or the local EHRbase when LAB_LOOP_RECORDS=ehrbase."""
    global _ehrbase
    if os.environ.get("LAB_LOOP_RECORDS") == "ehrbase":
        _ehrbase = _ehrbase or EhrbaseRecordStore()
        return _ehrbase
    return MemoryRecordStore()


def state_path() -> str | None:
    """A fresh SQLite file when LAB_LOOP_STATE=sqlite; otherwise workflow state stays in memory."""
    if os.environ.get("LAB_LOOP_STATE") != "sqlite":
        return None
    handle, path = tempfile.mkstemp(suffix=".sqlite")
    os.close(handle)
    atexit.register(os.remove, path)
    return path


def checked(loop: LabLoop) -> LabLoop:
    """Make every commit verify that reloading the file reproduces the committed state."""
    save = loop.store.save

    def save_and_verify(before, after):
        save(before, after)
        if loop.store.load(type(after)) != after:
            raise AssertionError("workflow state did not survive a reload")

    loop.store.save = save_and_verify
    return loop


def clinic(start: datetime = MONDAY, path: str | None = None, records=None, **config) -> LabLoop:
    path = path or state_path()
    loop = LabLoop(Config(**config), Clock(start), records or record_store(), path)
    if loop.store:
        checked(loop)
    loop.add_unit(UNIT, "Vårdcentral Norr", monitor_id="sara", manager_id="maria")
    loop.add_unit("other", "Vårdcentral Syd", monitor_id="olof", manager_id="olof")
    for id, name, role, unit in [
        ("holm", "Dr Holm", Role.PHYSICIAN, UNIT),
        ("sand", "Dr Sand", Role.PHYSICIAN, UNIT),
        ("berg", "Dr Berg", Role.PHYSICIAN, UNIT),
        ("nyberg", "Dr Nyberg (locum)", Role.PHYSICIAN, UNIT),
        ("falk", "Dr Falk (locum)", Role.PHYSICIAN, UNIT),
        ("eva", "Eva Ström", Role.NURSE, UNIT),
        ("sara", "Sara (care administrator)", Role.ADMINISTRATOR, UNIT),
        ("maria", "Maria (unit manager)", Role.MANAGER, UNIT),
        ("olsson", "Dr Olsson", Role.PHYSICIAN, "other"),
        ("olof", "Olof (manager)", Role.MANAGER, "other"),
    ]:
        loop.add_staff(id, name, role, unit)
    for id, name in [("anna", "Anna Berg"), ("bengt", "Bengt Lund"), ("carl", "Carl Ek"),
                     ("david", "David Ahl"), ("frida", "Frida Lind")]:
        loop.add_patient(id, f"TEST-{id.upper()}", name, UNIT)
    return loop


def message(loop: LabLoop, request_id: str | None, analyte: str, value: float | None, unit: str = "mmol/L", *,
            seq: int = 1, status: ResultStatus = ResultStatus.FINAL, patient: str | None = None,
            message_id: str | None = None, **fields) -> LabMessage:
    if patient is None:
        patient = loop.db.requests[request_id].patient_id
    return LabMessage(
        message_id=message_id or f"msg{next(_message_ids)}", laboratory=fields.pop("laboratory", LAB),
        unit_id=UNIT, patient_pnr=f"TEST-{patient.upper()}", analyte=analyte, lab_sequence=seq, status=status,
        value=value, unit=unit, request_id=request_id, **fields)


def obligation_for(loop: LabLoop, result_id: str):
    return next(o for o in loop.obligations(result_id=result_id))
