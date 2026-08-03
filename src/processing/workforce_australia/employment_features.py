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
# Employment features
# ==========================

employment = pd.DataFrame()
employment["job_id"] = jobs["job_id"]

employment["full_time"] = text.str.contains(
    r"full[- ]?time",
    regex=True,
    na=False
)

employment["part_time"] = text.str.contains(
    r"part[- ]?time",
    regex=True,
    na=False
)

employment["contract"] = text.str.contains(
    r"\bcontract\b|fixed[- ]?term",
    regex=True,
    na=False
)

employment["temporary"] = text.str.contains(
    r"\btemporary\b|\btemp\b",
    regex=True,
    na=False
)

employment["casual"] = text.str.contains(
    r"\bcasual\b",
    regex=True,
    na=False
)

employment["internship"] = text.str.contains(
    r"\bintern(ship)?\b",
    regex=True,
    na=False
)

# ==========================
# Merge with existing features
# ==========================

features = features.drop(
    columns=[c for c in employment.columns if c != "job_id"],
    errors="ignore"
)

features = features.merge(
    employment,
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

print("Employment features added successfully.")