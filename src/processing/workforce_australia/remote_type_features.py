import pandas as pd
from sqlalchemy import create_engine, text

engine = create_engine(
    "postgresql+psycopg2://postgres:7851@localhost:5432/australian_job_market"
)

jobs = pd.read_sql(
    "SELECT job_id, description_clean, title FROM jobs_unified",
    engine
)

text = (
    jobs["title"].fillna("") + " " +
    jobs["description_clean"].fillna("")
).str.lower()

is_hybrid = text.str.contains(r"\bhybrid\b", regex=True, na=False)
is_remote = text.str.contains(r"\bremote\b|\bwork from home\b|\bwfh\b", regex=True, na=False)
is_onsite = text.str.contains(r"\bon[- ]?site\b|\bin[- ]?office\b|\bin[- ]?person\b", regex=True, na=False)

def classify(h, r, o):
    if h:
        return "hybrid"
    if r:
        return "remote"
    if o:
        return "onsite"
    return None

remote_type = pd.DataFrame({"job_id": jobs["job_id"]})
remote_type["remote_type"] = [
    classify(h, r, o) for h, r, o in zip(is_hybrid, is_remote, is_onsite)
]

from sqlalchemy import text

# ==========================
# Update database
# ==========================

update_df = remote_type.dropna(subset=["remote_type"])

with engine.begin() as conn:
    for _, row in update_df.iterrows():
        conn.execute(
            text("UPDATE jobs_unified SET remote_type = :remote_type WHERE job_id = :job_id"),
            {"remote_type": row["remote_type"], "job_id": row["job_id"]}
        )

print(f"Updated {len(update_df)} rows with remote_type.")
