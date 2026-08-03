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
    SELECT job_id, description_clean,title
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
# Education features
# ==========================

education = pd.DataFrame()
education["job_id"] = jobs["job_id"]

education["bachelor_required"] = text.str.contains(
    r"bachelor|bachelor's degree|undergraduate degree|degree qualified",
    regex=True,
    na=False
)

education["master_required"] = text.str.contains(
    r"master|master's degree|masters degree",
    regex=True,
    na=False
)

education["phd_required"] = text.str.contains(
    r"\bphd\b|doctorate|doctoral degree",
    regex=True,
    na=False
)

education["certification_required"] = text.str.contains(
    r"certification required|required certification|industry certification|professional certification",
    regex=True,
    na=False
)

education["aws_certification"] = text.str.contains(
    r"aws certified|aws certification|aws certified solutions architect|aws developer associate",
    regex=True,
    na=False
)

education["azure_certification"] = text.str.contains(
    r"azure certification|microsoft certified: azure|az-900|az-104|az-305",
    regex=True,
    na=False
)

education["security_certification"] = text.str.contains(
    r"cissp|cism|security\+|comptia security\+|ceh|oscp",
    regex=True,
    na=False
)

# ==========================
# Merge with existing features
# ==========================

features = features.drop(
    columns=[c for c in education.columns if c != "job_id"],
    errors="ignore"
)

features = features.merge(
    education,
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

print("Education features added successfully.")