"""Records for the laboratory result loop prototype."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class Role(Enum):
    PHYSICIAN = "physician"
    NURSE = "nurse"
    ADMINISTRATOR = "administrator"
    MANAGER = "manager"


class RequestStatus(Enum):
    PLANNED = "planned"
    SENT = "sent"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class ResultStatus(Enum):
    PRELIMINARY = "preliminary"
    FINAL = "final"
    CORRECTED = "corrected"
    WITHHELD = "withheld"


class ObligationStatus(Enum):
    OPEN = "open"
    REVIEWED = "reviewed"
    CLOSED = "closed"


DECISIONS = {"no_action", "inform_patient", "new_request", "referral", "appointment", "emergency"}


@dataclass
class Unit:
    id: str
    name: str
    monitor_id: str
    manager_id: str


@dataclass
class Staff:
    id: str
    name: str
    role: Role
    unit_id: str
    active: bool = True
    successor_id: str | None = None


@dataclass
class Patient:
    id: str
    pnr: str
    name: str
    unit_id: str
    merged_into: str | None = None


@dataclass
class Request:
    id: str
    patient_id: str
    orderer_id: str | None
    unit_id: str
    tests: tuple[str, ...]
    laboratory: str
    channel: str
    status: RequestStatus
    sent_at: datetime
    expected_by: datetime
    specimen: str = "awaiting collection"
    linked_review_id: str | None = None
    overdue_flags: set[str] = field(default_factory=set)


@dataclass
class LabMessage:
    """One result message as a laboratory or a scanning service delivers it."""

    message_id: str
    laboratory: str
    unit_id: str
    patient_pnr: str
    analyte: str
    lab_sequence: int
    status: ResultStatus
    value: float | None
    unit: str
    reference_range: str | None = None
    abnormal: bool = False
    critical: bool = False
    comment: str | None = None
    request_id: str | None = None
    source: str = "electronic"
    document_received_at: datetime | None = None
    problem: str | None = None  # set by an adapter when the message cannot be processed automatically


@dataclass
class ResultVersion:
    """Workflow index of one result version; the content is in the record store at `version_uid`.

    Status and flags are kept here because the rules act on them. A late older
    version is never written to the record store and has no `version_uid`.
    A `reconciled` version was recovered from the record store without its
    message, so its flags are assumed until the laboratory resends it.
    """

    lab_sequence: int
    status: ResultStatus
    abnormal: bool
    critical: bool
    received_at: datetime
    message_id: str
    source: str
    document_received_at: datetime | None
    version_uid: str | None
    reconciled: bool = False


@dataclass
class Result:
    id: str
    request_id: str
    patient_id: str
    analyte: str
    laboratory: str
    ehr_id: str
    versions: list[ResultVersion] = field(default_factory=list)
    patient_visible_at: datetime | None = None

    @property
    def current(self) -> ResultVersion | None:
        return max(self.versions, key=lambda v: v.lab_sequence, default=None)

    def version(self, lab_sequence: int) -> ResultVersion:
        return next(v for v in self.versions if v.lab_sequence == lab_sequence)


@dataclass
class PhoneCall:
    id: str
    request_id: str
    analyte: str
    value: float
    unit: str
    caller: str
    received_by: str
    at: datetime
    service: str | None = None
    actions: str | None = None


@dataclass
class Obligation:
    """The duty to review one result version and record its follow-up."""

    id: str
    patient_id: str
    unit_id: str
    request_id: str
    analyte: str
    owner_id: str
    created_at: datetime
    result_id: str | None = None
    lab_sequence: int | None = None
    status: ObligationStatus = ObligationStatus.OPEN
    critical: bool = False
    call_id: str | None = None
    handled_elsewhere: str | None = None
    prior_review_id: str | None = None
    review_id: str | None = None
    reminded_at: datetime | None = None
    escalated_at: datetime | None = None
    actions: list[tuple[datetime, str, str]] = field(default_factory=list)
    history: list[tuple[datetime, str, str]] = field(default_factory=list)


@dataclass
class Review:
    id: str
    obligation_id: str
    result_id: str
    lab_sequence: int
    reviewer_id: str
    at: datetime
    decision: str
    reasoning: str | None
    inform: str | None
    agreed_not_to_inform: bool
    follow_up_request_id: str | None = None
    informed_at: datetime | None = None


@dataclass
class Task:
    id: str
    kind: str
    unit_id: str
    owner_id: str
    patient_id: str
    request_id: str
    created_at: datetime
    note: str | None = None
    done_at: datetime | None = None


@dataclass
class IntakeItem:
    """A result that could not be attached automatically, held in a unit queue."""

    id: str
    unit_id: str
    owner_id: str
    message: LabMessage
    reason: str
    received_at: datetime
    filed_at: datetime | None = None


@dataclass
class Notification:
    to: str
    kind: str
    ref: str
    created_at: datetime
    deliver_at: datetime


@dataclass
class AuditEvent:
    at: datetime
    actor: str
    action: str
    ref: str
    detail: str | None = None
