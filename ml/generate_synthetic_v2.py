"""
SAATHI: Synthetic Data v2 Generation Engine (Realistic Noise, Inconsistency & Delayed Effects)
Generates versioned synthetic data in data/synthetic_v2/ without modifying existing v1 datasets.

Introduces:
1. Non-linear resilience differences across individuals
2. Voluntary check-in reporting bias & increased missingness (~15%)
3. Delayed cumulative strain (lagged recovery deficit)
4. Measurement noise in duty/rest recording
5. Transient acute spikes vs genuine chronic strain
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
from ml.config import (
    PROCESSED_DIR,
    RANDOM_SEED,
    LONGITUDINAL_MONTHS,
    DEPLOYMENT_TYPES,
    LOCATION_CATEGORIES,
    LEAVE_TYPES
)

SYNTHETIC_V2_DIR = Path("data/synthetic_v2")
for sub in ["deployment", "leave", "workload", "wellness", "behavioral"]:
    (SYNTHETIC_V2_DIR / sub).mkdir(parents=True, exist_ok=True)

def generate_synthetic_v2():
    np.random.seed(RANDOM_SEED + 100) # Distinct seed for v2

    personnel_master_path = PROCESSED_DIR / "personnel_master.csv"
    personnel_df = pd.read_csv(personnel_master_path)
    personnel_ids = personnel_df['personnel_id'].tolist()
    n_personnel = len(personnel_ids)

    # Scenarios distribution
    scenario_choices = ['A_STABLE', 'B_HIGH_TEMPO', 'C_EXTENDED_DEPLOYMENT', 'D_CUMULATIVE_STRAIN', 'E_RECOVERY', 'F_RESILIENT_NOISE']
    scenario_probs = [0.50, 0.15, 0.12, 0.10, 0.08, 0.05]
    assigned_scenarios = np.random.choice(scenario_choices, size=n_personnel, p=scenario_probs)
    personnel_scenario_map = dict(zip(personnel_ids, assigned_scenarios))

    month_dates = [datetime(2025, m, 1) for m in range(1, LONGITUDINAL_MONTHS + 1)]

    dep_rows, leave_rows, workload_rows, wellness_rows, behavioral_rows = [], [], [], [], []
    dep_counter, leave_counter = 1, 1

    for p_idx, pid in enumerate(personnel_ids):
        scenario = personnel_scenario_map[pid]
        
        # Individual psychological & physiological traits
        indiv_resilience = np.clip(np.random.normal(3.0, 0.8), 1.0, 5.0)
        indiv_stoicism = np.random.rand() < 0.25 # 25% under-report strain on surveys
        indiv_somatic_sensitivity = np.random.rand() < 0.15 # 15% report high strain under mild sleep deficit
        reporting_compliance = np.clip(np.random.normal(0.85, 0.12), 0.4, 0.98) # Variable checkin compliance

        days_since_leave = np.random.randint(20, 70)
        in_deployment = False
        current_dep_type, current_intensity, current_hardship, current_location = "Routine", 2, 2, "Urban Base"

        prev_duty_hours = 176.0
        prev_workload_score = 30.0
        prev_sleep_quality = 4.0

        # Lagged strain accumulation state
        accumulated_fatigue_debt = 0.0

        for m_idx, m_date in enumerate(month_dates, 1):
            date_str = m_date.strftime("%Y-%m-%d")

            # 1. DEPLOYMENT DYNAMICS WITH REALISTIC JITTER
            if scenario == 'A_STABLE':
                in_deployment = (m_idx in [4, 5]) and (np.random.rand() < 0.35)
                current_dep_type = "Routine"
                current_intensity = np.random.choice([1, 2, 3], p=[0.4, 0.5, 0.1])
                current_hardship = np.random.choice([1, 2], p=[0.7, 0.3])
                current_location = np.random.choice(["Urban Base", "Semi-Urban Outpost"], p=[0.8, 0.2])
            elif scenario == 'B_HIGH_TEMPO':
                in_deployment = (4 <= m_idx <= 8)
                current_dep_type = "High Tempo"
                current_intensity = np.random.choice([3, 4, 5], p=[0.3, 0.5, 0.2])
                current_hardship = np.random.choice([3, 4], p=[0.6, 0.4])
                current_location = np.random.choice(["Semi-Urban Outpost", "Remote/Difficult Terrain"])
            elif scenario == 'C_EXTENDED_DEPLOYMENT':
                in_deployment = (3 <= m_idx <= 9)
                current_dep_type = "Extended"
                current_intensity = np.random.choice([3, 4, 5], p=[0.2, 0.6, 0.2])
                current_hardship = np.random.choice([4, 5], p=[0.5, 0.5])
                current_location = np.random.choice(["Remote/Difficult Terrain", "High Altitude/Extreme"])
            elif scenario == 'D_CUMULATIVE_STRAIN':
                in_deployment = (4 <= m_idx <= 11)
                current_dep_type = np.random.choice(["Extended", "High Tempo"])
                current_intensity = np.random.choice([4, 5], p=[0.4, 0.6])
                current_hardship = np.random.choice([4, 5], p=[0.3, 0.7])
                current_location = np.random.choice(["Remote/Difficult Terrain", "High Altitude/Extreme"])
            elif scenario == 'E_RECOVERY':
                in_deployment = (2 <= m_idx <= 5)
                current_dep_type = "High Tempo" if in_deployment else "Routine"
                current_intensity = 4 if in_deployment else 1
                current_hardship = 4 if in_deployment else 1
                current_location = "Remote/Difficult Terrain" if in_deployment else "Urban Base"
            elif scenario == 'F_RESILIENT_NOISE':
                in_deployment = (6 <= m_idx <= 7)
                current_dep_type = "High Tempo" if in_deployment else "Routine"
                current_intensity = 4 if in_deployment else 2
                current_hardship = 3 if in_deployment else 2
                current_location = "Semi-Urban Outpost" if in_deployment else "Urban Base"

            if in_deployment:
                dep_start = m_date + timedelta(days=np.random.randint(1, 5))
                dep_end = m_date + timedelta(days=np.random.randint(22, 28))
                dep_duration = (dep_end - dep_start).days
                dep_rows.append({
                    "personnel_id": pid,
                    "deployment_id": f"DEP-V2-{dep_counter:07d}",
                    "month_idx": m_idx,
                    "date": date_str,
                    "start_date": dep_start.strftime("%Y-%m-%d"),
                    "end_date": dep_end.strftime("%Y-%m-%d"),
                    "deployment_duration_days": dep_duration,
                    "deployment_type": current_dep_type,
                    "operational_intensity": int(current_intensity),
                    "hardship_level": int(current_hardship),
                    "recovery_required": bool((current_intensity >= 4) or (current_hardship >= 4)),
                    "location_category": current_location
                })
                dep_counter += 1

            # 2. LEAVE WITH OCCASIONAL CANCELATIONS
            days_since_leave += 30
            took_leave = False
            leave_duration = 0
            leave_type = "None"

            if scenario == 'E_RECOVERY' and m_idx == 6:
                took_leave = True
                leave_duration = np.random.randint(12, 18)
                leave_type = "Recovery"
            elif scenario == 'D_CUMULATIVE_STRAIN':
                if days_since_leave > 150 and np.random.rand() < 0.25:
                    took_leave = True
                    leave_duration = np.random.randint(3, 6)
                    leave_type = "Casual"
            elif in_deployment:
                if days_since_leave > 120 and np.random.rand() < 0.15:
                    took_leave = True
                    leave_duration = np.random.randint(3, 7)
                    leave_type = "Casual"
            else:
                if days_since_leave >= 60 and np.random.rand() < 0.40:
                    took_leave = True
                    leave_duration = np.random.randint(6, 14)
                    leave_type = np.random.choice(["Annual", "Casual", "Medical/Authorized"], p=[0.6, 0.3, 0.1])

            if took_leave:
                l_start = m_date + timedelta(days=np.random.randint(4, 10))
                l_end = l_start + timedelta(days=leave_duration)
                leave_rows.append({
                    "personnel_id": pid,
                    "leave_id": f"LV-V2-{leave_counter:07d}",
                    "month_idx": m_idx,
                    "date": date_str,
                    "leave_start_date": l_start.strftime("%Y-%m-%d"),
                    "leave_end_date": l_end.strftime("%Y-%m-%d"),
                    "duration_days": int(leave_duration),
                    "leave_type": leave_type,
                    "days_since_previous_leave": int(days_since_leave)
                })
                leave_counter += 1
                days_since_leave = 0

            # 3. WORKLOAD WITH MEASUREMENT NOISE & JITTER
            # Add Gaussian telemetry noise (+/- 6 hrs)
            meas_noise = np.random.normal(0, 6.0)
            if in_deployment:
                duty_hrs = 210 + (current_intensity * 7.0) + meas_noise
                ot_hrs = np.clip(np.random.normal(28 + current_intensity * 3, 7), 5, 65)
                night_shifts = int(np.clip(np.random.poisson(2 + current_intensity), 1, 14))
                consec_days = int(np.clip(np.random.normal(7 + current_intensity, 2), 4, 18))
                rest_hrs = np.clip(75 - (ot_hrs * 0.4) + np.random.normal(0, 5), 25, 95)
                sched_irreg = np.clip(np.random.normal(2.5 + current_intensity * 0.4, 0.4), 1.0, 5.0)
            else:
                duty_hrs = 176 + meas_noise
                ot_hrs = np.clip(np.random.normal(6, 4), 0, 22)
                night_shifts = int(np.clip(np.random.poisson(2), 0, 5))
                consec_days = int(np.clip(np.random.normal(5, 1), 3, 7))
                rest_hrs = np.clip(95 - (ot_hrs * 0.3) + np.random.normal(0, 4), 65, 120)
                sched_irreg = np.clip(np.random.normal(1.4, 0.3), 1.0, 3.0)

            # Cumulative fatigue debt accumulation
            if duty_hrs > 220 or night_shifts >= 6:
                accumulated_fatigue_debt += 0.8 / indiv_resilience
            else:
                accumulated_fatigue_debt = max(0.0, accumulated_fatigue_debt - 0.5 * (1.0 if took_leave else 0.2))

            raw_workload = (
                ((duty_hrs - 160) / 100.0) * 35.0 +
                (ot_hrs / 60.0) * 25.0 +
                (night_shifts / 12.0) * 20.0 +
                (consec_days / 15.0) * 10.0 +
                ((sched_irreg - 1.0) / 4.0) * 10.0 -
                ((rest_hrs - 40.0) / 80.0) * 15.0 + 15.0 +
                np.random.normal(0, 3.0) # Workload scoring variance
            )
            workload_score = float(np.clip(raw_workload, 5.0, 98.0))

            workload_rows.append({
                "personnel_id": pid,
                "date": date_str,
                "month_idx": m_idx,
                "duty_hours": round(float(duty_hrs), 1),
                "overtime_hours": round(float(ot_hrs), 1),
                "night_shifts": int(night_shifts),
                "consecutive_duty_days": int(consec_days),
                "rest_hours": round(float(rest_hrs), 1),
                "workload_score": round(workload_score, 1),
                "operational_intensity": int(current_intensity),
                "schedule_irregularity": round(float(sched_irreg), 2)
            })

            # 4. VOLUNTARY WELLNESS WITH REALISTIC MISSINGNESS & REPORTING BIAS
            checkin_completed = np.random.rand() < reporting_compliance

            # Base latent wellness modulated by individual traits
            sq_true = np.clip(4.2 - (accumulated_fatigue_debt * 0.4) - (night_shifts * 0.15) + np.random.normal(0, 0.4), 1.0, 5.0)
            fl_true = np.clip(1.5 + (accumulated_fatigue_debt * 0.6) + (ot_hrs * 0.03) + np.random.normal(0, 0.4), 1.0, 5.0)
            srs_true = np.clip(1.5 + (accumulated_fatigue_debt * 0.5) + ((5.0 - indiv_resilience) * 0.3) + np.random.normal(0, 0.4), 1.0, 5.0)

            # Apply reporting bias (stoicism vs somatic sensitivity)
            srs_reported = srs_true - (0.8 if indiv_stoicism else 0.0) + (0.7 if indiv_somatic_sensitivity else 0.0)
            srs_reported = np.clip(srs_reported, 1.0, 5.0)

            wellness_rows.append({
                "personnel_id": pid,
                "date": date_str,
                "month_idx": m_idx,
                "sleep_quality": round(float(sq_true), 1) if checkin_completed else np.nan,
                "fatigue_level": round(float(fl_true), 1) if checkin_completed else np.nan,
                "work_stress": round(float(np.clip(srs_reported * 0.9 + np.random.normal(0, 0.3), 1.0, 5.0)), 1) if checkin_completed else np.nan,
                "mood_wellbeing": round(float(np.clip(5.5 - srs_reported * 0.8 + np.random.normal(0, 0.3), 1.0, 5.0)), 1) if checkin_completed else np.nan,
                "work_life_balance": round(float(np.clip(5.0 - (ot_hrs * 0.05) + np.random.normal(0, 0.3), 1.0, 5.0)), 1) if checkin_completed else np.nan,
                "job_satisfaction": round(float(np.clip(4.0 - (accumulated_fatigue_debt * 0.2) + np.random.normal(0, 0.3), 1.0, 5.0)), 1) if checkin_completed else np.nan,
                "recovery_quality": round(float(np.clip((rest_hrs / 25.0) + np.random.normal(0, 0.3), 1.0, 5.0)), 1) if checkin_completed else np.nan,
                "self_reported_strain": round(float(srs_reported), 1) if checkin_completed else np.nan,
                "checkin_completion": bool(checkin_completed)
            })

            # 5. BEHAVIORAL CHANGES WITH UNOBSERVED NOISE
            duty_change = (duty_hrs - prev_duty_hours) / max(prev_duty_hours, 1.0)
            workload_delta = (workload_score - prev_workload_score) / max(prev_workload_score, 1.0)
            sleep_delta = (sq_true - prev_sleep_quality) / max(prev_sleep_quality, 1.0)

            att_change = -1.0 * max(0.0, float(duty_change * 0.25 + np.random.normal(0, 0.08)))
            lv_freq_change = 0.2 if took_leave else -0.1
            perf_change = np.clip(float(sleep_delta * 0.3 - duty_change * 0.15 + np.random.normal(0, 0.1)), -0.5, 0.5)
            sched_change = float((sched_irreg - 1.5) / 3.5 + np.random.normal(0, 0.05))
            rec_change = float((rest_hrs - 85.0) / 45.0 + np.random.normal(0, 0.05))
            routine_dev = float(np.clip(abs(duty_change) * 0.4 + abs(sched_change) * 0.4 + np.random.uniform(0, 0.15), 0.0, 1.0))

            behavioral_rows.append({
                "personnel_id": pid,
                "date": date_str,
                "month_idx": m_idx,
                "attendance_change": round(att_change, 3),
                "leave_frequency_change": round(lv_freq_change, 3),
                "workload_change": round(workload_delta, 3),
                "sleep_change": round(sleep_delta, 3),
                "routine_deviation": round(routine_dev, 3),
                "performance_change": round(perf_change, 3),
                "schedule_change": round(sched_change, 3),
                "recovery_change": round(rec_change, 3)
            })

            prev_duty_hours = duty_hrs
            prev_workload_score = workload_score
            prev_sleep_quality = sq_true

    pd.DataFrame(dep_rows).to_csv(SYNTHETIC_V2_DIR / "deployment/deployment_records.csv", index=False)
    pd.DataFrame(leave_rows).to_csv(SYNTHETIC_V2_DIR / "leave/leave_history.csv", index=False)
    pd.DataFrame(workload_rows).to_csv(SYNTHETIC_V2_DIR / "workload/workload_records.csv", index=False)
    pd.DataFrame(wellness_rows).to_csv(SYNTHETIC_V2_DIR / "wellness/wellness_surveys.csv", index=False)
    pd.DataFrame(behavioral_rows).to_csv(SYNTHETIC_V2_DIR / "behavioral/behavioral_records.csv", index=False)

    print(f"[✓] Synthetic v2 data successfully generated in {SYNTHETIC_V2_DIR}")

if __name__ == "__main__":
    generate_synthetic_v2()
