"""
SAATHI Force-Oriented Synthetic Presentation Taxonomy
Maps generic source attributes to synthetic uniformed-force operational and welfare classifications.
For prototype demonstration only — no real CRPF personnel or structures are represented.
"""

from typing import Optional, Dict

DEPARTMENT_TAXONOMY_MAP: Dict[str, str] = {
    "Sales": "Operations",
    "Research & Development": "Communications & Technology",
    "Human Resources": "Administration & Welfare",
    "Operations": "Operations",
    "Communications & Technology": "Communications & Technology",
    "Logistics & Support": "Logistics & Support",
    "Training & Readiness": "Training & Readiness",
    "Administration & Welfare": "Administration & Welfare",
    "Administration": "Administration & Welfare"
}

JOB_ROLE_TAXONOMY_MAP: Dict[str, str] = {
    "Sales Executive": "Field Sub-Inspector",
    "Sales Representative": "Field Constable",
    "Research Scientist": "Technical Specialist",
    "Laboratory Technician": "Signals & Comms Technician",
    "Manufacturing Director": "Operations Inspector",
    "Healthcare Representative": "Medical & Welfare Liaison",
    "Manager": "Assistant Commandant",
    "Research Director": "Communications Director",
    "Human Resources": "Administration Officer",
    # Pass-through for already mapped or generic roles
    "Field Sub-Inspector": "Field Sub-Inspector",
    "Field Constable": "Field Constable",
    "Technical Specialist": "Technical Specialist",
    "Signals & Comms Technician": "Signals & Comms Technician",
    "Operations Inspector": "Operations Inspector",
    "Medical & Welfare Liaison": "Medical & Welfare Liaison",
    "Assistant Commandant": "Assistant Commandant",
    "Communications Director": "Communications Director",
    "Administration Officer": "Administration Officer"
}

def map_department(dept: Optional[str]) -> str:
    if not dept:
        return "Operations"
    return DEPARTMENT_TAXONOMY_MAP.get(dept, dept)

def map_job_role(role: Optional[str]) -> str:
    if not role:
        return "Field Personnel"
    return JOB_ROLE_TAXONOMY_MAP.get(role, role)
