# Laboratory result scenarios

[Laboratory result loop](workflow-laboratory-results.md) · **Status:** Acceptance scenarios grounded in published Swedish routines, laboratory instructions, and reported incidents; not practitioner-reviewed · **Date:** 2026-10-26

Each scenario is a realistic sequence for the [laboratory result loop](workflow-laboratory-results.md). Patients and values are synthetic; values follow the cited laboratories' limits but are not clinical guidance. Source references (E1–E14) point to the workflow's [evidence list](workflow-laboratory-results.md#evidence). Rules (R) and failure cases (F) are defined there.

A scenario passes when every **Expect** line holds. Run each against a deployment configured with a 7-day review deadline, the critical limits of the named laboratory, and Stockholm-style 1177 publication unless stated.

## S1 — Annual diabetes check

**Grounded in:** E3, E4.

Anna Berg, 67, type 2 diabetes and hypertension, treated with metformin and ramipril. Dr Holm orders HbA1c, creatinine with eGFR, potassium, and lipids at her annual check. A nurse collects the samples the next morning.

1. Results arrive two days later: HbA1c 58 mmol/mol, lipids within target, potassium 4.6 mmol/L, eGFR 52 (68 a year earlier, flagged low).
2. Dr Holm reviews all four results on day 3. For eGFR she records: no medication change, recheck creatinine in three months, patient to be informed by letter.
3. A secretary sends the letter and records it.

**Expect:**
- Each result has one review obligation assigned to Dr Holm on arrival (R1).
- The normal results can be reviewed together; the abnormal eGFR cannot be closed as "no action" without reasoning (R3, F18).
- The follow-up records how the patient is informed, and the obligation closes when the letter is recorded (R11).
- The three-month recheck exists as a planned request linked to the review.

## S2 — Critical potassium on a Friday afternoon

**Grounded in:** E5, E6, E7.

Bengt Lund, 72, heart failure, on spironolactone and enalapril. Dr Holm ordered electrolytes on Friday morning and left at 15:00.

1. 16:40: the laboratory phones the clinic. Potassium 6.4 mmol/L, above the laboratory's limit of 6.0. Nurse Eva Ström takes the call.
2. Eva records the call: caller, value, time. The covering physician, Dr Sand, assesses by phone and sends Bengt to the emergency department. Eva documents the instruction and the contact with Bengt.
3. 17:05: the electronic result arrives, flagged critical.
4. Monday: Dr Holm sees the result, the call, and the actions taken, and reviews it.

**Expect:**
- The call starts the critical path before the electronic result exists (R7, F7).
- The electronic result links to the recorded call, not to a second, separate alert.
- The review obligation stays with Dr Holm and is marked as already acted on, not closed (R12).
- The call record identifies who gave the value, who received it, and when, matching the laboratory's own record (E5).

**Variant S2b — clinic closed.** The value is reported at 18:30, after closing. The laboratory reaches the out-of-hours physician service, which contacts Bengt. **Expect:** on Monday the clinic sees the result as handled out of hours, with the other service's note if received, and Dr Holm's review is still required (R12, F16).

**Variant S2c — no call.** Two days later Bengt's potassium is 6.2 again. The laboratory does not phone because a similar value was recently reported (E7). **Expect:** the electronic critical flag alone starts the critical path (R7, F17).

## S3 — Haemolysed sample

**Grounded in:** E12.

Anna Berg's follow-up sample is collected in the afternoon and transported to the laboratory.

1. The laboratory finds marked haemolysis. Potassium is withheld with the comment "haemolysed sample, new sample requested"; creatinine is reported.
2. A nurse books a new sample for the next morning and informs Anna.
3. The new sample gives potassium 4.8 mmol/L.

**Expect:**
- The withheld potassium shows as rejected with the laboratory's reason, not as missing or normal (F6).
- A recollection task is created and assigned; the original request stays open until the new result arrives.
- **Alternative laboratory policy:** if the laboratory instead reports potassium 5.9 with a haemolysis comment, the comment is displayed with the value wherever the value appears, including trends (ORD-004).

## S4 — Result corrected after review

**Grounded in:** E13; [case 2](record-model-comparison.md#case-2--corrected-result-after-review).

1. Dr Holm reviews Bengt's creatinine of 98 µmol/L and records no action.
2. Three days later the laboratory discovers a batch mix-up and sends a corrected creatinine of 210 µmol/L for Bengt.
3. A duplicate of the correction message arrives an hour later; the original 98 µmol/L message is then re-sent by the interface.

**Expect:**
- The corrected value is current and shown as unreviewed; Dr Holm's earlier review stays linked to the 98 µmol/L version (R4, F3).
- Exactly one new obligation is created, linked to the earlier review (F1).
- The re-sent original does not replace the correction (F2).
- Anyone viewing Bengt's results sees that the value was corrected and when.

## S5 — The locum leaves

**Grounded in:** E3, E4, E1.

Dr Nyberg, a locum on a six-week assignment, orders tests for twelve patients in her last week. Her assignment ends on Friday; another locum starts on Monday.

1. Results for seven patients arrive after Friday, including a raised ALT for Carl Ek, 58.
2. The unit's designated monitor reassigns Dr Nyberg's open obligations to the incoming locum.
3. The incoming locum is off sick for a week. Carl Ek's result is unreviewed on day 7.

**Expect:**
- No obligation is ever without an owner, including between Friday and the reassignment (R6, F8).
- On day 7 the owner gets a reminder; when it remains open, the unit's designated monitor and manager are notified (R5).
- A reassigned obligation keeps its history: original orderer, each reassignment, and who made it.
- The unit can list all obligations open longer than 7 days, by owner.

## S6 — Reviewed but not acted on

**Grounded in:** E11.

David Ahl, 66, has PSA 6.8 µg/L, above the action limit in the national prostate cancer care programme for his age. Dr Berg reviews it and records "no action, patient asymptomatic".

**Expect:**
- The review is accepted only with the reasoning recorded (R3, F18).
- The record shows an abnormal result closed without action, with the reasoning, and that is reportable to the medically responsible physician.
- The system does not judge whether the decision was right. Whether to check results against care-programme action limits is a decision-support question outside this slice.

## S7 — The patient sees it first

**Grounded in:** E9.

Anna Berg's eGFR of 52 is published in 1177 the moment it is released to the clinic, marked as unverified. On day 2, before review, she reads it and phones the clinic, worried.

**Expect:**
- The nurse taking the call sees that the result is visible to the patient, that it is unreviewed, and who is responsible for reviewing it (F13).
- The nurse can record the call and ask the responsible clinician to prioritise the review without taking over the obligation.
- Publication to the patient did not mark the result reviewed (R2).

## S8 — A send-out test without an orderer

**Grounded in:** E8.

A nurse sends a sample for a rare antibody test to a university laboratory using a paper request. The request omits the ordering physician.

1. The result arrives by post three weeks later and is scanned into the record.
2. It cannot be matched to an electronic request or an orderer.

**Expect:**
- The result is attached to the right patient after an explicit identity check, and placed in the unit's monitored queue (R8, F5).
- It gets an owner from that queue; it never waits without one.
- The scanned document keeps its source, arrival date, and scan date (INF-002).

## S9 — The result that never comes

**Grounded in:** E10, E4.

After a laboratory interface upgrade, results for one test type stop being delivered to the clinic. Nobody notices; results for other tests arrive normally.

1. Dr Holm ordered thyroid tests for Frida Lind, 34, on 3 March.
2. By 17 March, two weeks past the expected turnaround, no result has arrived.

**Expect:**
- Frida's request is flagged overdue to Dr Holm, then to the unit's monitor if still unresolved (R10, F15).
- The unit can list all requests overdue for a result, grouped by test and laboratory, so a systematic interface failure is visible as a pattern, not as isolated gaps.
- When the backlog is delivered, each result reaches the right request and owner without duplicates (F1).

## S10 — Laboratory interface down

**Grounded in:** E7; [NFR-AVL-004](platform-requirements.md#nfr-avl-004--downtime-procedures).

The connection to the laboratory is down for a full working day.

1. Clinicians cannot send electronic requests; samples go with paper requests.
2. The laboratory phones a critical sodium of 118 mmol/L for one patient.
3. Next morning the connection returns. The laboratory sends all results, including those already phoned.

**Expect:**
- Requests made during the outage are recorded so their results can be matched when they arrive; none are lost (R9, F10).
- The phoned value is recorded as in S2, and the electronic result later links to it.
- After reconnection, each result appears once and reaches its owner; nothing from the outage day is left without an obligation.

## S11 — Result withdrawn after review

**Grounded in:** E13, E14.

1. Carl Ek's ALT of 3.1 µkat/L is flagged high. Dr Holm reviews it, refers him for an ultrasound, and phones him.
2. Two days later the laboratory withdraws the result as entered in error: sample identity uncertain.

**Expect:**
- The result is no longer shown as a current value or in trends. Staff see it as withdrawn, with the reason and the withdrawn value; the patient-visibility state is unchanged (R16).
- Dr Holm's review stays linked to the withdrawn version, and the value stays readable in the record history.
- Dr Holm gets one new obligation linked to the earlier review. "No action" is refused without reasoning; the acknowledgement records what happens to the referral and how Carl is informed.

**Variant — withdrawn before review.** The open obligation becomes the acknowledgement; no second obligation is created, and a repeated withdrawal changes nothing.
