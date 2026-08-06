import pandas as pd
from sqlalchemy import create_engine

engine = create_engine(
    "postgresql+psycopg2://postgres:7851@localhost:5432/australian_job_market"
)

data = {
    "metric": [
        "Salary Disclosed (%)", "Salary Disclosed (%)",
        "Work Format Disclosed (%)", "Work Format Disclosed (%)",
        "Visa Sponsorship Offered (%)", "Visa Sponsorship Offered (%)",
        "Employer Named (%)", "Employer Named (%)",
        "Senior Share of Ranked Levels (%)", "Senior Share of Ranked Levels (%)",
        "Full-Time Share (%)", "Full-Time Share (%)",
    ],
    "segment": [
        "Overall Market", "IT Segment",
        "Overall Market", "IT Segment",
        "Overall Market", "IT Segment",
        "Overall Market", "IT Segment",
        "Overall Market", "IT Segment",
        "Overall Market", "IT Segment",
    ],
    "value": [1.55, 2.67, 5.8, 13.2, 0.4, 0.16, 12, 16, 92.3, 95.8, 75, 90.5],
    "metric_order": [1, 1, 2, 2, 3, 3, 4, 4, 5, 5, 6, 6],
}

df = pd.DataFrame(data)

df.to_sql(
    "it_vs_market_summary",
    engine,
    if_exists="replace",
    index=False,
)

print("Table created:", len(df), "rows")
