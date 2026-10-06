# Sepsis Screening and SEP-1 Bundle Compliance

I'm a registered nurse transitioning into healthcare analytics. This project applies the CMS SEP-1 measure to patient data to screen for severe sepsis and evaluate whether each bundle element was completed on time. Hospitals report SEP-1 performance to CMS, and this project models the analysis behind that reporting.

All data in this project is synthetic. No real patient information is used.

## What is SEP-1?

SEP-1, the Severe Sepsis and Septic Shock Management Bundle, is a quality measure from the Centers for Medicare & Medicaid Services (CMS). It checks whether hospitals complete a set of time-sensitive steps for patients with severe sepsis or septic shock, such as drawing a lactate, obtaining blood cultures before antibiotics, starting antibiotics, and giving IV fluids when needed.

## Overview

The screener (`sepsis_screener_classes.py`) evaluates a patient's vitals and labs using the same sequence a nurse follows at the bedside. It checks for infection, counts SIRS criteria, identifies organ dysfunction, and classifies the patient as no sepsis, sepsis, or severe sepsis. For each patient, it reports the findings behind the classification, the recommended action, and the bundle elements that apply.

The compliance analysis (`sepsis_compliance.py`) loads the encounter data, screens every patient, and checks each bundle element for severe sepsis cases. It reports overall compliance, compliance by element with the reason for each failure, and compliance by unit.

The data generator (`generate_sepsis_data.py`) produces 300 synthetic encounters across four units from January through June 2026. Each severe sepsis case includes a time zero and timestamps for every bundle element. The data includes realistic gaps in care, such as delayed antibiotics and cultures drawn after antibiotics, so the compliance results reflect what a real review would show.

## Criteria

The rules follow the CMS SEP-1 measure for non-pregnant adults.

Sepsis: known or suspected infection plus 2 or more SIRS criteria (temperature above 100.9 F or below 96.8 F, HR above 90, RR above 20, WBC above 12,000 or below 4,000, or bands above 10%).

Severe sepsis: sepsis plus at least one sign of organ dysfunction (SBP below 90 or MAP below 65, lactate above 2, creatinine above 2.0, platelets below 100,000 or INR above 1.5, bilirubin above 2).

Bundle elements: initial lactate, blood cultures before antibiotics, broad-spectrum antibiotics, a 30 mL/kg fluid bolus for hypotension or lactate of 4 or higher, and a repeat lactate when the initial result is above 2.

Septic shock, vasopressors, and organ dysfunction signs that require more than one reading are not yet included. Nurse actions are kept general because escalation steps vary by facility, and bundle timing is currently simplified relative to the full SEP-1 specifications.

## Design

The code is organized into two classes. `Patient` stores clinical data, and `SepsisProtocol` contains all screening and treatment rules. Keeping the rules separate from the data allows additional protocols to be added later and applied to the same patients.

Clinical thresholds such as MAP and lactate are defined as named constants, so updates to a standard require a change in only one place.

The screener includes six test patients, each designed to cover a different path through the logic, from no infection through severe sepsis requiring the full bundle.

## Running the project

```
python generate_sepsis_data.py
python sepsis_screener_classes.py
python sepsis_compliance.py
```

The first command creates `sepsis_encounters.csv`. The second prints the screening criteria and evaluates the six test patients. The third produces the compliance report.

## Results

Of 300 encounters, 140 met severe sepsis criteria. Overall bundle compliance was 25%.

| Element | Compliance |
|---|---|
| Initial lactate (3 hr) | 81% |
| Cultures before antibiotics | 79% |
| Fluids 30 mL/kg (3 hr) | 68% |
| Antibiotics (3 hr) | 66% |
| Repeat lactate (6 hr) | 43% |

Because the data is synthetic, these results reflect how the generator was configured rather than real performance. Units are assigned at random, so the differences between units reflect random variation in small samples rather than true differences in care.

## Next steps

The next phase will identify encounters that meet severe sepsis criteria but lack the corresponding diagnosis codes, connecting clinical documentation to coding accuracy and revenue cycle performance. I also plan to tune the generator toward more realistic timing and add the full SEP-1 time windows.

This project is for educational purposes and is not intended for clinical use.

## References

Centers for Medicare & Medicaid Services. Specifications Manual for National Hospital Inpatient Quality Measures, SEP-1: Severe Sepsis and Septic Shock: Management Bundle. QualityNet. https://qualitynet.cms.gov

Centers for Medicare & Medicaid Services, Hospital Inpatient Quality Reporting Program. SEP-1 presentation slides, March 2023. Quality Reporting Center. https://www.qualityreportingcenter.com/globalassets/iqr-2023-events/iqr32423/march2023_sep_1_npc_final508.pdf
