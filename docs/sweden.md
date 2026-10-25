# Sweden profile

[Master specification](../SPECIFICATION.md) · Draft supporting specification.

The following questions define the first Swedish profile across the [product coverage map](coverage.md). Initial dogfooding settings and implementation order remain open under [Q-PROD-001](decisions.md#product-and-care-settings) and [Q-PROD-002](decisions.md#product-and-care-settings).

## Swedish patient identity

The Swedish implementation must investigate and, where required, support the relevant use of:

- personal identity numbers,
- coordination numbers,
- temporary or reserve identifiers,
- protected personal information.

### Sweden-specific open questions

- **SE-PAT-Q01:** Which source is authoritative for demographics in the first Swedish deployment?
- **SE-PAT-Q02:** Which services are used for reserve identifiers?
- **SE-PAT-Q03:** What exact behavior is required for protected personal data in search, display, messaging, export, and support workflows?

## Swedish terminology and classifications

The Swedish profile must determine where the following are required or appropriate:

- ICD-10-SE,
- KVÅ,
- ICF,
- Snomed CT,
- national information structures and information sets published by Swedish authorities.

No decision is yet made about a single primary terminology for all clinical content.

## National Medication List

The Swedish implementation must determine the required interaction with **Nationella läkemedelslistan (NLL)** based on the medication scope of the product and the first target care setting.

### Open questions

- **SE-MED-Q01:** Which NLL workflows are required in the first release?
- **SE-MED-Q02:** Which medication information is authoritative locally versus in NLL?
- **SE-MED-Q03:** What user workflows are required when local and national medication information differ?

## National Patient Overview

The Swedish implementation must determine whether and how the product participates in **Nationell patientöversikt (NPÖ)**.

### Open questions

- **SE-NPO-Q01:** Is the system a producer of information to NPÖ?
- **SE-NPO-Q02:** Is the system a consumer of NPÖ information?
- **SE-NPO-Q03:** Which information sets are included?

## 1177

The Swedish implementation must determine which patient-facing functions are provided through **1177** and which, if any, are provided directly by the product.

### Open questions

- **SE-1177-Q01:** Which clinical information shall be made available through 1177 journal?
- **SE-1177-Q02:** Which patient interactions should occur through 1177 rather than a product-specific patient interface?
- **SE-1177-Q03:** What delay, review, or withholding rules apply to particular information sets?
- **SE-1177-Q04:** Is patient access history provided through 1177 Journal, as an extract on request from the care provider, or both, and which entries are withheld?

## Swedish identity and trust infrastructure

The first Swedish deployment must determine its requirements regarding infrastructure such as:

- HSA,
- SITHS,
- regional identity and access-management services,
- national or regional security services.

### Open questions

- **SE-IAM-Q01:** Which infrastructure is authoritative for professional identity, role, assignment, and organizational affiliation?
- **SE-IAM-Q02:** Which authorization decisions are made locally versus by shared services?

## Swedish referrals and regional services

Referral and consultation workflows may depend on regional services and established regional practice.

### Open questions

- **SE-REF-Q01:** Which Swedish referral infrastructure must the first deployment support?
- **SE-REF-Q02:** Which parts of the referral process should be product capabilities versus integration with external services?

## Swedish legal and regulatory profile

At minimum, the Swedish implementation shall maintain traceability against the currently applicable requirements arising from areas including:

- patient-record legislation,
- healthcare information processing and access rules,
- data protection,
- cross-provider information sharing,
- confidentiality and secrecy rules,
- medication-list legislation and connection requirements where applicable,
- national interoperability service requirements where applicable,
- medical-device or national medical-information-system regulation where applicable,
- archival and retention requirements,
- cybersecurity obligations applicable to the organization and delivery model.

The exact applicability of each source depends on intended purpose, care setting, provider type, product scope, and deployment model.

---

## Swedish reference sources to track

The following are starting points for the Swedish case study. Applicability and current wording must be checked for each relevant release.

1. **Patient Data Act (Patientdatalag 2008:355), Swedish Parliament**  
   https://www.riksdagen.se/sv/dokument-och-lagar/dokument/svensk-forfattningssamling/patientdatalag-2008355_sfs-2008-355

2. **HSLF-FS 2016:40 — patient records and processing of personal data in healthcare, National Board of Health and Welfare**  
   https://www.socialstyrelsen.se/kunskapsstod-och-regler/regler-och-riktlinjer/foreskrifter-och-allmanna-rad/konsoliderade-foreskrifter/201640-om-journalforing-och-behandling-av-personuppgifter-i-halso--och-sjukvarden/

3. **Information security for healthcare providers, Swedish Authority for Privacy Protection (IMY)**  
   https://www.imy.se/verksamhet/dataskydd/dataskydd-pa-olika-omraden/vard/informationssakerhet--for-vardgivare/

4. **Monitoring access to patient information, IMY**  
   https://www.imy.se/verksamhet/dataskydd/dataskydd-pa-olika-omraden/vard/informationssakerhet--for-vardgivare/kontroll-av-atkomst-till-uppgifter---for-vardgivare/

5. **Assignment of access rights to patient information, IMY**  
   https://www.imy.se/verksamhet/dataskydd/dataskydd-pa-olika-omraden/vard/informationssakerhet--for-vardgivare/tilldelning-av-behorighet-till-uppgifter-om-patienter--for-vardgivare/

6. **National Medication List — requirements for connecting healthcare systems, Swedish eHealth Agency**  
   https://samarbetsyta.ehalsomyndigheten.se/handboken/latest/utveckla-mot-e-haelsomyndighetens-tjaenster/information-stoed-och-krav-per-delsystem/nationella-laekemedelslistan-nll/krav-pa-anslutande-system-nll/sammanstaellning-av-krav/sammanstaellning-av-krav-vard

7. **National Service Platform, Inera**  
   https://www.inera.se/tjanster/arkitektur-och-digital-infrastruktur/nationella-tjansteplattformen/

8. **1177 Journal, Inera**  
   https://www.inera.se/journalen

9. **National Patient Overview (NPÖ), Inera**  
   https://www.inera.se/tjanster/alla-tjanster-a-o/npo---nationell-patientoversikt/

10. **National information structure and national information sets, National Board of Health and Welfare**  
    https://informationsstruktur.socialstyrelsen.se/

11. **National Medical Information Systems (NMI), Swedish Medical Products Agency**  
    https://www.lakemedelsverket.se/sv/medicinteknik/tillverka/nationella-medicinska-informationssystem
