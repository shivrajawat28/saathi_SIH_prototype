"""
SAATHI — Supabase Database Migration & Verification Utility
Connects to Supabase PostgreSQL, creates all tables/indexes based on SQLAlchemy models,
seeds deterministic demo accounts and longitudinal personnel records idempotently,
and verifies schema integrity.
"""

import sys
import os
import argparse
from pathlib import Path
from datetime import date, datetime, timedelta, timezone
import pandas as pd
from sqlalchemy import create_engine, select, func, text
from sqlalchemy.orm import sessionmaker

# Ensure project root is on sys.path
BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE_DIR))

from backend.app.core.config import settings, normalize_database_url
from backend.app.db.session import Base
import backend.app.models
from backend.app.models.user import User, Role
from backend.app.models.personnel import Personnel, HRProfile
from backend.app.models.prediction import Prediction, PredictionExplanation, WelfareRecommendation
from backend.app.models.intervention import Intervention, InterventionOutcome
from backend.app.models.follow_up import CheckInFollowUp
from backend.app.models.conversation import WellnessConversation, ConversationMessage
from backend.app.models.telemetry import DeploymentRecord, LeaveRecord, WorkloadRecord, WellnessRecord, BehavioralRecord
from backend.app.models.audit import AuditLog
from backend.app.core.security import get_password_hash
from backend.app.core.taxonomy import map_department, map_job_role
from backend.app.db.init_db import ROLES_LIST, DEMO_USERS


def run_migration_and_seed(database_url: str, seed_telemetry_limit: int = 50):
    print("=" * 70)
    print("SAATHI: Migrating to Supabase PostgreSQL Database")
    print("Target Project Reference: agsbavsttzdbbnoqoxeu")
    print("=" * 70)

    # Normalize driver scheme (e.g. postgresql+psycopg:// -> postgresql+psycopg2://)
    database_url = normalize_database_url(database_url)

    # Sanitize and prepare connection args
    connect_args = {}
    if database_url.startswith("sqlite"):
        connect_args = {"check_same_thread": False}
    elif "supabase" in database_url and "sslmode" not in database_url:
        connect_args["sslmode"] = "require"

    engine = create_engine(
        database_url,
        connect_args=connect_args,
        pool_pre_ping=True
    )

    # 1. Verify Connectivity
    print("\n[Step 1/6] Verifying database connectivity...")
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1;"))
            if "postgres" in engine.dialect.name:
                result = conn.execute(text("SELECT version();")).scalar()
                print(f"  [✓] Connected successfully to PostgreSQL: {result.split(',')[0]}")
            else:
                print(f"  [✓] Connected successfully to {engine.dialect.name.upper()} database.")
    except Exception as e:
        print(f"  [✗] Connection failed: {e}")
        return False

    # 2. Apply Schema Migrations
    print("\n[Step 2/6] Applying schema migrations (19 SAATHI tables)...")
    try:
        Base.metadata.create_all(bind=engine)
        print("  [✓] All tables, primary keys, foreign keys, and indexes ensured.")
    except Exception as e:
        print(f"  [✗] Schema migration failed: {e}")
        return False

    # 3. Seed Roles & Demo Users
    Session = sessionmaker(bind=engine)
    db = Session()
    try:
        print("\n[Step 3/6] Seeding system roles & authorized demo accounts...")
        role_objs = {}
        for role_name, desc in ROLES_LIST:
            role = db.scalars(select(Role).where(Role.name == role_name)).first()
            if not role:
                role = Role(name=role_name, description=desc)
                db.add(role)
                db.flush()
            role_objs[role_name] = role
        db.commit()
        print(f"  [✓] 5 System Roles verified: {list(role_objs.keys())}")

        users_created = 0
        for uname, email, pwd, full_name, r_name, p_id in DEMO_USERS:
            user = db.scalars(select(User).where(User.username == uname)).first()
            if not user:
                user = User(
                    username=uname,
                    email=email,
                    hashed_password=get_password_hash(pwd),
                    full_name=full_name,
                    personnel_id=p_id,
                    is_active=True
                )
                user.roles.append(role_objs[r_name])
                db.add(user)
                users_created += 1
            elif user and not user.roles:
                user.roles.append(role_objs[r_name])
        db.commit()
        print(f"  [✓] Demo accounts verified ({users_created} newly created, {len(DEMO_USERS)} total ensured).")

        # 4. Seed Personnel Master Profiles
        print("\n[Step 4/6] Seeding pseudonymous personnel profiles...")
        personnel_csv = BASE_DIR / "data/processed/personnel_master.csv"
        if personnel_csv.exists():
            existing_count = db.query(Personnel).count()
            if existing_count == 0:
                df = pd.read_csv(personnel_csv)
                subset = df.head(200)
                for _, row in subset.iterrows():
                    pid = str(row["personnel_id"])
                    p_rec = Personnel(
                        personnel_id=pid,
                        original_ref_id=str(row.get("original_ref_id", ""))
                    )
                    hr = HRProfile(
                        personnel_id=pid,
                        age=int(row["age"]) if pd.notna(row.get("age")) else None,
                        gender=str(row["gender"]) if pd.notna(row.get("gender")) else None,
                        department=map_department(str(row["department"])) if pd.notna(row.get("department")) else "Operations",
                        job_role=map_job_role(str(row["job_role"])) if pd.notna(row.get("job_role")) else "Field Personnel",
                        job_level=int(row["job_level"]) if pd.notna(row.get("job_level")) else None,
                        education_level=int(row["education_level"]) if pd.notna(row.get("education_level")) else None,
                        education_field=str(row["education_field"]) if pd.notna(row.get("education_field")) else None,
                        marital_status=str(row["marital_status"]) if pd.notna(row.get("marital_status")) else None,
                        distance_from_home=int(row["distance_from_home"]) if pd.notna(row.get("distance_from_home")) else None,
                        business_travel=str(row["business_travel"]) if pd.notna(row.get("business_travel")) else None,
                        overtime_eligible=str(row["overtime_eligible"]) if pd.notna(row.get("overtime_eligible")) else None,
                        total_working_years=int(row["total_working_years"]) if pd.notna(row.get("total_working_years")) else None,
                        years_in_service=int(row["years_in_service"]) if pd.notna(row.get("years_in_service")) else None,
                        years_in_current_role=int(row["years_in_current_role"]) if pd.notna(row.get("years_in_current_role")) else None,
                        years_since_last_promotion=int(row["years_since_last_promotion"]) if pd.notna(row.get("years_since_last_promotion")) else None,
                        years_with_curr_supervisor=float(row["years_with_curr_supervisor"]) if pd.notna(row.get("years_with_curr_supervisor")) else None,
                        baseline_env_satisfaction=int(row["baseline_env_satisfaction"]) if pd.notna(row.get("baseline_env_satisfaction")) else None,
                        baseline_job_satisfaction=int(row["baseline_job_satisfaction"]) if pd.notna(row.get("baseline_job_satisfaction")) else None,
                        baseline_job_involvement=int(row["baseline_job_involvement"]) if pd.notna(row.get("baseline_job_involvement")) else None,
                        baseline_work_life_balance=int(row["baseline_work_life_balance"]) if pd.notna(row.get("baseline_work_life_balance")) else None,
                        baseline_rel_satisfaction=int(row["baseline_rel_satisfaction"]) if pd.notna(row.get("baseline_rel_satisfaction")) else None,
                        performance_rating=int(row["performance_rating"]) if pd.notna(row.get("performance_rating")) else None,
                        training_times_last_year=int(row["training_times_last_year"]) if pd.notna(row.get("training_times_last_year")) else None,
                        monthly_income=int(row["monthly_income"]) if pd.notna(row.get("monthly_income")) else None
                    )
                    p_rec.hr_profile = hr
                    db.add(p_rec)
                db.commit()
                print(f"  [✓] Seeded {len(subset)} personnel master profiles.")
            else:
                print(f"  [✓] Personnel master profiles already present ({existing_count} records).")

        # 5. Seed Canonical Demo Records (Predictions, Interventions, Check-In Follow-Up, Conversations)
        print("\n[Step 5/6] Seeding canonical evaluation cases (P-000013 and P-000001)...")
        welfare_user = db.scalars(select(User).where(User.username == "welfare_officer")).first()
        commander_user = db.scalars(select(User).where(User.username == "commander")).first()

        # P-000013 Prediction
        pred13 = db.scalars(select(Prediction).where(Prediction.prediction_id == "PRED-P000013-M12")).first()
        if not pred13:
            pred13 = Prediction(
                prediction_id="PRED-P000013-M12",
                personnel_id="P-000013",
                prediction_month_idx=12,
                support_score=88.1,
                support_priority="RED",
                high_risk_probability=0.8806,
                prediction_reliability=0.88,
                data_completeness=1.0,
                baseline_maturity_months=11,
                operating_threshold=0.50,
                human_review_required=True
            )
            db.add(pred13)
            db.flush()

            exp1 = PredictionExplanation(
                prediction_id="PRED-P000013-M12",
                factor_name="Elapsed duration since previous leave",
                direction="increase",
                contribution_score=0.196
            )
            exp2 = PredictionExplanation(
                prediction_id="PRED-P000013-M12",
                factor_name="Operational tempo & intensity level",
                direction="increase",
                contribution_score=0.167
            )
            exp3 = PredictionExplanation(
                prediction_id="PRED-P000013-M12",
                factor_name="Total monthly workload index",
                direction="increase",
                contribution_score=0.145
            )
            rec1 = WelfareRecommendation(
                prediction_id="PRED-P000013-M12",
                recommendation_type="RECOVERY_LEAVE",
                priority_level="HIGH",
                reason="Mandatory 10-day recovery leave advised to address cumulative 302-day leave deficit."
            )
            rec2 = WelfareRecommendation(
                prediction_id="PRED-P000013-M12",
                recommendation_type="WORKLOAD_ROTATION",
                priority_level="HIGH",
                reason="Rotate off consecutive night shifts and high-intensity duty roster for next rotation cycle."
            )
            rec3 = WelfareRecommendation(
                prediction_id="PRED-P000013-M12",
                recommendation_type="WELFARE_OFFICER_CHECK_IN",
                priority_level="MEDIUM",
                reason="Conduct confidential, non-punitive welfare review within 7 operational days."
            )
            db.add_all([exp1, exp2, exp3, rec1, rec2, rec3])
            db.commit()
            print("  [✓] Seeded P-000013 canonical RED prediction (88.1, RED) with SHAP factors & recommendations.")
        else:
            print("  [✓] P-000013 canonical prediction already present.")

        # P-000001 Prediction
        pred1 = db.scalars(select(Prediction).where(Prediction.prediction_id == "PRED-P000001-M12")).first()
        if not pred1:
            pred1 = Prediction(
                prediction_id="PRED-P000001-M12",
                personnel_id="P-000001",
                prediction_month_idx=12,
                support_score=5.0,
                support_priority="GREEN",
                high_risk_probability=0.0187,
                prediction_reliability=0.98,
                data_completeness=1.0,
                baseline_maturity_months=11,
                operating_threshold=0.50,
                human_review_required=False
            )
            db.add(pred1)
            db.flush()
            exp_p1 = PredictionExplanation(
                prediction_id="PRED-P000001-M12",
                factor_name="Total monthly workload index",
                direction="decrease",
                contribution_score=0.05
            )
            rec_p1 = WelfareRecommendation(
                prediction_id="PRED-P000001-M12",
                recommendation_type="STANDARD_MONITORING",
                priority_level="LOW",
                reason="Routine welfare monitoring; personnel maintains stable operational baseline."
            )
            db.add_all([exp_p1, rec_p1])
            db.commit()
            print("  [✓] Seeded P-000001 canonical GREEN prediction (5.0, GREEN).")

        # Canonical Intervention for P-000013
        inv = db.scalars(select(Intervention).where(Intervention.intervention_id == "INT-P000013-001")).first()
        if not inv and welfare_user:
            inv = Intervention(
                intervention_id="INT-P000013-001",
                personnel_id="P-000013",
                officer_user_id=welfare_user.id,
                intervention_type="RECOVERY_LEAVE_AND_REST",
                intervention_date=date(2026, 9, 15),
                status="IN_PROGRESS",
                action_summary="Initiated administrative coordination for 10-day accumulated compensatory leave and rotational relief from night shifts."
            )
            db.add(inv)
            db.flush()
            out = InterventionOutcome(
                intervention_id="INT-P000013-001",
                review_date=date(2026, 10, 1),
                outcome_status="IMPROVED",
                follow_up_notes="Personnel completed rest cycle; initial fatigue markers visibly stabilized. Follow-up scheduled for next monthly cycle.",
                recorded_by_user_id=welfare_user.id
            )
            db.add(out)
            db.commit()
            print("  [✓] Seeded canonical welfare intervention & outcome for P-000013.")

        # Canonical Check-in Follow-up for P-000013
        fu = db.scalars(select(CheckInFollowUp).where(CheckInFollowUp.personnel_id == "P-000013")).first()
        if not fu and commander_user:
            fu = CheckInFollowUp(
                personnel_id="P-000013",
                requested_by_id=commander_user.id,
                requested_by_username=commander_user.username,
                target_month="2026-09",
                status="FOLLOW_UP_REQUESTED",
                notes="Administrative monthly welfare check-in reminder requested by unit commander."
            )
            db.add(fu)
            db.commit()
            print("  [✓] Seeded canonical check-in follow-up request for P-000013.")

        # Canonical Confidential Wellness Conversation for P-000013
        conv = db.scalars(select(WellnessConversation).where(WellnessConversation.conversation_id == "CONV-P000013-001")).first()
        if not conv:
            conv = WellnessConversation(
                conversation_id="CONV-P000013-001",
                personnel_id="P-000013",
                consent_given=True,
                input_mode="TEXT",
                ai_summary="Voluntary check-in indicated elevated operational fatigue and disrupted sleep rhythm following consecutive night shifts.",
                structured_signals={"fatigue": "Elevated", "sleep_difficulty": "Elevated", "workload_pressure": "Elevated"},
                confidence=0.91,
                urgency_level="MODERATE",
                is_crisis=False,
                welfare_signal_impact="Elevated Strain Indicator (+7.2 pts)",
                change_vs_previous="Fatigue and sleep concerns increased vs last check-in",
                status="PENDING_REVIEW"
            )
            db.add(conv)
            db.flush()
            msg1 = ConversationMessage(
                conversation_id=conv.id,
                sender="USER",
                text="Namaste, pichhle kuch hafton se duty continuous chal rahi hai aur night shifts ki wajah se neend nahi aa rahi.",
                is_voice=False
            )
            msg2 = ConversationMessage(
                conversation_id=conv.id,
                sender="ASSISTANT",
                text="Namaste. Aapki continuous duty aur night shifts ki wajah se sharir aur dimag par asar padna swabhavik hai. Aapka yeh anubhav poori tarah confidential hai. Kya aapko lagta hai ki thoda rest ya shift change se madad mil sakti hai?",
                is_voice=False
            )
            db.add_all([msg1, msg2])
            db.commit()
            print("  [✓] Seeded canonical voluntary confidential conversation & messages for P-000013.")

        # Telemetry Records from Parquet
        parquet_path = BASE_DIR / "data/processed/integrated_longitudinal.parquet"
        if parquet_path.exists():
            existing_wl = db.query(WorkloadRecord).count()
            if existing_wl == 0:
                print(f"  [...] Seeding longitudinal telemetry from {parquet_path.name}...")
                df_long = pd.read_parquet(parquet_path)
                # Seed canonical personnel P-000013, P-000001 and top N personnel
                seeded_pids = ["P-000013", "P-000001"] + [f"P-{i:06d}" for i in range(2, seed_telemetry_limit + 1)]
                df_subset = df_long[df_long["personnel_id"].isin(seeded_pids)]
                
                wl_count = 0
                wn_count = 0
                dp_count = 0
                lv_count = 0
                bh_count = 0
                
                for _, row in df_subset.iterrows():
                    pid = str(row["personnel_id"])
                    m_idx = int(row["month_idx"])
                    dt = date.fromisoformat(str(row["date"])) if pd.notna(row.get("date")) else date(2025, m_idx, 1)

                    # Workload
                    wl = WorkloadRecord(
                        personnel_id=pid,
                        month_idx=m_idx,
                        date=dt,
                        duty_hours=float(row.get("duty_hours", 160.0)),
                        overtime_hours=float(row.get("overtime_hours", 0.0)),
                        night_shifts=int(row.get("night_shifts", 0)),
                        consecutive_duty_days=int(row.get("consecutive_duty_days", 5)),
                        rest_hours=float(row.get("rest_hours", 80.0)),
                        workload_score=float(row.get("workload_score", 50.0)),
                        operational_intensity=int(row.get("operational_intensity", 1)),
                        schedule_irregularity=float(row.get("schedule_irregularity", 0.0))
                    )
                    db.add(wl)
                    wl_count += 1

                    # Wellness
                    wn = WellnessRecord(
                        personnel_id=pid,
                        month_idx=m_idx,
                        date=dt,
                        sleep_quality=float(row["sleep_quality"]) if pd.notna(row.get("sleep_quality")) else None,
                        fatigue_level=float(row["fatigue_level"]) if pd.notna(row.get("fatigue_level")) else None,
                        work_stress=float(row["work_stress"]) if pd.notna(row.get("work_stress")) else None,
                        mood_wellbeing=float(row["mood_wellbeing"]) if pd.notna(row.get("mood_wellbeing")) else None,
                        work_life_balance=float(row["work_life_balance"]) if pd.notna(row.get("work_life_balance")) else None,
                        job_satisfaction=float(row["job_satisfaction"]) if pd.notna(row.get("job_satisfaction")) else None,
                        recovery_quality=float(row["recovery_quality"]) if pd.notna(row.get("recovery_quality")) else None,
                        self_reported_strain=float(row["self_reported_strain"]) if pd.notna(row.get("self_reported_strain")) else None,
                        checkin_completion=bool(row.get("checkin_completion", True))
                    )
                    db.add(wn)
                    wn_count += 1

                    # Behavioral
                    bh = BehavioralRecord(
                        personnel_id=pid,
                        month_idx=m_idx,
                        date=dt,
                        attendance_change=float(row.get("attendance_change", 0.0)),
                        leave_frequency_change=float(row.get("leave_frequency_change", 0.0)),
                        workload_change=float(row.get("workload_change", 0.0)),
                        sleep_change=float(row.get("sleep_change", 0.0)),
                        routine_deviation=float(row.get("routine_deviation", 0.0)),
                        performance_change=float(row.get("performance_change", 0.0)),
                        schedule_change=float(row.get("schedule_change", 0.0)),
                        recovery_change=float(row.get("recovery_change", 0.0))
                    )
                    db.add(bh)
                    bh_count += 1

                    # Deployment if deployed
                    if bool(row.get("is_deployed", False)):
                        dep_id = f"DEP-{pid}-{m_idx:02d}"
                        dp = DeploymentRecord(
                            deployment_id=dep_id,
                            personnel_id=pid,
                            month_idx=m_idx,
                            date=dt,
                            start_date=dt,
                            end_date=dt + timedelta(days=int(row.get("dep_duration_days", 20))),
                            deployment_duration_days=int(row.get("dep_duration_days", 20)),
                            deployment_type=str(row.get("dep_type", "Extended")),
                            operational_intensity=int(row.get("dep_intensity", 3)),
                            hardship_level=int(row.get("dep_hardship", 4)),
                            recovery_required=bool(row.get("dep_recovery_required", True)),
                            location_category=str(row.get("dep_location", "Remote/Difficult Terrain"))
                        )
                        db.add(dp)
                        dp_count += 1

                    # Leave if took leave
                    if bool(row.get("took_leave", False)):
                        lv_id = f"LV-{pid}-{m_idx:02d}"
                        lv = LeaveRecord(
                            leave_id=lv_id,
                            personnel_id=pid,
                            month_idx=m_idx,
                            date=dt,
                            leave_start_date=dt,
                            leave_end_date=dt + timedelta(days=int(row.get("leave_duration_days", 10))),
                            duration_days=int(row.get("leave_duration_days", 10)),
                            leave_type=str(row.get("leave_type", "Annual")),
                            days_since_previous_leave=int(row.get("days_since_prev_leave", 30))
                        )
                        db.add(lv)
                        lv_count += 1

                db.commit()
                print(f"  [✓] Seeded longitudinal telemetry: {wl_count} workload, {wn_count} wellness, {dp_count} deployments, {lv_count} leaves, {bh_count} behavioral.")
            else:
                print(f"  [✓] Longitudinal telemetry records already present ({existing_wl} records).")

        # Initial Audit Log
        audit = db.scalars(select(AuditLog).where(AuditLog.action == "MIGRATION_INIT")).first()
        if not audit and welfare_user:
            audit = AuditLog(
                user_id=welfare_user.id,
                username="system_migrator",
                user_role="ADMIN",
                action="MIGRATION_INIT",
                target_resource="supabase_postgresql",
                status="SUCCESS",
                details="Supabase database initialization and idempotent seed complete."
            )
            db.add(audit)
            db.commit()
            print("  [✓] Audit log entry recorded.")

    finally:
        db.close()

    # 6. Final Table Verification
    print("\n[Step 6/6] Verifying Table Row Counts...")
    tables_to_verify = [
        ("roles", Role),
        ("users", User),
        ("personnel", Personnel),
        ("hr_profiles", HRProfile),
        ("workload_records", WorkloadRecord),
        ("wellness_records", WellnessRecord),
        ("deployment_records", DeploymentRecord),
        ("leave_records", LeaveRecord),
        ("behavioral_records", BehavioralRecord),
        ("predictions", Prediction),
        ("prediction_explanations", PredictionExplanation),
        ("welfare_recommendations", WelfareRecommendation),
        ("interventions", Intervention),
        ("intervention_outcomes", InterventionOutcome),
        ("checkin_followups", CheckInFollowUp),
        ("wellness_conversations", WellnessConversation),
        ("conversation_messages", ConversationMessage),
        ("audit_logs", AuditLog),
    ]

    v_db = Session()
    try:
        print(f"  {'Table Name':<28} | {'Row Count':<10} | {'Status'}")
        print(f"  {'-'*28}-|-{'-'*10}-|-{'-'*8}")
        all_passed = True
        for tbl_name, model_cls in tables_to_verify:
            cnt = v_db.query(model_cls).count()
            status_str = "PASS" if cnt > 0 else "EMPTY"
            print(f"  {tbl_name:<28} | {cnt:<10} | {status_str}")
            if cnt == 0 and tbl_name in ["roles", "users", "personnel", "hr_profiles"]:
                all_passed = False
    finally:
        v_db.close()

    print("\n" + "=" * 70)
    if all_passed:
        print("MIGRATION & VERIFICATION COMPLETE: ALL SYSTEMS READY FOR SUPABASE!")
    else:
        print("MIGRATION FINISHED WITH WARNINGS.")
    print("=" * 70)
    return all_passed


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="SAATHI Supabase Migration & Seed Tool")
    parser.add_argument("--database-url", type=str, default=None, help="PostgreSQL connection string (e.g. Supabase)")
    args = parser.parse_args()

    target_url = args.database_url or os.getenv("DATABASE_URL") or settings.DATABASE_URL
    print(f"Using DATABASE_URL: {target_url.split('@')[-1] if '@' in target_url else target_url}")

    success = run_migration_and_seed(target_url)
    sys.exit(0 if success else 1)
