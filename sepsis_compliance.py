# SEP-1 bundle compliance analysis on the synthetic encounter data.
# Uses the Patient and SepsisProtocol classes for screening.
# Timing is simplified: elements must happen within X hours AFTER time zero.

import csv
from datetime import datetime
from sepsis_screener_classes import Patient, SepsisProtocol

TIME_FORMAT = "%Y-%m-%d %H:%M"
NUMBER_COLUMNS = ["temp", "HR", "RR", "WBC", "bands", "SBP", "MAP",
                  "lactate", "creatinine", "platelets", "INR", "bilirubin"]

protocol = SepsisProtocol()


def parse_time(text):
    # Blank cell = never happened
    return datetime.strptime(text, TIME_FORMAT) if text else None


def hours_after(start, end):
    return (end - start).total_seconds() / 3600


# ---------- Phase 2: load the CSV ----------

def load_encounters(path):
    encounters = []
    with open(path) as f:
        for row in csv.DictReader(f):
            numbers = {col: float(row[col]) for col in NUMBER_COLUMNS}
            patient = Patient(row["encounter_id"], row["infection"], **numbers)
            times = {col: parse_time(row[col]) for col in
                     ["time_zero", "lactate_time", "cultures_time", "abx_time",
                      "fluids_time", "repeat_lactate_time"]}
            encounters.append({"patient": patient, "unit": row["unit"], **times})
    return encounters


# ---------- Phase 3: check each bundle element ----------
# Each check returns "pass", a failure reason, or None (not applicable)

def check_within(t0, t, hours):
    if t is None:
        return "missed"
    if hours_after(t0, t) > hours:
        return "late"
    return "pass"


def check_encounter(e):
    p = e["patient"]
    t0 = e["time_zero"]
    results = {}

    results["Initial lactate (3 hr)"] = check_within(t0, e["lactate_time"], 3)
    results["Antibiotics (3 hr)"] = check_within(t0, e["abx_time"], 3)

    # Cultures must be drawn, and before antibiotics if antibiotics were given
    if e["cultures_time"] is None:
        results["Cultures before antibiotics"] = "missed"
    elif e["abx_time"] and e["cultures_time"] > e["abx_time"]:
        results["Cultures before antibiotics"] = "after antibiotics"
    else:
        results["Cultures before antibiotics"] = "pass"

    # Fluids only apply if hypotensive or lactate >= 4
    if protocol.is_hypotensive(p) or p.lactate >= protocol.LACTATE_FLUIDS:
        results["Fluids 30 mL/kg (3 hr)"] = check_within(t0, e["fluids_time"], 3)
    else:
        results["Fluids 30 mL/kg (3 hr)"] = None

    # Repeat lactate only applies if initial lactate > 2
    if p.lactate > protocol.LACTATE_THRESHOLD:
        results["Repeat lactate (6 hr)"] = check_within(t0, e["repeat_lactate_time"], 6)
    else:
        results["Repeat lactate (6 hr)"] = None

    return results


# ---------- Phase 4: report ----------

def report(encounters):
    severe = [e for e in encounters if protocol.is_severe_sepsis(e["patient"])]
    sepsis_only = [e for e in encounters
                   if protocol.is_sepsis(e["patient"]) and not protocol.is_severe_sepsis(e["patient"])]

    print("SEP-1 BUNDLE COMPLIANCE REPORT")
    print(f"Encounters screened: {len(encounters)}")
    print(f"  Severe sepsis: {len(severe)}")
    print(f"  Sepsis only:   {len(sepsis_only)}")
    print(f"  No sepsis:     {len(encounters) - len(severe) - len(sepsis_only)}")
    print()

    all_results = [(e, check_encounter(e)) for e in severe]
    elements = list(all_results[0][1].keys())

    # Overall: SEP-1 is all-or-none -- every applicable element must pass
    def bundle_passed(results):
        return all(r == "pass" for r in results.values() if r is not None)

    passed = sum(1 for _, r in all_results if bundle_passed(r))
    print(f"Overall bundle compliance (all-or-none): {passed}/{len(severe)} = {passed / len(severe):.0%}")
    print()

    print("By element:")
    for element in elements:
        applicable = [r[element] for _, r in all_results if r[element] is not None]
        ok = applicable.count("pass")
        failures = {}
        for r in applicable:
            if r != "pass":
                failures[r] = failures.get(r, 0) + 1
        fail_text = ", ".join(f"{count} {reason}" for reason, count in failures.items())
        print(f"  {element:30} {ok}/{len(applicable)} = {ok / len(applicable):.0%}   ({fail_text})")
    print()

    print("By unit (all-or-none):")
    units = sorted(set(e["unit"] for e in severe))
    for unit in units:
        unit_results = [r for e, r in all_results if e["unit"] == unit]
        unit_pass = sum(1 for r in unit_results if bundle_passed(r))
        print(f"  {unit:12} {unit_pass}/{len(unit_results)} = {unit_pass / len(unit_results):.0%}")


if __name__ == "__main__":
    encounters = load_encounters("sepsis_encounters.csv")
    report(encounters)
