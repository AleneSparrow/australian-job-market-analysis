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
# Experience patterns
# ==========================

text = (
    jobs["title"].fillna("") + " " +
    jobs["description_clean"].fillna("")
).str.lower()

# Паттерны сужены там, где слово часто встречается вне контекста грейда
# (lead generation, sales leads, leadership skills и т.п.)
patterns = {
    "graduate": r"\bgraduate\b|\bgraduate program\b",
    "entry": r"\bentry[- ]?level\b",
    "junior": r"\bjunior\b|\bjr\b",
    "mid": r"\bmid[- ]?level\b|\bintermediate\b",
    "senior": r"\bsenior\b|\bsr\b",
    "lead": r"\bteam lead\b|\btechnical lead\b|\btech lead\b|\blead engineer\b|\blead developer\b|\blead analyst\b",
    "principal": r"\bprincipal engineer\b|\bprincipal consultant\b|\bprincipal analyst\b|\bprincipal\b(?!\s+(officer|house))",
    "staff": r"\bstaff engineer\b",
    "manager": r"\bengineering manager\b|\bdata manager\b|\bit manager\b"
}

experience = pd.DataFrame()
experience["job_id"] = jobs["job_id"]

for column, pattern in patterns.items():
    experience[column] = text.str.contains(pattern, regex=True, na=False)

# ==========================
# Единый уровень опыта (без противоречий)
# Чем выше в списке — тем выше приоритет при совпадении нескольких грейдов
# ==========================

level_priority = [
    "staff", "principal", "lead", "manager",
    "senior", "mid", "junior", "entry", "graduate"
]

def pick_level(row):
    for level in level_priority:
        if row[level]:
            return level
    return None

experience["experience_level"] = experience.apply(pick_level, axis=1)

# ==========================
# Merge with existing features
# ==========================

# Убираем старые версии этих колонок (включая experience_level, если уже была)
cols_to_replace = [c for c in experience.columns if c != "job_id"]
features = features.drop(columns=cols_to_replace, errors="ignore")

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

print("Experience features updated successfully — no more overlapping levels.")
