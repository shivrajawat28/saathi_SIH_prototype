"""
SAATHI: Synthetic Longitudinal Scenario Engine
Generates privacy-preserving, scientifically defensible synthetic datasets across 12 months for 1,470 personnel.
Implements 6 distinct occupational scenarios with realistic cross-signal coherence.

Datasets Generated:
1. data/synthetic/deployment/deployment_records.csv
2. data/synthetic/leave/leave_history.csv
3. data/synthetic/workload/workload_records.csv
4. data/synthetic/wellness/wellness_surveys.csv
5. data/synthetic/behavioral/behavioral_records.csv
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
from ml.config import (
    PROCESSED_DIR,
    SYNTHETIC_DIR,
    RANDOM_SEED,
    LONGITUDINAL_MONTHS,
    DEPLOYMENT_TYPES,
    LOCATION_CATEGORIES,
    LEAVE_TYPES
)

def generate_synthetic_longitudinal_data():
    np.random.seed(RANDOM_SEED)

    personnel_master_path = PROCESSED_DIR / "personnel_master.csv"
    if not personnel_master_path.exists():
        raise FileNotFoundError(f"Personnel master dataset not found at {personnel_master_path}. Run create_personnel_master first.")

    personnel_df = pd.read_csv(personnel_master_path)
    personnel_ids = personnel_df['personnel_id'].tolist()
    n_personnel = len(personnel_ids)

    # 1. Assign Personnel Scenarios
    # Scenario A (Stable): 50%
    # Scenario B (High Tempo): 15%
    # Scenario C (Extended Deployment): 12%
    # Scenario D (Cumulative Strain): 10%
    # Scenario E (Recovery / Rebound): 8%
    # Scenario F (Resilient Noise / False-Alarm Resistance): 5%
    scenario_choices = ['A_STABLE', 'B_HIGH_TEMPO', 'C_EXTENDED_DEPLOYMENT', 'D_CUMULATIVE_STRAIN', 'E_RECOVERY', 'F_RESILIENT_NOISE']
    scenario_probs = [0.50, 0.15, 0.12, 0.10, 0.08, 0.05]
    
    assigned_scenarios = np.random.choice(scenario_choices, size=n_personnel, p=scenario_probs)
    personnel_scenario_map = dict(zip(personnel_ids, assigned_scenarios))

    # Base dates for 12 monthly periods (2025-01 to 2025-12)
    month_dates = [datetime(2025, m, 1) for m in range(1, LONGITUDINAL_MONTHS + 1)]

    # Storage for datasets
    deployment_rows = []
    leave_rows = []
    workload_rows = []
    wellness_rows = []
    behavioral_rows = []

    dep_counter = 1
    leave_counter = 1

    for p_idx, pid in enumerate(personnel_ids):
        scenario = personnel_scenario_map[pid]
        p_row = personnel_df.iloc[p_idx]
        
        # Individual baseline tendencies (for realistic individual variation)
        indiv_workload_bias = np.random.normal(0, 5.0)
        indiv_sleep_bias = np.random.normal(0, 0.3)
        indiv_resilience = np.clip(np.random.normal(3.0, 0.5), 1.0, 5.0)

        # Track longitudinal state across months
        days_since_leave = np.random.randint(15, 60)
        last_leave_date = datetime(2024, 11, 15) + timedelta(days=np.random.randint(0, 45))
        
        in_deployment = False
        dep_start_date = None
        dep_end_date = None
        current_dep_type = "Routine"
        current_intensity = 2
        current_hardship = 2
        current_location = "Urban Base"

        # Baseline stats for behavioral change tracking
        prev_duty_hours = 176.0
        prev_night_shifts = 2
        prev_sleep_quality = 4.0
        prev_workload_score = 30.0

        for m_idx, m_date in enumerate(month_dates, 1):
            date_str = m_date.strftime("%Y-%m-%d")

            # -------------------------------------------------------------
            # 1. DEPLOYMENT DYNAMICS
            # -------------------------------------------------------------
            # Determine deployment state for the month based on scenario
            if scenario == 'A_STABLE':
                # Occasional routine deployment
                if m_idx in [4, 5] and np.random.rand() < 0.4:
                    in_deployment = True
                    current_dep_type = "Routine"
                    current_intensity = np.random.randint(2, 4)
                    current_hardship = np.random.randint(1, 3)
                    current_location = np.random.choice(["Urban Base", "Semi-Urban Outpost"])
                else:
                    in_deployment = False
                    current_dep_type = "Routine"
                    current_intensity = 2
                    current_hardship = 1
                    current_location = "Urban Base"

            elif scenario == 'B_HIGH_TEMPO':
                # High tempo operations in months 4-8
                if 4 <= m_idx <= 8:
                    in_deployment = True
                    current_dep_type = "High Tempo"
                    current_intensity = np.random.randint(3, 5)
                    current_hardship = np.random.randint(3, 5)
                    current_location = np.random.choice(["Semi-Urban Outpost", "Remote/Difficult Terrain"])
                else:
                    in_deployment = False
                    current_dep_type = "Routine"
                    current_intensity = 2
                    current_hardship = 2
                    current_location = "Urban Base"

            elif scenario == 'C_EXTENDED_DEPLOYMENT':
                # Long continuous deployment months 3-9
                if 3 <= m_idx <= 9:
                    in_deployment = True
                    current_dep_type = "Extended"
                    current_intensity = np.random.randint(3, 5)
                    current_hardship = np.random.randint(4, 6)
                    current_location = np.random.choice(["Remote/Difficult Terrain", "High Altitude/Extreme"])
                else:
                    in_deployment = False
                    current_dep_type = "Routine"
                    current_intensity = 2
                    current_hardship = 2
                    current_location = "Urban Base"

            elif scenario == 'D_CUMULATIVE_STRAIN':
                # Sustained difficult deployments months 4-11
                if 4 <= m_idx <= 11:
                    in_deployment = True
                    current_dep_type = np.random.choice(["Extended", "High Tempo"])
                    current_intensity = np.random.randint(4, 6)
                    current_hardship = np.random.randint(4, 6)
                    current_location = np.random.choice(["Remote/Difficult Terrain", "High Altitude/Extreme"])
                else:
                    in_deployment = False
                    current_dep_type = "Routine"
                    current_intensity = 2
                    current_hardship = 2
                    current_location = "Semi-Urban Outpost"

            elif scenario == 'E_RECOVERY':
                # Heavy deployment early (months 2-5), then stationed at base
                if 2 <= m_idx <= 5:
                    in_deployment = True
                    current_dep_type = "High Tempo"
                    current_intensity = 4
                    current_hardship = 4
                    current_location = "Remote/Difficult Terrain"
                else:
                    in_deployment = False
                    current_dep_type = "Routine"
                    current_intensity = 1
                    current_hardship = 1
                    current_location = "Urban Base"

            elif scenario == 'F_RESILIENT_NOISE':
                # Temporary operational surge in months 6-7
                if 6 <= m_idx <= 7:
                    in_deployment = True
                    current_dep_type = "High Tempo"
                    current_intensity = 4
                    current_hardship = 3
                    current_location = "Semi-Urban Outpost"
                else:
                    in_deployment = False
                    current_dep_type = "Routine"
                    current_intensity = 2
                    current_hardship = 2
                    current_location = "Urban Base"

            # Create deployment record if deployed this month
            if in_deployment:
                dep_start = m_date + timedelta(days=np.random.randint(1, 5))
                dep_end = m_date + timedelta(days=np.random.randint(22, 28))
                dep_duration = (dep_end - dep_start).days
                recovery_req = (current_intensity >= 4) or (current_hardship >= 4)

                deployment_rows.append({
                    "personnel_id": pid,
                    "deployment_id": f"DEP-{dep_counter:07d}",
                    "month_idx": m_idx,
                    "date": date_str,
                    "start_date": dep_start.strftime("%Y-%m-%d"),
                    "end_date": dep_end.strftime("%Y-%m-%d"),
                    "deployment_duration_days": dep_duration,
                    "deployment_type": current_dep_type,
                    "operational_intensity": int(current_intensity),
                    "hardship_level": int(current_hardship),
                    "recovery_required": bool(recovery_req),
                    "location_category": current_location
                })
                dep_counter += 1

            # -------------------------------------------------------------
            # 2. LEAVE PATTERNS
            # -------------------------------------------------------------
            days_since_leave += 30
            took_leave = False
            leave_duration = 0
            leave_type = "None"

            # Determine if leave is taken this month
            if scenario == 'E_RECOVERY' and m_idx == 6:
                # Mandatory recovery leave in month 6
                took_leave = True
                leave_duration = np.random.randint(12, 18)
                leave_type = "Recovery"
            elif scenario == 'D_CUMULATIVE_STRAIN':
                # Severely delayed leave
                if days_since_leave > 160 and np.random.rand() < 0.3:
                    took_leave = True
                    leave_duration = np.random.randint(3, 7)
                    leave_type = "Casual"
            elif scenario in ['B_HIGH_TEMPO', 'C_EXTENDED_DEPLOYMENT'] and in_deployment:
                # Less leave during active deployment
                if days_since_leave > 120 and np.random.rand() < 0.2:
                    took_leave = True
                    leave_duration = np.random.randint(4, 8)
                    leave_type = "Casual"
            else:
                # Regular leave cycle (every 60-90 days)
                if days_since_leave >= 60 and np.random.rand() < 0.45:
                    took_leave = True
                    leave_duration = np.random.randint(7, 14)
                    leave_type = np.random.choice(["Annual", "Casual", "Medical/Authorized"], p=[0.55, 0.35, 0.10])

            if took_leave:
                l_start = m_date + timedelta(days=np.random.randint(5, 12))
                l_end = l_start + timedelta(days=leave_duration)
                leave_rows.append({
                    "personnel_id": pid,
                    "leave_id": f"LV-{leave_counter:07d}",
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

            # -------------------------------------------------------------
            # 3. WORKLOAD RECORDS
            # -------------------------------------------------------------
            # Base monthly duty hours ~176 (22 days * 8 hours)
            if scenario == 'A_STABLE':
                duty_hrs = 176 + indiv_workload_bias + np.random.normal(0, 4)
                ot_hrs = np.clip(np.random.normal(6, 3), 0, 18)
                night_shifts = int(np.clip(np.random.poisson(2), 0, 4))
                consec_days = int(np.clip(np.random.normal(5, 1), 3, 7))
                rest_hrs = np.clip(95 - (ot_hrs * 0.5) + np.random.normal(0, 3), 75, 115)
                op_int = current_intensity
                sched_irreg = np.clip(np.random.normal(1.5, 0.3), 1.0, 3.0)

            elif scenario == 'B_HIGH_TEMPO':
                if 4 <= m_idx <= 8:
                    duty_hrs = 215 + indiv_workload_bias + np.random.normal(0, 6)
                    ot_hrs = np.clip(np.random.normal(32, 6), 18, 55)
                    night_shifts = int(np.clip(np.random.poisson(6), 4, 10))
                    consec_days = int(np.clip(np.random.normal(9, 2), 6, 13))
                    rest_hrs = np.clip(60 - (ot_hrs * 0.4) + np.random.normal(0, 4), 40, 75)
                    op_int = current_intensity
                    sched_irreg = np.clip(np.random.normal(3.8, 0.4), 2.5, 5.0)
                else:
                    duty_hrs = 180 + indiv_workload_bias + np.random.normal(0, 4)
                    ot_hrs = np.clip(np.random.normal(10, 4), 0, 20)
                    night_shifts = int(np.clip(np.random.poisson(2), 1, 4))
                    consec_days = int(np.clip(np.random.normal(5, 1), 3, 7))
                    rest_hrs = np.clip(90 - (ot_hrs * 0.4), 70, 105)
                    op_int = 2
                    sched_irreg = np.clip(np.random.normal(1.8, 0.3), 1.0, 3.0)

            elif scenario == 'C_EXTENDED_DEPLOYMENT':
                if 3 <= m_idx <= 9:
                    duty_hrs = 225 + indiv_workload_bias + np.random.normal(0, 5)
                    ot_hrs = np.clip(np.random.normal(38, 5), 20, 58)
                    night_shifts = int(np.clip(np.random.poisson(7), 4, 11))
                    consec_days = int(np.clip(np.random.normal(10, 2), 7, 14))
                    rest_hrs = np.clip(55 - (ot_hrs * 0.3), 35, 70)
                    op_int = current_intensity
                    sched_irreg = np.clip(np.random.normal(4.0, 0.3), 3.0, 5.0)
                else:
                    duty_hrs = 178 + indiv_workload_bias + np.random.normal(0, 4)
                    ot_hrs = np.clip(np.random.normal(8, 3), 0, 18)
                    night_shifts = int(np.clip(np.random.poisson(2), 0, 4))
                    consec_days = int(np.clip(np.random.normal(5, 1), 3, 7))
                    rest_hrs = np.clip(92 - (ot_hrs * 0.4), 75, 110)
                    op_int = 2
                    sched_irreg = np.clip(np.random.normal(1.8, 0.3), 1.0, 3.0)

            elif scenario == 'D_CUMULATIVE_STRAIN':
                if m_idx < 4:
                    duty_hrs = 188 + indiv_workload_bias + np.random.normal(0, 5)
                    ot_hrs = np.clip(np.random.normal(15, 4), 5, 25)
                    night_shifts = int(np.clip(np.random.poisson(3), 1, 5))
                    consec_days = int(np.clip(np.random.normal(6, 1), 4, 8))
                    rest_hrs = np.clip(82 - (ot_hrs * 0.4), 65, 95)
                    op_int = 3
                    sched_irreg = np.clip(np.random.normal(2.5, 0.4), 1.5, 3.5)
                else:
                    # Escalating strain across months 4-11
                    escalation = min((m_idx - 3) * 4.0, 30.0)
                    duty_hrs = 230 + escalation + indiv_workload_bias + np.random.normal(0, 5)
                    ot_hrs = np.clip(np.random.normal(42 + (escalation * 0.4), 5), 25, 65)
                    night_shifts = int(np.clip(np.random.poisson(8 + int(escalation * 0.1)), 5, 14))
                    consec_days = int(np.clip(np.random.normal(11, 2), 7, 16))
                    rest_hrs = np.clip(45 - (escalation * 0.3) + np.random.normal(0, 3), 25, 60)
                    op_int = 5
                    sched_irreg = np.clip(np.random.normal(4.5, 0.3), 3.5, 5.0)

            elif scenario == 'E_RECOVERY':
                if 2 <= m_idx <= 5:
                    duty_hrs = 220 + indiv_workload_bias + np.random.normal(0, 5)
                    ot_hrs = np.clip(np.random.normal(35, 5), 20, 50)
                    night_shifts = int(np.clip(np.random.poisson(6), 4, 10))
                    consec_days = int(np.clip(np.random.normal(9, 2), 6, 13))
                    rest_hrs = np.clip(58 - (ot_hrs * 0.3), 40, 75)
                    op_int = 4
                    sched_irreg = np.clip(np.random.normal(3.8, 0.4), 2.5, 5.0)
                elif m_idx == 6:
                    # Recovery leave month
                    duty_hrs = 120 + indiv_workload_bias
                    ot_hrs = 0.0
                    night_shifts = 0
                    consec_days = 3
                    rest_hrs = 120.0
                    op_int = 1
                    sched_irreg = 1.0
                else:
                    # Post-recovery stabilized operation
                    duty_hrs = 172 + indiv_workload_bias + np.random.normal(0, 4)
                    ot_hrs = np.clip(np.random.normal(5, 2), 0, 12)
                    night_shifts = int(np.clip(np.random.poisson(1), 0, 3))
                    consec_days = int(np.clip(np.random.normal(5, 1), 3, 6))
                    rest_hrs = np.clip(98 - (ot_hrs * 0.4), 85, 115)
                    op_int = 1
                    sched_irreg = np.clip(np.random.normal(1.3, 0.2), 1.0, 2.0)

            elif scenario == 'F_RESILIENT_NOISE':
                if 6 <= m_idx <= 7:
                    duty_hrs = 210 + indiv_workload_bias + np.random.normal(0, 5)
                    ot_hrs = np.clip(np.random.normal(26, 4), 15, 40)
                    night_shifts = int(np.clip(np.random.poisson(5), 3, 8))
                    consec_days = int(np.clip(np.random.normal(8, 1), 5, 10))
                    rest_hrs = np.clip(70 - (ot_hrs * 0.3), 50, 85)
                    op_int = 4
                    sched_irreg = np.clip(np.random.normal(3.0, 0.3), 2.0, 4.0)
                else:
                    duty_hrs = 176 + indiv_workload_bias + np.random.normal(0, 4)
                    ot_hrs = np.clip(np.random.normal(7, 3), 0, 15)
                    night_shifts = int(np.clip(np.random.poisson(2), 0, 4))
                    consec_days = int(np.clip(np.random.normal(5, 1), 3, 7))
                    rest_hrs = np.clip(92 - (ot_hrs * 0.4), 75, 110)
                    op_int = 2
                    sched_irreg = np.clip(np.random.normal(1.5, 0.3), 1.0, 2.5)

            # Calculate deterministic multi-component Workload Score (0-100)
            # Higher duty hours, overtime, night shifts, consecutive days, schedule irregularity -> higher score
            # Higher rest hours -> lower score
            raw_workload = (
                ((duty_hrs - 160) / 100.0) * 35.0 +
                (ot_hrs / 60.0) * 25.0 +
                (night_shifts / 12.0) * 20.0 +
                (consec_days / 15.0) * 10.0 +
                ((sched_irreg - 1.0) / 4.0) * 10.0 -
                ((rest_hrs - 40.0) / 80.0) * 15.0 + 15.0
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
                "operational_intensity": int(op_int),
                "schedule_irregularity": round(float(sched_irreg), 2)
            })

            # -------------------------------------------------------------
            # 4. WELLNESS SURVEYS (VOLUNTARY CHECK-INS)
            # -------------------------------------------------------------
            # Check-in completion rate (~92% overall voluntary participation)
            checkin_completed = np.random.rand() < 0.92

            if scenario == 'A_STABLE':
                sq = np.clip(4.2 + indiv_sleep_bias + np.random.normal(0, 0.4), 1.0, 5.0)
                fl = np.clip(1.8 - (indiv_sleep_bias * 0.5) + np.random.normal(0, 0.4), 1.0, 5.0)
                ws = np.clip(1.9 + np.random.normal(0, 0.4), 1.0, 5.0)
                mw = np.clip(4.1 + np.random.normal(0, 0.4), 1.0, 5.0)
                wlb = np.clip(4.0 + np.random.normal(0, 0.4), 1.0, 5.0)
                js = np.clip(4.0 + np.random.normal(0, 0.4), 1.0, 5.0)
                rq = np.clip(4.2 + np.random.normal(0, 0.4), 1.0, 5.0)
                srs = np.clip(1.6 + np.random.normal(0, 0.4), 1.0, 5.0)

            elif scenario == 'B_HIGH_TEMPO':
                if 4 <= m_idx <= 8:
                    sq = np.clip(2.8 + indiv_sleep_bias + np.random.normal(0, 0.4), 1.0, 5.0)
                    fl = np.clip(3.6 + np.random.normal(0, 0.4), 1.0, 5.0)
                    ws = np.clip(3.7 + np.random.normal(0, 0.4), 1.0, 5.0)
                    mw = np.clip(3.0 + np.random.normal(0, 0.4), 1.0, 5.0)
                    wlb = np.clip(2.6 + np.random.normal(0, 0.4), 1.0, 5.0)
                    js = np.clip(3.2 + np.random.normal(0, 0.4), 1.0, 5.0)
                    rq = np.clip(2.7 + np.random.normal(0, 0.4), 1.0, 5.0)
                    srs = np.clip(3.4 + np.random.normal(0, 0.4), 1.0, 5.0)
                else:
                    sq = np.clip(3.9 + indiv_sleep_bias + np.random.normal(0, 0.4), 1.0, 5.0)
                    fl = np.clip(2.2 + np.random.normal(0, 0.4), 1.0, 5.0)
                    ws = np.clip(2.3 + np.random.normal(0, 0.4), 1.0, 5.0)
                    mw = np.clip(3.8 + np.random.normal(0, 0.4), 1.0, 5.0)
                    wlb = np.clip(3.6 + np.random.normal(0, 0.4), 1.0, 5.0)
                    js = np.clip(3.8 + np.random.normal(0, 0.4), 1.0, 5.0)
                    rq = np.clip(3.9 + np.random.normal(0, 0.4), 1.0, 5.0)
                    srs = np.clip(2.0 + np.random.normal(0, 0.4), 1.0, 5.0)

            elif scenario == 'C_EXTENDED_DEPLOYMENT':
                if 3 <= m_idx <= 9:
                    sq = np.clip(2.4 + indiv_sleep_bias + np.random.normal(0, 0.4), 1.0, 5.0)
                    fl = np.clip(4.0 + np.random.normal(0, 0.4), 1.0, 5.0)
                    ws = np.clip(3.9 + np.random.normal(0, 0.4), 1.0, 5.0)
                    mw = np.clip(2.7 + np.random.normal(0, 0.4), 1.0, 5.0)
                    wlb = np.clip(2.1 + np.random.normal(0, 0.4), 1.0, 5.0)
                    js = np.clip(2.9 + np.random.normal(0, 0.4), 1.0, 5.0)
                    rq = np.clip(2.3 + np.random.normal(0, 0.4), 1.0, 5.0)
                    srs = np.clip(3.8 + np.random.normal(0, 0.4), 1.0, 5.0)
                else:
                    sq = np.clip(3.8 + indiv_sleep_bias + np.random.normal(0, 0.4), 1.0, 5.0)
                    fl = np.clip(2.4 + np.random.normal(0, 0.4), 1.0, 5.0)
                    ws = np.clip(2.4 + np.random.normal(0, 0.4), 1.0, 5.0)
                    mw = np.clip(3.7 + np.random.normal(0, 0.4), 1.0, 5.0)
                    wlb = np.clip(3.5 + np.random.normal(0, 0.4), 1.0, 5.0)
                    js = np.clip(3.6 + np.random.normal(0, 0.4), 1.0, 5.0)
                    rq = np.clip(3.7 + np.random.normal(0, 0.4), 1.0, 5.0)
                    srs = np.clip(2.1 + np.random.normal(0, 0.4), 1.0, 5.0)

            elif scenario == 'D_CUMULATIVE_STRAIN':
                if m_idx < 4:
                    sq = np.clip(3.5 + indiv_sleep_bias + np.random.normal(0, 0.4), 1.0, 5.0)
                    fl = np.clip(2.7 + np.random.normal(0, 0.4), 1.0, 5.0)
                    ws = np.clip(2.9 + np.random.normal(0, 0.4), 1.0, 5.0)
                    mw = np.clip(3.4 + np.random.normal(0, 0.4), 1.0, 5.0)
                    wlb = np.clip(3.1 + np.random.normal(0, 0.4), 1.0, 5.0)
                    js = np.clip(3.3 + np.random.normal(0, 0.4), 1.0, 5.0)
                    rq = np.clip(3.2 + np.random.normal(0, 0.4), 1.0, 5.0)
                    srs = np.clip(2.7 + np.random.normal(0, 0.4), 1.0, 5.0)
                else:
                    # Progressively degrading wellness indicators
                    strain_mult = min((m_idx - 3) * 0.35, 2.5)
                    sq = np.clip(2.8 - (strain_mult * 0.5) + indiv_sleep_bias + np.random.normal(0, 0.3), 1.0, 5.0)
                    fl = np.clip(3.2 + (strain_mult * 0.6) + np.random.normal(0, 0.3), 1.0, 5.0)
                    ws = np.clip(3.3 + (strain_mult * 0.55) + np.random.normal(0, 0.3), 1.0, 5.0)
                    mw = np.clip(3.0 - (strain_mult * 0.5) + np.random.normal(0, 0.3), 1.0, 5.0)
                    wlb = np.clip(2.5 - (strain_mult * 0.45) + np.random.normal(0, 0.3), 1.0, 5.0)
                    js = np.clip(2.8 - (strain_mult * 0.4) + np.random.normal(0, 0.3), 1.0, 5.0)
                    rq = np.clip(2.6 - (strain_mult * 0.5) + np.random.normal(0, 0.3), 1.0, 5.0)
                    srs = np.clip(3.0 + (strain_mult * 0.7) + np.random.normal(0, 0.3), 1.0, 5.0)

            elif scenario == 'E_RECOVERY':
                if 2 <= m_idx <= 5:
                    sq = np.clip(2.5 + indiv_sleep_bias + np.random.normal(0, 0.4), 1.0, 5.0)
                    fl = np.clip(3.9 + np.random.normal(0, 0.4), 1.0, 5.0)
                    ws = np.clip(3.8 + np.random.normal(0, 0.4), 1.0, 5.0)
                    mw = np.clip(2.8 + np.random.normal(0, 0.4), 1.0, 5.0)
                    wlb = np.clip(2.2 + np.random.normal(0, 0.4), 1.0, 5.0)
                    js = np.clip(2.9 + np.random.normal(0, 0.4), 1.0, 5.0)
                    rq = np.clip(2.4 + np.random.normal(0, 0.4), 1.0, 5.0)
                    srs = np.clip(3.7 + np.random.normal(0, 0.4), 1.0, 5.0)
                else:
                    # Fast rebound in month 6-12
                    sq = np.clip(4.3 + indiv_sleep_bias + np.random.normal(0, 0.3), 1.0, 5.0)
                    fl = np.clip(1.7 + np.random.normal(0, 0.3), 1.0, 5.0)
                    ws = np.clip(1.8 + np.random.normal(0, 0.3), 1.0, 5.0)
                    mw = np.clip(4.2 + np.random.normal(0, 0.3), 1.0, 5.0)
                    wlb = np.clip(4.1 + np.random.normal(0, 0.3), 1.0, 5.0)
                    js = np.clip(4.1 + np.random.normal(0, 0.3), 1.0, 5.0)
                    rq = np.clip(4.4 + np.random.normal(0, 0.3), 1.0, 5.0)
                    srs = np.clip(1.5 + np.random.normal(0, 0.3), 1.0, 5.0)

            elif scenario == 'F_RESILIENT_NOISE':
                # Despite workload bump in months 6-7, individual remains resilient with solid wellness
                sq = np.clip(3.9 + indiv_sleep_bias + np.random.normal(0, 0.3), 1.0, 5.0)
                fl = np.clip(2.4 + np.random.normal(0, 0.3), 1.0, 5.0)
                ws = np.clip(2.5 + np.random.normal(0, 0.3), 1.0, 5.0)
                mw = np.clip(4.0 + np.random.normal(0, 0.3), 1.0, 5.0)
                wlb = np.clip(3.7 + np.random.normal(0, 0.3), 1.0, 5.0)
                js = np.clip(3.9 + np.random.normal(0, 0.3), 1.0, 5.0)
                rq = np.clip(3.9 + np.random.normal(0, 0.3), 1.0, 5.0)
                srs = np.clip(2.0 + np.random.normal(0, 0.3), 1.0, 5.0)

            wellness_rows.append({
                "personnel_id": pid,
                "date": date_str,
                "month_idx": m_idx,
                "sleep_quality": round(float(sq), 1) if checkin_completed else np.nan,
                "fatigue_level": round(float(fl), 1) if checkin_completed else np.nan,
                "work_stress": round(float(ws), 1) if checkin_completed else np.nan,
                "mood_wellbeing": round(float(mw), 1) if checkin_completed else np.nan,
                "work_life_balance": round(float(wlb), 1) if checkin_completed else np.nan,
                "job_satisfaction": round(float(js), 1) if checkin_completed else np.nan,
                "recovery_quality": round(float(rq), 1) if checkin_completed else np.nan,
                "self_reported_strain": round(float(srs), 1) if checkin_completed else np.nan,
                "checkin_completion": bool(checkin_completed)
            })

            # -------------------------------------------------------------
            # 5. BEHAVIORAL CHANGE RECORDS (ORGANIZATIONAL SHIFTS ONLY)
            # -------------------------------------------------------------
            # Measuring month-over-month relative delta from prior period
            duty_change = (duty_hrs - prev_duty_hours) / max(prev_duty_hours, 1.0)
            workload_delta = (workload_score - prev_workload_score) / max(prev_workload_score, 1.0)
            sleep_delta = (sq - prev_sleep_quality) / max(prev_sleep_quality, 1.0)

            att_change = -1.0 * max(0.0, float(duty_change * 0.3 + np.random.normal(0, 0.05)))
            lv_freq_change = 0.2 if took_leave else -0.1
            perf_change = np.clip(float(sleep_delta * 0.4 - duty_change * 0.2 + np.random.normal(0, 0.05)), -0.5, 0.5)
            sched_change = float((sched_irreg - 1.5) / 3.5)
            rec_change = float((rest_hrs - 85.0) / 45.0)
            routine_dev = float(np.clip(abs(duty_change) * 0.5 + abs(sched_change) * 0.5, 0.0, 1.0))

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

            # Update lag variables
            prev_duty_hours = duty_hrs
            prev_night_shifts = night_shifts
            prev_sleep_quality = sq
            prev_workload_score = workload_score

    # Save synthetic datasets to disk
    dep_df = pd.DataFrame(deployment_rows)
    leave_df = pd.DataFrame(leave_rows)
    workload_df = pd.DataFrame(workload_rows)
    wellness_df = pd.DataFrame(wellness_rows)
    behavioral_df = pd.DataFrame(behavioral_rows)

    dep_path = SYNTHETIC_DIR / "deployment" / "deployment_records.csv"
    leave_path = SYNTHETIC_DIR / "leave" / "leave_history.csv"
    workload_path = SYNTHETIC_DIR / "workload" / "workload_records.csv"
    wellness_path = SYNTHETIC_DIR / "wellness" / "wellness_surveys.csv"
    behavioral_path = SYNTHETIC_DIR / "behavioral" / "behavioral_records.csv"

    dep_df.to_csv(dep_path, index=False)
    leave_df.to_csv(leave_path, index=False)
    workload_df.to_csv(workload_path, index=False)
    wellness_df.to_csv(wellness_path, index=False)
    behavioral_df.to_csv(behavioral_path, index=False)

    print(f"[✓] Synthetic datasets generated successfully:")
    print(f"    - Deployment records: {len(dep_df)} rows ({dep_path})")
    print(f"    - Leave history:     {len(leave_df)} rows ({leave_path})")
    print(f"    - Workload records:  {len(workload_df)} rows ({workload_path})")
    print(f"    - Wellness surveys:  {len(wellness_df)} rows ({wellness_path})")
    print(f"    - Behavioral logs:   {len(behavioral_df)} rows ({behavioral_path})")

if __name__ == "__main__":
    generate_synthetic_longitudinal_data()
