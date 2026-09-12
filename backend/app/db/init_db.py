"""
SAATHI Database Initialization & Seeding Script
Creates tables, initializes system roles, creates default administrator and demo accounts,
and seeds pseudonymous personnel master profiles.
"""

import os
from pathlib import Path
import pandas as pd
from sqlalchemy.orm import Session
from sqlalchemy import select

from backend.app.db.session import engine, Base, SessionLocal
import backend.app.models  # Ensure all models are registered
from backend.app.models.user import User, Role
from backend.app.models.personnel import Personnel, HRProfile
from backend.app.core.security import get_password_hash
from backend.app.core.taxonomy import map_department, map_job_role

ROLES_LIST = [
    ("ADMIN", "System administrator with full configuration and audit access"),
    ("WELFARE_OFFICER", "Authorized welfare officer with personnel, prediction, and intervention authority"),
    ("COMMANDER", "Unit commander with aggregate and operational priority overview"),
    ("ANALYST", "Welfare research analyst with anonymized analytics access"),
    ("PERSONNEL", "Individual uniformed personnel with personal welfare view and check-in access")
]

DEMO_USERS = [
    ("admin", "admin@saathi.gov.in", "admin123", "System Administrator", "ADMIN", None),
    ("welfare_officer", "welfare@saathi.gov.in", "welfare123", "Capt. Sharma (Welfare Officer)", "WELFARE_OFFICER", None),
    ("commander", "commander@saathi.gov.in", "commander123", "Col. Verma (Unit Commander)", "COMMANDER", None),
    ("analyst", "analyst@saathi.gov.in", "analyst123", "Dr. Rao (Welfare Analyst)", "ANALYST", None),
    ("personnel_p13", "personnel13@saathi.gov.in", "personnel123", "Personnel P-000013 (Demo Candidate)", "PERSONNEL", "P-000013"),
    ("officer_p1", "personnel1@saathi.gov.in", "personnel123", "Personnel P-000001 (Baseline Comparison)", "PERSONNEL", "P-000001")
]

def init_db():
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        # 1. Seed Roles
        role_objs = {}
        for role_name, desc in ROLES_LIST:
            role = db.scalars(select(Role).where(Role.name == role_name)).first()
            if not role:
                role = Role(name=role_name, description=desc)
                db.add(role)
                db.flush()
            role_objs[role_name] = role
        db.commit()

        # 2. Seed Demo Users
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
            elif user and not user.roles:
                user.roles.append(role_objs[r_name])
        db.commit()

        # 3. Seed Personnel Master Profiles (from data/processed/personnel_master.csv)
        personnel_csv = Path(__file__).resolve().parents[3] / "data" / "processed" / "personnel_master.csv"
        if personnel_csv.exists():
            existing_count = db.query(Personnel).count()
            if existing_count == 0:
                print(f"Seeding personnel from {personnel_csv} with synthetic force taxonomy...")
                df = pd.read_csv(personnel_csv)
                # Seed first 200 personnel records for quick startup while covering full diversity
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
                print(f"Successfully seeded {len(subset)} personnel profiles.")
            else:
                # Update existing HRProfiles with mapped department/job_role if legacy corporate names exist
                legacy_profiles = db.scalars(select(HRProfile)).all()
                updated_cnt = 0
                for prof in legacy_profiles:
                    new_dept = map_department(prof.department)
                    new_role = map_job_role(prof.job_role)
                    if new_dept != prof.department or new_role != prof.job_role:
                        prof.department = new_dept
                        prof.job_role = new_role
                        updated_cnt += 1
                if updated_cnt > 0:
                    db.commit()
                    print(f"Migrated {updated_cnt} personnel profiles to synthetic force taxonomy.")
        print("Database initialization complete.")
        print("Database initialization complete.")
    finally:
        db.close()

if __name__ == "__main__":
    init_db()
