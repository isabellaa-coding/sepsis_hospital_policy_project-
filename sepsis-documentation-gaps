# Sepsis documentation gap analysis on the synthetic encounter data.
# Compares what the clinical criteria show against what was coded.
# Codes can only come from provider documentation, so a mismatch is flagged
# for CDI review -- it is never a reason to change a code on its own.

import csv
from sepsis_screener_classes import Patient, SepsisProtocol

NUMBER_COLUMNS = ["temp", "HR", "RR", "WBC", "bands", "SBP", "MAP",
                  "lactate", "creatinine", "platelets", "INR", "bilirubin"]
SEPSIS_CODE = "A41.9"
SEVERE_CODES = ("R65.20", "R65.21")

protocol = SepsisProtocol()


def load_encounters(path):
    encounters = []
    with open(path) as f:
        for row in csv.DictReader(f):
            numbers = {col: float(row[col]) for col in NUMBER_COLUMNS}
            patient = Patient(row["encounter_id"], row["infection"], **numbers)
            codes = row["dx_codes"].split(";") if row["dx_codes"] else []
            encounters.append({"patient": patient, "unit": row["unit"], "codes": codes})
    return encounters


def find_gap(e):
    # Returns (category, description) or None if criteria and codes agree
    p = e["patient"]
    codes = e["codes"]
    severe_met = protocol.is_severe_sepsis(p)
    sepsis_met = protocol.is_sepsis(p)
    severe_coded = any(c in codes for c in SEVERE_CODES)
    sepsis_coded = SEPSIS_CODE in codes

    # Query opportunities: criteria met, not documented/coded
    if severe_met and not sepsis_coded:
        return ("Query", "Severe sepsis criteria met, no sepsis code")
    if severe_met and not severe_coded:
        return ("Query", "Severe sepsis criteria met, coded as sepsis only")
    if sepsis_met and not sepsis_coded:
        return ("Query", "Sepsis criteria met, no sepsis code")

    # Clinical validation: coded, but criteria not met
    if severe_coded and not severe_met:
        return ("Validation", "Severe sepsis coded, criteria not met")
    if sepsis_coded and not sepsis_met:
        return ("Validation", "Sepsis coded, criteria not met")

    return None


def report(encounters):
    gaps = []
    for e in encounters:
        gap = find_gap(e)
        if gap:
            gaps.append((e, gap))

    queries = [g for g in gaps if g[1][0] == "Query"]
    validations = [g for g in gaps if g[1][0] == "Validation"]

    print("SEPSIS DOCUMENTATION GAP REPORT")
    print(f"Encounters reviewed: {len(encounters)}")
    print(f"Encounters flagged:  {len(gaps)}")
    print()

    print(f"Query opportunities (criteria met, not documented): {len(queries)}")
    print_breakdown(queries)

    print(f"Clinical validation reviews (coded, criteria not met): {len(validations)}")
    print_breakdown(validations)

    print("Flagged encounters by unit:")
    for unit in sorted(set(e["unit"] for e in encounters)):
        unit_total = sum(1 for e in encounters if e["unit"] == unit)
        unit_flags = sum(1 for e, _ in gaps if e["unit"] == unit)
        print(f"  {unit:12} {unit_flags}/{unit_total}")
    print()

    print("Sample encounters for review:")
    for e, (category, description) in gaps[:8]:
        print(f"  {e['patient'].name}  {category:10}  {description}  [{';'.join(e['codes'])}]")


def print_breakdown(group):
    counts = {}
    for _, (_, description) in group:
        counts[description] = counts.get(description, 0) + 1
    for description, count in counts.items():
        print(f"  {count:3}  {description}")
    print()


if __name__ == "__main__":
    encounters = load_encounters("sepsis_encounters.csv")
    report(encounters)
