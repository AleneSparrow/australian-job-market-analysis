import pandas as pd
from sqlalchemy import create_engine

# ==========================
# PostgreSQL connection
# ==========================

engine = create_engine(
    "postgresql+psycopg2://postgres:7851@localhost:5432/australian_job_market"
)

# ==========================
# Load tables
# ==========================

jobs = pd.read_sql(
    """
    SELECT job_id, description_clean, title
    FROM jobs_unified
    """,
    engine
)

features = pd.read_sql(
    "SELECT * FROM jobs_features",
    engine
)

# ==========================
# Prepare text
# ==========================

text = (
    jobs["title"].fillna("") + " " +
    jobs["description_clean"].fillna("")
).str.lower()
# ==========================
# Visa & Work Rights Patterns
# ==========================

visa = pd.DataFrame()
visa["job_id"] = jobs["job_id"]

visa["visa_sponsorship"] = text.str.contains(
    r"visa sponsorship|sponsorship available|482 visa|491 visa|494 visa|"
    r"employer sponsored|employer-sponsored|sponsor visa|"
    r"sponsor available|we sponsor|can sponsor|will sponsor",
    regex=True,
    na=False
)

visa["work_rights_required"] = text.str.contains(
    r"full working rights|working rights|valid work rights|"
    r"must have work rights|right to work|eligible to work|"
    r"australian work rights|permanent work rights",
    regex=True,
    na=False
)

visa["citizenship_required"] = text.str.contains(
    r"australian citizen|australian citizenship|citizen only|"
    r"permanent resident|pr only|citizenship required",
    regex=True,
    na=False
)

visa["security_clearance_required"] = text.str.contains(
    r"security clearance|baseline clearance|nv1|nv2|"
    r"negative vetting|agsva|government clearance",
    regex=True,
    na=False
)

# ==========================
# Merge with existing features
# ==========================

features = features.drop(
    columns=[c for c in visa.columns if c != "job_id"],
    errors="ignore"
)

features = features.merge(
    visa,
    on="job_id",
    how="left"
)

# ==========================
# Save
# ==========================

features.to_sql(
    "jobs_features",
    engine,
    if_exists="replace",
    index=False
)

print("Visa features added successfully.")