# sepsis_hospital_policy_project-
### **Sepsis Screening and SEP-1 Bundle Compliance**

I'm a registered nurse transitioning into healthcare analytics. This project applies the CMS SEP-1 measure to patient data to screen for severe sepsis and evaluate whether each bundle element was completed on time. Hospitals report SEP-1 performance to CMS, and this project models the analysis behind that reporting.

All data in this project is synthetic. No real patient information is used.



### **Overview**

The screener (sepsis_screener_classes.py) evaluates a patient's vitals and labs using the same sequence a nurse follows at the bedside. It checks for infection, counts SIRS criteria, identifies organ dysfunction, and classifies the patient as no sepsis, sepsis, or severe sepsis. For each patient, it reports the findings behind the classification, the recommended action, and the bundle elements that apply.

The data generator (generate_sepsis_data.py) produces 300 synthetic encounters across four units from January through June 2026. Each severe sepsis case includes a time zero and timestamps for every bundle element. The data includes realistic gaps in care, such as delayed antibiotics and cultures drawn after antibiotics, so the compliance results reflect what a real review would show.


### **Criteria**

The rules follow the CMS SEP-1 measure for non-pregnant adults.

**Sepsis:** known or suspected infection plus 2 or more SIRS criteria (temperature above 100.9 F or below 96.8 F, HR above 90, RR above 20, WBC above 12,000 or below 4,000, or bands above 10%).

**Severe sepsis:** sepsis plus at least one sign of organ dysfunction (SBP below 90 or MAP below 65, lactate above 2, creatinine above 2.0, platelets below 100,000 or INR above 1.5, bilirubin above 2).

**Bundle elements:** initial lactate, blood cultures before antibiotics, broad-spectrum antibiotics, a 30 mL/kg fluid bolus for hypotension or lactate of 4 or higher, and a repeat lactate when the initial result is above 2.

Septic shock, vasopressors, and organ dysfunction signs that require more than one reading are not yet included. Nurse actions are kept general because escalation steps vary by facility, and bundle timing is currently simplified relative to the full SEP-1 specifications.


### **Design**

The code is organized into two classes. Patient stores clinical data, and SepsisProtocol contains all screening and treatment rules. Keeping the rules separate from the data allows additional protocols to be added later and applied to the same patients.

Clinical thresholds such as MAP and lactate are defined as named constants, so updates to a standard require a change in only one place.

The screener includes six test patients, each designed to cover a different path through the logic, from no infection through severe sepsis requiring the full bundle.


### **Running the Project**

python generate_sepsis_data.py

python sepsis_screener_classes.py

The first command creates sepsis_encounters.csv. The second prints the screening criteria and evaluates the six test patients.


### **Next Steps**

I'm currently building the compliance analysis: loading the encounter data, measuring completion of each bundle element against SEP-1 time windows, and reporting results by element and by unit. The following phase will identify encounters that meet severe sepsis criteria but lack the corresponding diagnosis codes, connecting clinical documentation to coding accuracy and revenue cycle performance.

This project is for educational purposes and is not intended for clinical use.
