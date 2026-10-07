# Generates a synthetic dataset of adult encounters for SEP-1 compliance analysis.
# All data is fake. Thresholds match the SepsisProtocol class (CMS SEP-1 criteria).

import csv
import random
from datetime import datetime, timedelta
 
random.seed(42)  # same "random" data every run, so results are reproducible
code_rng = random.Random(7)
bundle_rng = random.Random(11)  # separate generator for bundle timing  # separate generator for diagnosis codes, so adding codes doesn't change the other data

NUM_ENCOUNTERS = 300
UNITS = ["Med/Surg A", "Med/Surg B", "Telemetry", "Step-Down"]
START_DATE = datetime(2026, 1, 1)
END_DATE = datetime(2026, 6, 30)
TIME_FORMAT = "%Y-%m-%d %H:%M"


# ---------- Helpers for normal vs. abnormal values ----------

def rand(low, high, decimals=1):
    return round(random.uniform(low, high), decimals)


def make_sirs(num_abnormal):
    # Pick which SIRS criteria will be abnormal
    abnormal = random.sample(["temp", "HR", "RR", "WBC"], num_abnormal)

    if "temp" in abnormal:
        temp = rand(101.2, 103.5) if random.random() < 0.8 else rand(95.0, 96.5)
    else:
        temp = rand(97.5, 100.0)

    HR = random.randint(92, 135) if "HR" in abnormal else random.randint(65, 88)
    RR = random.randint(22, 32) if "RR" in abnormal else random.randint(12, 19)

    if "WBC" in abnormal:
        pick = random.choice(["high", "low", "bands"])
        if pick == "high":
            WBC, bands = random.randint(12500, 24000), random.randint(0, 8)
        elif pick == "low":
            WBC, bands = random.randint(2000, 3800), random.randint(0, 8)
        else:
            WBC, bands = random.randint(5000, 11000), random.randint(11, 20)
    else:
        WBC, bands = random.randint(5000, 11000), random.randint(0, 8)

    return {"temp": temp, "HR": HR, "RR": RR, "WBC": WBC, "bands": bands}


def make_organ(abnormal):
    # abnormal is a list of organ dysfunction signs to include
    labs = {}
    if "hypotension" in abnormal:
        labs["SBP"], labs["MAP"] = random.randint(75, 89), random.randint(50, 64)
    else:
        labs["SBP"], labs["MAP"] = random.randint(100, 140), random.randint(70, 95)

    if "lactate_high" in abnormal:
        labs["lactate"] = rand(4.0, 7.5)
    elif "lactate" in abnormal:
        labs["lactate"] = rand(2.1, 3.9)
    else:
        labs["lactate"] = rand(0.6, 1.9)

    labs["creatinine"] = rand(2.1, 3.5) if "creatinine" in abnormal else rand(0.6, 1.4)

    if "coag" in abnormal:
        labs["platelets"], labs["INR"] = random.randint(50000, 95000), rand(1.6, 2.4)
    else:
        labs["platelets"], labs["INR"] = random.randint(150000, 350000), rand(0.9, 1.3)

    labs["bilirubin"] = rand(2.1, 4.0) if "bilirubin" in abnormal else rand(0.3, 1.2)
    return labs


def random_time_zero():
    total_minutes = int((END_DATE - START_DATE).total_seconds() // 60)
    return START_DATE + timedelta(minutes=random.randint(0, total_minutes))


def fmt(t):
    # Blank string = the bundle element never happened
    return t.strftime(TIME_FORMAT) if t else ""


# ---------- Bundle timestamps for severe sepsis cases ----------

def minutes_with_tail(rng, on_time_share, on_time_range, late_range):
    # Most cases land inside the window; a realistic share run late
    if rng.random() < on_time_share:
        return rng.randint(*on_time_range)
    return rng.randint(*late_range)


def make_bundle_times(time_zero, labs):
    # Uses its own random generator, so tuning these delays never changes the patients
    rng = bundle_rng
    times = {}

    # Initial lactate: almost always drawn, usually within 3 hours
    if rng.random() < 0.97:
        times["lactate_time"] = time_zero + timedelta(minutes=minutes_with_tail(rng, 0.92, (5, 150), (185, 300)))
    else:
        times["lactate_time"] = None

    # Antibiotics: almost always given, most within 3 hours
    if rng.random() < 0.98:
        abx = time_zero + timedelta(minutes=minutes_with_tail(rng, 0.86, (15, 170), (185, 320)))
    else:
        abx = None
    times["abx_time"] = abx

    # Blood cultures: usually before antibiotics, occasionally after or missed
    roll = rng.random()
    if abx and roll < 0.92:
        times["cultures_time"] = abx - timedelta(minutes=rng.randint(5, 60))
    elif abx and roll < 0.97:
        times["cultures_time"] = abx + timedelta(minutes=rng.randint(10, 90))  # after abx = fail
    elif not abx and roll < 0.95:
        times["cultures_time"] = time_zero + timedelta(minutes=rng.randint(10, 120))
    else:
        times["cultures_time"] = None

    # Fluids: only expected if hypotensive or lactate >= 4
    needs_fluids = labs["SBP"] < 90 or labs["MAP"] < 65 or labs["lactate"] >= 4
    if needs_fluids and rng.random() < 0.95:
        times["fluids_time"] = time_zero + timedelta(minutes=minutes_with_tail(rng, 0.88, (10, 170), (185, 300)))
    else:
        times["fluids_time"] = None

    # Repeat lactate: only expected if initial lactate > 2
    if labs["lactate"] > 2 and rng.random() < 0.90:
        times["repeat_lactate_time"] = time_zero + timedelta(minutes=minutes_with_tail(rng, 0.88, (120, 350), (370, 540)))
    else:
        times["repeat_lactate_time"] = None

    return times


# ---------- Diagnosis codes (what was documented and coded) ----------
# A41.9  = sepsis, unspecified organism
# R65.20 = severe sepsis without septic shock
# R65.21 = severe sepsis with septic shock
# Infection source codes: J18.9 pneumonia, N39.0 UTI, L03.90 cellulitis

INFECTION_CODES = ["J18.9", "N39.0", "L03.90"]


def make_codes(case, infection, labs):
    codes = []
    if infection in ("known", "suspected"):
        codes.append(code_rng.choice(INFECTION_CODES))

    roll = code_rng.random()
    if case == "severe":
        if roll < 0.70:
            # Documented and coded correctly
            shock = labs["lactate"] >= 4 or labs["SBP"] < 90 or labs["MAP"] < 65
            codes += ["A41.9", "R65.21" if shock and code_rng.random() < 0.3 else "R65.20"]
        elif roll < 0.92:
            codes.append("A41.9")  # sepsis documented, severity missing
        # else: sepsis never documented at all
    elif case == "sepsis":
        if roll < 0.85:
            codes.append("A41.9")
        elif roll < 0.95:
            codes += ["A41.9", "R65.20"]  # severe sepsis coded without support
        # else: sepsis never documented
    else:
        if roll < 0.08:
            codes.append("A41.9")  # sepsis coded without support

    return ";".join(codes)


# ---------- Build one encounter ----------

def make_encounter(encounter_id):
    roll = random.random()

    if roll < 0.45:
        case = "severe"
    elif roll < 0.70:
        case = "sepsis"
    else:
        case = "none"

    if case == "severe":
        infection = random.choice(["known", "suspected"])
        sirs = make_sirs(random.randint(2, 4))
        signs = random.sample(["hypotension", "lactate", "lactate_high",
                               "creatinine", "coag", "bilirubin"], random.randint(1, 3))
        if "lactate" in signs and "lactate_high" in signs:
            signs.remove("lactate")
        labs = make_organ(signs)
    elif case == "sepsis":
        infection = random.choice(["known", "suspected"])
        sirs = make_sirs(random.randint(2, 4))
        labs = make_organ([])
    else:
        # Either no infection, or infection with fewer than 2 SIRS
        if random.random() < 0.5:
            infection = "none"
            sirs = make_sirs(random.randint(0, 4))
        else:
            infection = random.choice(["known", "suspected"])
            sirs = make_sirs(random.randint(0, 1))
        labs = make_organ([])

    row = {
        "encounter_id": encounter_id,
        "unit": random.choice(UNITS),
        "infection": infection,
        **sirs,
        **labs,
        "dx_codes": make_codes(case, infection, labs),
    }

    # Only severe sepsis cases get a time zero and bundle timestamps
    if case == "severe":
        time_zero = random_time_zero()
        times = make_bundle_times(time_zero, labs)
        row["time_zero"] = fmt(time_zero)
        for key, value in times.items():
            row[key] = fmt(value)
    else:
        for key in ["time_zero", "lactate_time", "cultures_time", "abx_time",
                    "fluids_time", "repeat_lactate_time"]:
            row[key] = ""

    return row


# ---------- Write the CSV ----------

COLUMNS = ["encounter_id", "unit", "infection",
           "temp", "HR", "RR", "WBC", "bands",
           "SBP", "MAP", "lactate", "creatinine", "platelets", "INR", "bilirubin",
           "time_zero", "lactate_time", "cultures_time", "abx_time",
           "fluids_time", "repeat_lactate_time", "dx_codes"]

with open("sepsis_encounters.csv", "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=COLUMNS)
    writer.writeheader()
    for i in range(NUM_ENCOUNTERS):
        writer.writerow(make_encounter(1001 + i))

print(f"Wrote {NUM_ENCOUNTERS} encounters to sepsis_encounters.csv")
