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
    "SELECT job_id FROM jobs_unified",
    engine
)

features = pd.read_sql(
    "SELECT * FROM jobs_features",
    engine
)

print("\n==============================")
print("DATA QUALITY CHECK")
print("==============================\n")

# ==========================
# Row count
# ==========================

print("Rows in jobs_unified :", len(jobs))
print("Rows in jobs_features:", len(features))

if len(jobs) == len(features):
    print("✓ Row count matches")
else:
    print("✗ Row count mismatch")

# ==========================
# Duplicate job_id
# ==========================

duplicates = features["job_id"].duplicated().sum()

print("\nDuplicate job_id:", duplicates)

# ==========================
# Missing job_id
# ==========================

missing = features["job_id"].isna().sum()

print("Missing job_id:", missing)

# ==========================
# Missing values
# ==========================

print("\n==============================")
print("MISSING VALUES")
print("==============================")

missing_values = features.isna().sum()

for column, value in missing_values.items():
    if value > 0:
        print(f"{column:<35} {value}")

# ==========================
# Boolean features
# ==========================

print("\n==============================")
print("BOOLEAN FEATURES")
print("==============================")

boolean_columns = [
    column
    for column in features.columns
    if features[column].dtype == bool
]

for column in boolean_columns:

    true_count = int(features[column].sum())
    false_count = len(features) - true_count

    print(
        f"{column:<35}"
        f"TRUE: {true_count:<8}"
        f"FALSE: {false_count}"
    )

# ==========================
# Skill coverage
# ==========================

skills = [
    "python",
    "sql",
    "excel",
    "tableau",
    "power_bi",
    "aws",
    "azure",
    "gcp",
    "docker",
    "kubernetes",
    "git",
    "linux",
    "terraform",
    "snowflake",
    "databricks",
    "spark",
    "pandas",
    "numpy",
    "tensorflow",
    "pytorch"
]

features["skills_found"] = features[skills].sum(axis=1)

print("\n==============================")
print("SKILLS")
print("==============================")

print(
    "Vacancies without skills:",
    (features["skills_found"] == 0).sum()
)

print(
    "Vacancies with skills:",
    (features["skills_found"] > 0).sum()
)

print(
    "Average skills per vacancy:",
    round(features["skills_found"].mean(), 2)
)

# ==========================
# Experience coverage
# ==========================

experience = [
    "graduate",
    "entry",
    "junior",
    "mid",
    "senior",
    "lead",
    "principal",
    "staff",
    "manager"
]

features["experience_found"] = features[experience].sum(axis=1)

print("\n==============================")
print("EXPERIENCE")
print("==============================")

print(
    "Without experience level:",
    (features["experience_found"] == 0).sum()
)

print(
    "With experience level:",
    (features["experience_found"] > 0).sum()
)

print(
    "Multiple experience levels:",
    (features["experience_found"] > 1).sum()
)

# ==========================
# Remote type
# ==========================

print("\n==============================")
print("REMOTE TYPE")
print("==============================")

print(features["remote_type"].value_counts())

print("\n==============================")
print("QUALITY CHECK COMPLETED")
print("==============================")