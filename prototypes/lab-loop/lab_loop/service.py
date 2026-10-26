"""Operations of the laboratory result loop and the draft rules R1–R12.

Rule numbers refer to docs/workflow-laboratory-results.md. Each public
operation runs as one transaction: if it raises, all state is restored, so an
interrupted operation cannot leave a stored result without its obligation (F4).
State is in memory; durability across process restarts is out of scope.
"""

from __future__ import annotations

import copy
from contextlib import contextmanager
from dataclasses import dataclass, field, replace
from datetime import datetime, time, timedelta

from .model import (
    DECISIONS,
    AuditEvent,
    IntakeItem,
    LabMessage,
    Notification,
    Obligation,
    ObligationStatus,
    Patient,
    PhoneCall,
    Request,
    RequestStatus,
    Result,
    ResultStatus,
    ResultVersion,
    Review,
    Role,
    Staff,
    Task,
    Unit,
)

OPEN = ObligationStatus.OPEN


class Refused(Exception):
    """The rules do not allow this operation; nothing was changed."""


class SimulatedCrash(Exception):
    """Raised at a fault point to interrupt an operation in tests."""


@dataclass
class Config:
    review_deadline: timedelta = timedelta(days=7)
    escalation_after_reminder: timedelta = timedelta(days=2)
    overdue_request_grace: timedelta = timedelta(days=3)
    opening: time = time(8)
    publish_to_patient: bool = True


class Clock:
    def __init__(self, now: datetime):
        self.now = now

    def advance(self, **kwargs) -> None:
        self.now += timedelta(**kwargs)

    def set(self, now: datetime) -> None:
        self.now = now


@dataclass
class _State:
    units: dict[str, Unit] = field(default_factory=dict)
    staff: dict[str, Staff] = field(default_factory=dict)
    patients: dict[str, Patient] = field(default_factory=dict)
    requests: dict[str, Request] = field(default_factory=dict)
    results: dict[str, Result] = field(default_factory=dict)
    obligations: dict[str, Obligation] = field(default_factory=dict)
    reviews: dict[str, Review] = field(default_factory=dict)
    calls: dict[str, PhoneCall] = field(default_factory=dict)
    tasks: dict[str, Task] = field(default_factory=dict)
    intake: dict[str, IntakeItem] = field(default_factory=dict)
    notifications: list[Notification] = field(default_factory=list)
    audit: list[AuditEvent] = field(default_factory=list)
    messages: set[str] = field(default_factory=set)
    interface_up: bool = True
    next_id: int = 1


class LabLoop:
    def __init__(self, config: Config | None = None, clock: Clock | None = None):
        self.config = config or Config()
        self.clock = clock or Clock(datetime.now())
        self.db = _State()
        self.fault: str | None = None
        self._depth = 0

    # Setup

    def add_unit(self, id: str, name: str, monitor_id: str, manager_id: str) -> Unit:
        self.db.units[id] = Unit(id, name, monitor_id, manager_id)
        return self.db.units[id]

    def add_staff(self, id: str, name: str, role: Role, unit_id: str) -> Staff:
        self.db.staff[id] = Staff(id, name, role, unit_id)
        return self.db.staff[id]

    def add_patient(self, id: str, pnr: str, name: str, unit_id: str) -> Patient:
        self.db.patients[id] = Patient(id, pnr, name, unit_id)
        return self.db.patients[id]

    def set_interface(self, up: bool, by: str) -> None:
        with self._transaction():
            self.db.interface_up = up
            self._audit(by, "laboratory interface " + ("up" if up else "down"), "interface")

    # Requests

    def order(self, patient_id: str, orderer_id: str | None, tests: tuple[str, ...], laboratory: str,
              turnaround: timedelta = timedelta(days=3), planned_for: datetime | None = None,
              linked_review_id: str | None = None) -> Request:
        with self._transaction():
            patient = self._patient(patient_id)
            sent_at = planned_for or self.now
            channel = "electronic" if self.db.interface_up else "paper"
            request = Request(
                id=self._id("req"), patient_id=patient.id, orderer_id=orderer_id, unit_id=patient.unit_id,
                tests=tuple(tests), laboratory=laboratory, channel=channel,
                status=RequestStatus.PLANNED if sent_at > self.now else RequestStatus.SENT,
                sent_at=sent_at, expected_by=sent_at + turnaround, linked_review_id=linked_review_id)
            self.db.requests[request.id] = request
            self._audit(orderer_id or "unit", f"request {request.status.value} ({channel})", request.id, ", ".join(tests))
            return request

    def collect(self, request_id: str, by: str) -> None:
        with self._transaction():
            self._request(request_id).specimen = "collected"
            self._audit(by, "specimen collected", request_id)

    def cancel(self, request_id: str, by: str) -> None:
        with self._transaction():
            self._request(request_id).status = RequestStatus.CANCELLED
            self._audit(by, "request cancelled", request_id)

    # Results

    def receive(self, msg: LabMessage) -> Result | IntakeItem | None:
        """Accept one laboratory message. Returns None for a duplicate (F1)."""
        with self._transaction():
            if msg.message_id in self.db.messages:
                self._audit(msg.laboratory, "duplicate message ignored", msg.message_id)
                return None
            self.db.messages.add(msg.message_id)
            request = self.db.requests.get(msg.request_id) if msg.request_id else None
            patient = self._patient_by_pnr(msg.patient_pnr)
            if msg.source == "scanned":
                reason = "scanned document needs an identity check"
            elif patient is None:
                reason = "unknown patient"
            elif request is None:
                reason = "no matching request"
            elif request.patient_id != patient.id:
                reason = "patient does not match request"
            else:
                return self._store(request, msg)
            return self._to_intake(msg, request.unit_id if request else msg.unit_id, reason)  # R8, F5

    def file_intake(self, item_id: str, patient_id: str, owner_id: str, by: str) -> Result:
        """Attach a queued result after an explicit identity check (R8, S8)."""
        with self._transaction():
            item = self.db.intake[item_id]
            patient = self._patient(patient_id)
            if item.filed_at:
                raise Refused("already filed")
            if patient.pnr != item.message.patient_pnr:
                raise Refused("identity check failed: personal identity number differs")
            self._require_active(owner_id)
            request = self.db.requests.get(item.message.request_id or "")
            if request is None:
                request = Request(
                    id=self._id("req"), patient_id=patient.id, orderer_id=None, unit_id=item.unit_id,
                    tests=(item.message.analyte,), laboratory=item.message.laboratory, channel="paper",
                    status=RequestStatus.SENT, sent_at=item.received_at, expected_by=item.received_at,
                    specimen="analysed")
                self.db.requests[request.id] = request
            result = self._store(request, item.message)
            item.filed_at = self.now
            for ob in self._obligations(result_id=result.id, status=OPEN):
                self._move(ob, owner_id, by, "assigned from intake queue")
            self._audit(by, "intake filed after identity check", item.id, result.id)
            return result

    def _store(self, request: Request, msg: LabMessage) -> Result:
        result = next((r for r in self.db.results.values()
                       if r.request_id == request.id and r.analyte == msg.analyte), None)
        if result is None:
            result = Result(self._id("res"), request.id, request.patient_id, msg.analyte, msg.laboratory)
            self.db.results[result.id] = result
        if any(v.lab_sequence == msg.lab_sequence for v in result.versions):
            self._audit(msg.laboratory, "resent version ignored", result.id, msg.message_id)
            return result
        previous = result.current
        version = ResultVersion(
            msg.lab_sequence, msg.status, msg.value, msg.unit, msg.reference_range, msg.abnormal, msg.critical,
            msg.comment, self.now, msg.message_id, msg.source, msg.document_received_at)
        result.versions.append(version)
        self._fault_point("after_result_stored")
        if previous and version.lab_sequence < previous.lab_sequence:
            self._audit(msg.laboratory, "late older version kept as history", result.id)  # F2
            return result
        if version.status is ResultStatus.WITHHELD:
            request.specimen = "rejected"  # F6
            task = Task(self._id("task"), "recollect", request.unit_id, request.patient_id, request.id,
                        self.now, version.comment)
            self.db.tasks[task.id] = task
            self._notify(self.db.units[request.unit_id].monitor_id, "recollection", task.id)
            return result
        if self.config.publish_to_patient and result.patient_visible_at is None:
            result.patient_visible_at = self.now
        if version.status in (ResultStatus.FINAL, ResultStatus.CORRECTED) or version.critical:
            self._assign_review(request, result, version)
        self._update_request(request)
        return result

    def _assign_review(self, request: Request, result: Result, version: ResultVersion) -> None:
        """R1: one obligation per result version that needs review, always with an owner."""
        waiting = next((o for o in self._obligations(status=OPEN) if o.result_id is None
                        and o.request_id == request.id and o.analyte == result.analyte), None)
        if waiting:  # F7: link to the phoned value instead of raising a second alert
            waiting.result_id, waiting.lab_sequence = result.id, version.lab_sequence
            self._history(waiting, "laboratory", "electronic result linked to phoned value")
            return
        current = next(iter(self._obligations(result_id=result.id, status=OPEN)), None)
        if current:
            current.lab_sequence = version.lab_sequence
            self._history(current, "laboratory", f"now refers to version {version.lab_sequence}")
            if version.critical and not current.critical:
                self._start_critical(current, "critical flag in electronic result")
            return
        prior = self._latest_review(result.id)
        ob = self._new_obligation(request, result.analyte, result_id=result.id, lab_sequence=version.lab_sequence,
                                  prior_review_id=prior.id if prior else None)  # R4
        if prior:
            self._history(ob, "laboratory", f"correction after review {prior.id}")
        if version.critical:
            self._start_critical(ob, "critical flag in electronic result")  # R7, F17

    # Critical values

    def record_phone_call(self, request_id: str, analyte: str, value: float, unit: str, caller: str,
                          received_by: str, service: str | None = None, actions: str | None = None) -> tuple[PhoneCall, Obligation]:
        """R7: a phoned critical value starts the critical path. With `service`, it was handled out of hours (R12)."""
        with self._transaction():
            request = self._request(request_id)
            call = PhoneCall(self._id("call"), request.id, analyte, value, unit, caller, received_by, self.now,
                             service, actions)
            self.db.calls[call.id] = call
            result = next((r for r in self.db.results.values()
                           if r.request_id == request.id and r.analyte == analyte), None)
            ob = next(iter(self._obligations(result_id=result.id, status=OPEN)), None) if result else None
            if ob is None:
                ob = self._new_obligation(request, analyte, result_id=result.id if result else None,
                                          lab_sequence=result.current.lab_sequence if result else None)
            ob.call_id, ob.critical = call.id, True
            self._history(ob, received_by, f"critical value {value} {unit} phoned by {caller}")
            if service:
                ob.handled_elsewhere = service
                if actions:
                    ob.actions.append((self.now, service, actions))
                self._notify(ob.owner_id, "critical handled elsewhere", ob.id, self._next_opening(self.now))
            else:
                self._notify(ob.owner_id, "critical", ob.id)
            return call, ob

    def record_action(self, obligation_id: str, actor: str, text: str) -> None:
        with self._transaction():
            ob = self._obligation(obligation_id)
            ob.actions.append((self.now, actor, text))
            self._history(ob, actor, "action: " + text)

    def _start_critical(self, ob: Obligation, reason: str) -> None:
        ob.critical = True
        self._history(ob, "system", reason)
        for to in {ob.owner_id, self.db.units[ob.unit_id].monitor_id}:
            self._notify(to, "critical", ob.id)

    # Review and follow-up

    def review(self, obligation_id: str, reviewer_id: str, decision: str, *, reasoning: str | None = None,
               inform: str | None = None, agreed_not_to_inform: bool = False,
               follow_up: dict | None = None) -> Review:
        ob = self._obligation(obligation_id)
        reviewer = self.db.staff[reviewer_id]
        patient = self._patient(ob.patient_id)
        if not reviewer.active or reviewer.role is not Role.PHYSICIAN or reviewer.unit_id != patient.unit_id:
            self._audit(reviewer_id, "review refused: no access", ob.id)  # F14: logged although refused
            raise Refused("reviewer has no access to this patient")
        with self._transaction():
            if ob.status is not OPEN:
                raise Refused("obligation is not open")
            if ob.result_id is None:
                raise Refused("the electronic result has not arrived")
            if decision not in DECISIONS:
                raise Refused(f"unknown decision {decision!r}")
            result = self.db.results[ob.result_id]
            version = result.version(ob.lab_sequence)
            if (version.abnormal or version.critical) and decision == "no_action" and not reasoning:
                raise Refused("a no-action decision on an abnormal result needs reasoning")  # R3, F18
            if not inform and not agreed_not_to_inform:
                raise Refused("record how the patient is informed, or that they agreed not to be")  # R11
            review = Review(self._id("rev"), ob.id, result.id, version.lab_sequence, reviewer_id, self.now,
                            decision, reasoning, inform, agreed_not_to_inform)
            self.db.reviews[review.id] = review
            ob.review_id, ob.status = review.id, ObligationStatus.REVIEWED
            if agreed_not_to_inform:
                ob.status = ObligationStatus.CLOSED
            if follow_up:
                request = self.db.requests[result.request_id]
                follow = self.order(ob.patient_id, reviewer_id, tuple(follow_up["tests"]), request.laboratory,
                                    planned_for=follow_up.get("planned_for"), linked_review_id=review.id)
                review.follow_up_request_id = follow.id
            self._history(ob, reviewer_id, f"reviewed version {version.lab_sequence}: {decision}")
            return review

    def review_batch(self, obligation_ids: list[str], reviewer_id: str, decision: str, **kwargs) -> dict:
        """Review several results with one decision; each is accepted or refused on its own."""
        outcome = {}
        for ob_id in obligation_ids:
            try:
                outcome[ob_id] = self.review(ob_id, reviewer_id, decision, **kwargs)
            except Refused as refusal:
                outcome[ob_id] = refusal
        return outcome

    def record_patient_informed(self, obligation_ids: list[str], actor: str, method: str) -> None:
        with self._transaction():
            for ob_id in obligation_ids:
                ob = self._obligation(ob_id)
                if ob.status is not ObligationStatus.REVIEWED:
                    raise Refused(f"{ob_id} is not reviewed")
                self.db.reviews[ob.review_id].informed_at = self.now
                ob.status = ObligationStatus.CLOSED
                self._history(ob, actor, "patient informed by " + method)

    # Ownership

    def reassign(self, obligation_id: str, to: str, by: str) -> None:
        with self._transaction():
            self._require_active(to)
            self._move(self._obligation(obligation_id), to, by, "reassigned")

    def depart(self, staff_id: str, by: str, handover_to: str | None = None) -> None:
        """R6: open work passes to a named colleague, or to the unit monitor."""
        with self._transaction():
            staff = self.db.staff[staff_id]
            successor = handover_to or self.db.units[staff.unit_id].monitor_id
            self._require_active(successor)
            staff.active, staff.successor_id = False, successor
            for ob in self._obligations(owner_id=staff_id, status=OPEN):
                self._move(ob, successor, by, f"{staff.name} left")
            self._audit(by, "staff departed", staff_id, f"work to {successor}")

    def hand_over_orderer(self, departed_id: str, to: str, by: str) -> None:
        """Give a departed orderer's open and future results to a new colleague."""
        with self._transaction():
            self._require_active(to)
            self.db.staff[departed_id].successor_id = to
            for ob in self._obligations(status=OPEN):
                if self.db.requests[ob.request_id].orderer_id == departed_id:
                    self._move(ob, to, by, f"handover of {departed_id}'s results")

    # Time-driven checks

    def tick(self) -> None:
        """Run deadline checks: R5 review escalation and R10 overdue requests."""
        with self._transaction():
            now, cfg = self.now, self.config
            for request in self.db.requests.values():
                if request.status is RequestStatus.PLANNED and request.sent_at <= now:
                    request.status = RequestStatus.SENT
            for ob in self._obligations(status=OPEN):
                if ob.reminded_at is None and now - ob.created_at >= cfg.review_deadline:
                    ob.reminded_at = now
                    self._notify(ob.owner_id, "review reminder", ob.id)
                    self._history(ob, "system", "review deadline passed: owner reminded")
                elif ob.reminded_at and ob.escalated_at is None and now - ob.reminded_at >= cfg.escalation_after_reminder:
                    ob.escalated_at = now
                    unit = self.db.units[ob.unit_id]
                    for to in (unit.monitor_id, unit.manager_id):
                        self._notify(to, "review escalation", ob.id)
                    self._history(ob, "system", "still open after reminder: escalated")
            for request in self.db.requests.values():
                if request.status is not RequestStatus.SENT or now < request.expected_by:
                    continue
                if "orderer" not in request.overdue_flags:
                    request.overdue_flags.add("orderer")
                    self._notify(self._responsible(request.orderer_id, request.unit_id), "result overdue", request.id)
                if "unit" not in request.overdue_flags and now >= request.expected_by + cfg.overdue_request_grace:
                    request.overdue_flags.add("unit")
                    self._notify(self.db.units[request.unit_id].monitor_id, "result overdue", request.id)

    # Queries

    @property
    def now(self) -> datetime:
        return self.clock.now

    def obligations(self, **filters) -> list[Obligation]:
        return self._obligations(**filters)

    def notifications_for(self, staff_id: str, kind: str | None = None) -> list[Notification]:
        return [n for n in self.db.notifications
                if n.to == staff_id and n.deliver_at <= self.now and (kind is None or n.kind == kind)]

    def open_longer_than(self, unit_id: str, age: timedelta) -> dict[str, list[str]]:
        by_owner: dict[str, list[str]] = {}
        for ob in self._obligations(unit_id=unit_id, status=OPEN):
            if self.now - ob.created_at > age:
                by_owner.setdefault(ob.owner_id, []).append(ob.id)
        return by_owner

    def overdue_requests(self, unit_id: str) -> dict[tuple[str, str], list[str]]:
        groups: dict[tuple[str, str], list[str]] = {}
        for request in self.db.requests.values():
            if request.unit_id == unit_id and request.status is RequestStatus.SENT and self.now >= request.expected_by:
                for test in request.tests:
                    if not self._final(request, test):
                        groups.setdefault((request.laboratory, test), []).append(request.id)
        return groups

    def abnormal_without_action(self, unit_id: str) -> list[Review]:
        found = []
        for review in self.db.reviews.values():
            version = self.db.results[review.result_id].version(review.lab_sequence)
            if self.db.obligations[review.obligation_id].unit_id == unit_id and review.decision == "no_action" \
                    and (version.abnormal or version.critical):
                found.append(review)
        return found

    def staff_view(self, result_id: str) -> dict:
        """What staff see about one result, including its patient visibility (F13)."""
        result = self.db.results[result_id]
        version = result.current
        open_ob = next(iter(self._obligations(result_id=result.id, status=OPEN)), None)
        reviewed = any(r.result_id == result.id and r.lab_sequence == version.lab_sequence
                       for r in self.db.reviews.values())
        return {
            "value": version.value, "unit": version.unit, "status": version.status, "comment": version.comment,
            "corrected": version.status is ResultStatus.CORRECTED, "versions": len(result.versions),
            "reviewed": reviewed, "owner": open_ob.owner_id if open_ob else None,
            "visible_to_patient": result.patient_visible_at is not None, "visible_since": result.patient_visible_at,
        }

    def trend(self, patient_id: str, analyte: str) -> list[dict]:
        """F12: each value keeps its own unit, range, and comment; nothing is converted."""
        rows = []
        for result in self.db.results.values():
            version = result.current
            if result.patient_id == patient_id and result.analyte == analyte and version.status is not ResultStatus.WITHHELD:
                rows.append({"at": version.received_at, "value": version.value, "unit": version.unit,
                             "reference_range": version.reference_range, "comment": version.comment})
        return sorted(rows, key=lambda row: row["at"])

    def merge_patients(self, duplicate_id: str, surviving_id: str, by: str) -> None:
        """F11: requests, results, and obligations follow the surviving identity."""
        with self._transaction():
            self._patient(surviving_id)
            for record in [*self.db.requests.values(), *self.db.results.values(), *self.db.tasks.values()]:
                if record.patient_id == duplicate_id:
                    record.patient_id = surviving_id
            for ob in self.db.obligations.values():
                if ob.patient_id == duplicate_id:
                    ob.patient_id = surviving_id
                    self._history(ob, by, f"moved from patient {duplicate_id} by merge")
            self.db.patients[duplicate_id].merged_into = surviving_id
            self._audit(by, "patients merged", duplicate_id, surviving_id)

    # Internals

    @contextmanager
    def _transaction(self):
        if self._depth:
            self._depth += 1
            try:
                yield
            finally:
                self._depth -= 1
            return
        snapshot = copy.deepcopy(self.db)
        self._depth = 1
        try:
            yield
        except BaseException:
            self.db = snapshot
            raise
        finally:
            self._depth = 0

    def _fault_point(self, name: str) -> None:
        if self.fault == name:
            self.fault = None
            raise SimulatedCrash(name)

    def _id(self, prefix: str) -> str:
        self.db.next_id += 1
        return f"{prefix}{self.db.next_id - 1}"

    def _patient(self, patient_id: str) -> Patient:
        patient = self.db.patients[patient_id]
        return self._patient(patient.merged_into) if patient.merged_into else patient

    def _patient_by_pnr(self, pnr: str) -> Patient | None:
        return next((p for p in self.db.patients.values() if p.pnr == pnr and not p.merged_into), None)

    def _request(self, request_id: str) -> Request:
        return self.db.requests[request_id]

    def _obligation(self, obligation_id: str) -> Obligation:
        return self.db.obligations[obligation_id]

    def _obligations(self, **filters) -> list[Obligation]:
        return [o for o in self.db.obligations.values()
                if all(getattr(o, key) == value for key, value in filters.items())]

    def _latest_review(self, result_id: str) -> Review | None:
        reviews = [r for r in self.db.reviews.values() if r.result_id == result_id]
        return max(reviews, key=lambda r: r.at, default=None)

    def _final(self, request: Request, test: str) -> bool:
        return any(r.request_id == request.id and r.analyte == test and r.current.status in
                   (ResultStatus.FINAL, ResultStatus.CORRECTED) for r in self.db.results.values())

    def _update_request(self, request: Request) -> None:
        if request.status is RequestStatus.SENT and all(self._final(request, test) for test in request.tests):
            request.status = RequestStatus.COMPLETED

    def _responsible(self, staff_id: str | None, unit_id: str) -> str:
        """The active person who holds a staff member's work, following handovers (R6)."""
        seen = set()
        while staff_id and staff_id not in seen:
            seen.add(staff_id)
            staff = self.db.staff[staff_id]
            if staff.active:
                return staff_id
            staff_id = staff.successor_id
        return self.db.units[unit_id].monitor_id

    def _require_active(self, staff_id: str) -> None:
        if not self.db.staff[staff_id].active:
            raise Refused(f"{staff_id} is not active")

    def _new_obligation(self, request: Request, analyte: str, **fields) -> Obligation:
        ob = Obligation(self._id("ob"), request.patient_id, request.unit_id, request.id, analyte,
                        self._responsible(request.orderer_id, request.unit_id), self.now, **fields)
        self.db.obligations[ob.id] = ob
        self._history(ob, "system", f"assigned to {ob.owner_id}")
        return ob

    def _move(self, ob: Obligation, to: str, by: str, why: str) -> None:
        self._history(ob, by, f"{why}: {ob.owner_id} -> {to}")
        ob.owner_id = to

    def _to_intake(self, msg: LabMessage, unit_id: str, reason: str) -> IntakeItem:
        unit = self.db.units[unit_id]
        item = IntakeItem(self._id("in"), unit.id, unit.monitor_id, replace(msg), reason, self.now)
        self.db.intake[item.id] = item
        self._notify(unit.monitor_id, "intake", item.id)
        self._audit(msg.laboratory, "result held in unit queue", item.id, reason)
        return item

    def _next_opening(self, at: datetime) -> datetime:
        opening = datetime.combine(at.date(), self.config.opening)
        if opening <= at:
            opening += timedelta(days=1)
        while opening.weekday() >= 5:
            opening += timedelta(days=1)
        return opening

    def _notify(self, to: str, kind: str, ref: str, deliver_at: datetime | None = None) -> None:
        self.db.notifications.append(Notification(to, kind, ref, self.now, deliver_at or self.now))

    def _history(self, ob: Obligation, actor: str, text: str) -> None:
        ob.history.append((self.now, actor, text))

    def _audit(self, actor: str, action: str, ref: str, detail: str | None = None) -> None:
        self.db.audit.append(AuditEvent(self.now, actor, action, ref, detail))
