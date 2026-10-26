# Review session: laboratory result loop

[Laboratory result loop](workflow-laboratory-results.md) · [Svensk version](review-session-laboratory-results.sv.md) · **Status:** Script for the first practitioner review; not yet run · **Date:** 2026-10-26

A 30-minute walkthrough that tests the draft rules and failure cases of the [laboratory result loop](workflow-laboratory-results.md) against how a primary-care clinic actually works. It follows [practitioner testing](assurance.md#practitioner-testing-and-dogfooding): synthetic patient, no software, findings linked to rules and cases.

## Setup

- **Participants:** one physician and one nurse from Swedish primary care. One of either is enough for a first session; note which roles were missing.
- **Facilitator and note-taker:** two people if possible. The facilitator does not defend the draft.
- **Materials:** this script and a printed copy of the failure-case table. Do not send the draft rules in advance.
- **Ground rules to state:** the patient is invented; do not mention real patients or identifiable cases; we are testing the specification, not the participants; "we don't do that" and "that never happens" are useful answers.
- **Introduction (2 minutes):** state the ground rules and the patient.
- **Method:** in each scene, first ask how they handle it today. Show the draft rule only afterwards and ask what is wrong with it.

## Synthetic patient

**Anna Berg**, 67, synthetic test identity. Type 2 diabetes and hypertension, treated with metformin and ramipril. Listed at the clinic. Annual diabetes check with blood tests: HbA1c, creatinine with eGFR, potassium, and lipids.

The values below are invented for the scenario and are not clinical guidance.

## Scenes

### 1. Ordering — 3 minutes

*Dr Lind, a locum on a six-week contract, sees Anna and orders the tests. A nurse takes the samples the next morning.*

- Who is responsible for these results once they come back? Does that change because Dr Lind is a locum?
- How does the responsible person appear in your current system?

**Tests:** R1, R6 · clinical question 1.

### 2. Normal and abnormal results arrive — 5 minutes

*Two days later: HbA1c 58 mmol/mol and lipids within target. Creatinine has risen; eGFR is 52, down from 68 a year ago.*

- Walk us through what you do when results arrive. Do you sign off (*vidimera*) each result, each request, or only abnormal ones?
- What do you record when you decide no action is needed? Where?
- Is "seen, no action" a real decision you document, or the absence of one?

**Tests:** R2, R3 · clinical question 3 · the *vidimering* point in [Swedish context](workflow-laboratory-results.md#swedish-context-to-confirm).

### 3. Critical value by phone — 6 minutes

*Friday 16:40, the laboratory phones the clinic: potassium 6.7 mmol/L. The nurse takes the call. Dr Lind has left for the day. The electronic result has not arrived.*

- What happens next, minute by minute? Who is called?
- Where is the phone call recorded, and by whom?
- When the electronic result arrives on Monday, how is it connected to Friday's call?
- What would happen if the nurse had already gone home and the call went unanswered?

**Tests:** R7, F7 · clinical question 2.

### 4. Correction after review — 4 minutes

*Continue scene 3. Anna was assessed on Friday evening. On Monday the laboratory sends a corrected potassium of 4.9 with the comment "haemolysed sample" and asks for a new sample.*

- How do corrected results appear today? Would you notice that a result you already acted on has changed?
- Who arranges the new sample and contacts Anna?
- Should the corrected result need a new sign-off?

**Tests:** R4, F3, F6.

### 5. The locum leaves — 4 minutes

*Dr Lind's contract ends. Three weeks later, the falling eGFR from scene 2 has never been reviewed.*

- How would anyone find out? Who would that be?
- What deadline is acceptable before an unreviewed abnormal result should be raised with someone else?
- Who should receive it: a named colleague, a team list, the clinic manager?

**Tests:** R5, R6, F8 · clinical questions 1 and 2.

### 6. The patient sees it first — 3 minutes

*Anna reads her eGFR in 1177 before any clinician has reviewed it, and calls the clinic worried.*

- Does this happen today? For which results?
- Who takes the call, and what can they see about whether the result was reviewed?
- How is the patient told about results, and is that recorded?

**Tests:** F13 · clinical question 4 · [SE-1177-Q03](sweden.md).

### 7. What did we miss — 3 minutes

Hand over the printed failure-case table.

- Which of these have you seen? Which never happen?
- What goes wrong with results that is not on this list?

**Tests:** clinical question 5.

## Recording findings

Record one row per finding. Do not record anything about real patients.

| Scene | Participant role | Expected (draft) | Observed or said | Impact | Rule, case, or gap | Action |
|---|---|---|---|---|---|---|
| | | | | Safety · Correctness · Workload · Other | | Change rule · New case · New question · None |

Also note the participants' roles and settings, scenes skipped for lack of time, and anything where the two participants disagreed.

## After the session

1. Update the rules, cases, and questions in the [workflow](workflow-laboratory-results.md), noting the session date and roles in its status line.
2. Record roles and settings still unreviewed.
3. Write **Verify** criteria only for rules that survived review.
