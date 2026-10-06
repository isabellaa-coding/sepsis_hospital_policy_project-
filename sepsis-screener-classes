# Sepsis Screener -- teaching tool
# Criteria based on the CMS SEP-1 severe sepsis measure (public national standard).
# Scope: non-pregnant adult patients. Educational use only, not for clinical decisions.


class Patient:
    # Patient only holds data -- no rules live here
    def __init__(self, name, infection, temp, HR, RR, WBC, bands,
                 SBP, MAP, lactate, creatinine, platelets, INR, bilirubin):
        self.name = name
        self.infection = infection
        self.temp = temp
        self.HR = HR
        self.RR = RR
        self.WBC = WBC
        self.bands = bands
        self.SBP = SBP
        self.MAP = MAP
        self.lactate = lactate
        self.creatinine = creatinine
        self.platelets = platelets
        self.INR = INR
        self.bilirubin = bilirubin


class SepsisProtocol:
    # All the rules live here. Each method takes a patient to evaluate.

    MAP_THRESHOLD = 65        # hypotension: MAP < 65
    LACTATE_THRESHOLD = 2.0   # organ dysfunction: lactate > 2
    LACTATE_FLUIDS = 4.0      # fluid bolus if lactate >= 4

    def print_policy(self):
        print("SEPSIS SCREENING -- Adult Patients")
        print()
        print("Who gets screened: adult patients with a known or suspected infection.")
        print()
        print("Step 1 -- SIRS criteria (count how many are abnormal):")
        print("  - Temperature above 100.9 F or below 96.8 F")
        print("  - Heart rate above 90")
        print("  - Respiratory rate above 20")
        print("  - WBC above 12,000 or below 4,000, or bands above 10%")
        print()
        print("Step 2 -- Look for organ dysfunction (any one counts):")
        print("  - SBP below 90 or MAP below 65")
        print("  - Lactate above 2")
        print("  - Creatinine above 2.0")
        print("  - Platelets below 100,000 or INR above 1.5")
        print("  - Bilirubin above 2")
        print()
        print("Step 3 -- Classify:")
        print("  - Sepsis: infection + 2 or more SIRS criteria")
        print("  - Severe sepsis: sepsis + at least 1 sign of organ dysfunction")
        print()

    # ---------- Screening ----------

    def sirs_findings(self, patient):
        findings = []
        if patient.temp > 100.9 or patient.temp < 96.8:
            findings.append(f"Temp {patient.temp} (>100.9 or <96.8)")
        if patient.HR > 90:
            findings.append(f"HR {patient.HR} (HR > 90)")
        if patient.RR > 20:
            findings.append(f"RR {patient.RR} (RR > 20)")
        if patient.WBC > 12000 or patient.WBC < 4000 or patient.bands > 10:
            findings.append(f"WBC {patient.WBC} (WBC > 12000 or < 4000) and bands {patient.bands} (bands > 10%)")
        return findings

    def is_sepsis(self, patient):
        # No known or suspected infection means no sepsis
        if patient.infection not in ("known", "suspected"):
            return False
        # Infection + 2 or more SIRS findings = sepsis
        return len(self.sirs_findings(patient)) >= 2

    def is_hypotensive(self, patient):
        return patient.SBP < 90 or patient.MAP < self.MAP_THRESHOLD

    def organ_dysfunction_findings(self, patient):
        findings = []
        if self.is_hypotensive(patient):
            findings.append(f"Hypotension: SBP {patient.SBP} (<90) or MAP {patient.MAP} (<{self.MAP_THRESHOLD})")
        if patient.lactate > self.LACTATE_THRESHOLD:
            findings.append(f"Lactate: {patient.lactate} (> {self.LACTATE_THRESHOLD})")
        if patient.creatinine > 2.0:
            findings.append(f"Creatinine: {patient.creatinine} (> 2.0)")
        if patient.platelets < 100000 or patient.INR > 1.5:
            findings.append(f"Coagulopathy: platelets {patient.platelets} (< 100,000) or INR {patient.INR} (> 1.5)")
        if patient.bilirubin > 2:
            findings.append(f"Bilirubin: {patient.bilirubin} (> 2)")
        return findings

    def is_severe_sepsis(self, patient):
        # Severe sepsis = sepsis AND at least 1 organ dysfunction finding
        return self.is_sepsis(patient) and len(self.organ_dysfunction_findings(patient)) >= 1

    # ---------- RN action ----------

    def action(self, patient):
        # Check severe first: every severe sepsis patient also meets sepsis criteria
        if self.is_severe_sepsis(patient):
            return "Notify provider immediately; activate sepsis alert per facility protocol"
        elif self.is_sepsis(patient):
            return "Notify provider"
        else:
            return "No sepsis action; continue routine assessment"

    # ---------- Treatment bundle (SEP-1) ----------

    def treatments(self, patient):
        if not self.is_severe_sepsis(patient):
            return []

        orders = []
        # 3-hour bundle
        orders.append("Initial serum lactate")
        orders.append("Blood cultures BEFORE antibiotics")
        orders.append("Broad-spectrum IV antibiotics")

        # Fluids if hypotensive OR lactate >= 4
        if self.is_hypotensive(patient) or patient.lactate >= self.LACTATE_FLUIDS:
            orders.append("Crystalloid fluid bolus 30 mL/kg")

        # 6-hour bundle: repeat lactate if initial was elevated
        if patient.lactate > self.LACTATE_THRESHOLD:
            orders.append("Repeat serum lactate within 6 hours")

        # Vasopressors (persistent hypotension after fluids) need post-fluid data -- not yet modeled
        return orders

    # ---------- Full report ----------

    def screen(self, patient):
        if self.is_severe_sepsis(patient):
            result = "SEVERE SEPSIS"
        elif self.is_sepsis(patient):
            result = "SEPSIS"
        else:
            result = "Does not meet sepsis criteria"
        print(f"{patient.name}: {result}")

        print(f"  Infection: {patient.infection}")

        sirs = self.sirs_findings(patient)
        print(f"  SIRS criteria met ({len(sirs)}):")
        for finding in sirs:
            print(f"    - {finding}")

        organ = self.organ_dysfunction_findings(patient)
        print(f"  Organ dysfunction findings ({len(organ)}):")
        for finding in organ:
            print(f"    - {finding}")

        print(f"  ACTION: {self.action(patient)}")

        orders = self.treatments(patient)
        if orders:
            print("  BUNDLE:")
            for order in orders:
                print(f"    - {order}")
        print()


if __name__ == "__main__":
    # Runs only when this file is run directly, not when imported
    # Test patients -- each one is designed to hit a different path
    patients = [
        # Expected: no sepsis (no infection, even though SIRS is positive)
        Patient("Patient A", infection="none", temp=101, HR=110, RR=24, WBC=13000, bands=5,
                SBP=120, MAP=85, lactate=1.0, creatinine=0.9, platelets=250000, INR=1.0, bilirubin=0.8),

        # Expected: no sepsis (infection, but only 1 SIRS criterion)
        Patient("Patient B", infection="suspected", temp=98.6, HR=95, RR=16, WBC=9000, bands=3,
                SBP=118, MAP=82, lactate=1.2, creatinine=1.0, platelets=220000, INR=1.1, bilirubin=0.7),

        # Expected: sepsis (infection + 4 SIRS, normal BP and labs)
        Patient("Patient C", infection="known", temp=101, HR=95, RR=27, WBC=11000, bands=12,
                SBP=124, MAP=88, lactate=1.5, creatinine=1.1, platelets=200000, INR=1.0, bilirubin=0.9),

        # Expected: severe sepsis (sepsis + hypotension) -> fluids
        Patient("Patient D", infection="suspected", temp=98.7, HR=101, RR=19, WBC=14000, bands=9,
                SBP=87, MAP=66, lactate=1.8, creatinine=1.2, platelets=180000, INR=1.2, bilirubin=1.0),

        # Expected: severe sepsis from lactate alone (BP normal) -> repeat lactate, no fluids
        Patient("Patient E", infection="known", temp=95.9, HR=118, RR=22, WBC=3500, bands=4,
                SBP=110, MAP=78, lactate=3.4, creatinine=1.3, platelets=150000, INR=1.3, bilirubin=1.1),

        # Expected: severe sepsis, very sick -> fluids AND repeat lactate
        Patient("Patient F", infection="known", temp=102.3, HR=124, RR=26, WBC=18500, bands=14,
                SBP=84, MAP=58, lactate=4.6, creatinine=2.4, platelets=92000, INR=1.7, bilirubin=1.4),
    ]

    protocol = SepsisProtocol()
    protocol.print_policy()

    for patient in patients:
        protocol.screen(patient)
