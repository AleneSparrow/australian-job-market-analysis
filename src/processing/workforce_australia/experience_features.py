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
# Experience patterns
# ==========================

text = (
    jobs["title"].fillna("") + " " +
    jobs["description_clean"].fillna("")
).str.lower()

patterns = {
    "graduate": r"\bgraduate\b|\bgraduate program\b",
    "entry": r"\bentry[- ]?level\b",
    "junior": r"\bjunior\b|\bjr\b",
    "mid": r"\bmid[- ]?level\b|\bintermediate\b",
    "senior": r"\bsenior\b|\bsr\b",
    "lead": r"\blead\b|\bteam lead\b|\btechnical lead\b",
    "principal": r"\bprincipal\b",
    "staff": r"\bstaff engineer\b",
    "manager": r"\bengineering manager\b|\bdata manager\b|\bit manager\b"
}

experience = pd.DataFrame()
experience["job_id"] = jobs["job_id"]

for column, pattern in patterns.items():
    experience[column] = text.str.contains(pattern, regex=True, na=False)

# ==========================
# Merge with existing features
# ==========================

features = features.drop(
    columns=[c for c in experience.columns if c != "job_id"],
    errors="ignore"
)

features = features.merge(
    experience,
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

print("Experience features added successfully.")