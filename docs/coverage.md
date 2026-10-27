# Product coverage map

[Master specification](../SPECIFICATION.md) · Working scope inventory.

The product ambition covers the areas below from the outset. This map makes gaps visible without prescribing every feature or module. It is an inventory to expand through research, not a claim of exhaustive requirements or implemented support. Each area may combine shared capabilities, specialist modules, profiles, and integrations; those boundaries remain open.

## Care settings and populations

General record requirements alone do not establish support for a setting. Each row needs representative workflows and checks of its particular needs.

| Area | Variations to examine |
|---|---|
| Primary and outpatient care | First contact, continuity, prevention, chronic conditions, referrals, and follow-up. |
| Emergency and prehospital care | Triage, uncertain identity, rapid treatment, transfers, and interrupted connectivity. |
| Inpatient and intensive care | Admission, rounds, monitoring, beds, transfers, complex therapies, and discharge. |
| Surgery and procedural care | Planning, preparation, anaesthesia, procedure records, recovery, and implant tracking. |
| Mental health and addiction | Assessments, multidisciplinary plans, sensitive information, crisis care, and jurisdiction-specific restrictions. |
| Maternity, newborn, and paediatric care | Linked family records, pregnancy episodes, growth, development, guardianship, and transitions to adult care. |
| Community, home, and long-term care | Nursing and daily care, visits, delegated tasks, mobility, elder care, and coordination with social care. |
| Rehabilitation and palliative care | Functional goals, multidisciplinary interventions, patient preferences, carers, and continuity. |
| Dental and other specialist care | Specialist records and procedures, including oncology, dialysis, cardiology, and sensory care; further disciplines to identify. |
| Remote and patient-directed care | Asynchronous contacts, teleconsultation, patient-reported observations, monitoring devices, and accessibility. |

Across these areas, examine transitions between providers, concurrent care, language and communication needs, disability, safeguarding, and patients without stable identity or contact details.

## Capability coverage and gaps

Links identify existing draft requirements, not completed coverage. The last column records detail still needed; add requirement IDs and verification cases in the owning document as behavior is defined.

| Domain | Existing draft | Detail to develop |
|---|---|---|
| Identity and care context | [PAT, ENC](clinical-requirements.md#patient-identity-and-demographics) | Registration, matching, merge recovery, family relationships, episodes, and movement. |
| Records and shared clinical information | [DOC, CLI](clinical-requirements.md#clinical-documentation), [INF, OVR](clinical-requirements.md#information-requirements) | Documentation lifecycles, concurrent work, provenance, reconciliation, search, and summary freshness. |
| Medication and pharmacy | [MED](clinical-requirements.md#medications) | Prescribing through preparation, dispensing, administration, monitoring, reconciliation, and pharmacy boundaries. |
| Diagnostics and therapeutic orders | [ORD](clinical-requirements.md#orders-investigations-and-results) | Specimens, laboratory disciplines, imaging, pathology, transfusion, specialist procedures, and closed-loop result follow-up. |
| Care delivery and coordination | [REF](clinical-requirements.md#referrals-and-consultations), [WF](clinical-requirements.md#care-plans-tasks-and-clinical-workflow) | Nursing, multidisciplinary plans, referrals, handovers, discharge, and cross-provider responsibility. |
| Scheduling and patient flow | [ENC questions](clinical-requirements.md#organization-care-context-and-encounters) | Appointments, waiting lists, triage queues, beds, theatre capacity, transport, cancellations, and rescheduling. |
| Patient and carer participation | [PRT](clinical-requirements.md#patient-access-and-participation), [CON](clinical-requirements.md#consent-restrictions-and-patient-choices) | Booking, forms, communication, patient-reported outcomes, education, proxies, and information access. |
| User surfaces and assistants | [SUR, AGT](platform-requirements.md#user-surfaces-and-assistants), [usability](platform-requirements.md#usability-and-accessibility) | Workspace and navigation, work lists, what each workflow shows, keyboard and mobile use, assistant capabilities, confirmation, and accessibility. |
| Decision support and assistance | [CDS](clinical-requirements.md#clinical-decision-support), [AI questions](decisions.md#ai) | Clinical rules, protocols, alerts, knowledge sources, and assessment of dictation and AI assistance; techniques remain undecided. |
| Finance and administration | [Product questions](decisions.md#product-and-care-settings) | Eligibility, coding, billing, claims, reimbursement, and financial-system boundaries across payment models. |
| Workforce, supplies, and assets | No dedicated requirements | Staffing and assignment, stock, equipment, procurement, and maintenance interfaces where care workflows depend on them. |
| Quality, population health, and research | No dedicated requirements | Reporting, registries, prevention and recall, surveillance, outcomes, incident review, and governed secondary use. |
| Interoperability and devices | [INT](platform-requirements.md#interoperability) | Specialist and national services, clinical devices, exchange contracts, ownership, reconciliation, and failure recovery. |
| Access, privacy, and accountability | [IAM, AUD](platform-requirements.md#identity-authentication-and-authorization), [CON](clinical-requirements.md#consent-restrictions-and-patient-choices) | Role and purpose rules, restrictions, exceptional access, representatives, disclosures, and monitoring. |
| Modules and international variation | [ADM, MOD](platform-requirements.md#administration-and-configuration), [JUR](platform-requirements.md#jurisdiction-profiles), [localization](platform-requirements.md#internationalization-and-localization) | Extension boundaries, compatibility, configuration changes, terminology, regional variation, and translation. |
| Operation and information lifecycle | [Quality requirements](platform-requirements.md#non-functional-requirements), [MIG](assurance.md#migration) | Installation, upgrades, monitoring, support, security response, downtime, recovery, import/export, archive, and exit. |
| Safety and verification | [Assurance](assurance.md) | Workflow hazards, realistic testing, accessibility, and scenario evidence for each supported configuration. |
| Open-source maintenance | No dedicated requirements; [license](../README.md#license) adopted | Contribution process, module maintainers, reproducible development setup, documentation, and release policy. |

## Developing the detail

Review journeys across domains, such as referral → appointment → encounter → investigation → result → treatment → follow-up. Include handovers and failed or delayed steps. Add workflow definitions where they expose a concrete need; keep each obligation in its owning requirement and link back here. Update gaps as coverage develops, keeping planned scope separate from demonstrated behavior.
