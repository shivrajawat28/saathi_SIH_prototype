# SAATHI Security, Privacy & Compliance Architecture

## 1. Authentication & Cryptographic Standards

- **Password Hashing**: Passwords are encrypted using **Bcrypt** with salt stretching (work factor 12). Plaintext passwords are never logged, stored, or transmitted.
- **JWT Authorization**: Stateless JSON Web Tokens signed with HMAC-SHA256 (`HS256`). Tokens include:
  - Subject (`sub`): User identifier
  - Role (`role`): Assigned system role
  - Expiration (`exp`): 8 hours (`28800` seconds)
- **Secret Management**: Environment-based configuration loaded via Pydantic `BaseSettings`. Default secrets are blocked in production environments.

---

## 2. Role-Based Access Control (RBAC) & Service-Layer Enforcement

Authorization is enforced at the FastAPI dependency layer via `require_role(...)` and `require_permission(...)`:

```python
@router.post("/predictions/personnel/{personnel_id}", dependencies=[Depends(require_role(["ADMIN", "WELFARE_OFFICER"]))])
async def generate_prediction(...):
    ...
```

### Privacy Isolation Matrix:
1. **Commander Role Restrictions**:
   - Commanders receive high-level readiness/workload counts and support priority distribution.
   - **Privacy Boundary**: Commanders are blocked from viewing raw voluntary self-reported wellness surveys (e.g., subjective mood, personal fatigue scores) to maintain trust and psychological safety in uniformed forces.
2. **Analyst Role Restrictions**:
   - Analysts receive aggregated statistical summaries without identifiable personnel references.
3. **Personnel Role Restrictions**:
   - Personnel can view their own score and submit voluntary check-ins, but cannot view peer records.

---

## 3. Data Protection & Privacy by Design

- **Pseudonymization**: Personnel master and longitudinal records use pseudonymous identifiers (`P-000001` to `P-001470`).
- **No Medical/Clinical Claims**: The system outputs occupational priority classifications, not medical diagnoses.
- **Surveillance Vector Exclusion**: SAATHI contains zero video surveillance feeds, facial recognition, voice stress analysis, GPS location tracking, or private message scraping.
- **SQL Injection Prevention**: Built entirely with **SQLAlchemy 2.x ORM** using parameterized queries.
- **Cross-Origin Resource Sharing (CORS)**: Configurable origin whitelisting via `BACKEND_CORS_ORIGINS`.

---

## 4. Immutable Audit Logging

Every sensitive data access and modification is recorded in the `audit_logs` table:
- User ID & Role
- Action type (`LOGIN`, `VIEW_PERSONNEL`, `RUN_PREDICTION`, `CREATE_INTERVENTION`, `SUBMIT_WELLNESS`)
- Target resource identifier
- Client IP Address
- Execution timestamp (UTC)
- Audit logs contain zero raw wellness text or passwords.
