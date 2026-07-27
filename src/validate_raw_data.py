from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parent.parent
INTERIM_DATA_DIR = PROJECT_ROOT / "data" / "interim"
REPORTS_DIR = PROJECT_ROOT / "reports"


def main():
    csv_files = list(
        INTERIM_DATA_DIR.glob("adzuna_data_analyst_*.csv")
    )

    if not csv_files:
        raise FileNotFoundError(
            "В папке data/interim не найден CSV-файл Adzuna."
        )

    latest_file = max(
        csv_files,
        key=lambda path: path.stat().st_mtime
    )

    print(f"Проверяю файл: {latest_file.name}")

    df = pd.read_csv(latest_file)

    total_rows = len(df)
    total_columns = len(df.columns)

    duplicate_job_ids = df["job_id"].duplicated().sum()

    missing_values = (
        df.isna()
        .sum()
        .sort_values(ascending=False)
    )

    missing_salary = (
        df["salary_min"].isna()
        & df["salary_max"].isna()
    ).sum()

    unique_titles = df["job_title"].nunique()
    unique_companies = df["company"].nunique()
    unique_locations = df["location"].nunique()

    top_titles = df["job_title"].value_counts().head(10)
    top_companies = df["company"].value_counts().head(10)
    top_locations = df["location"].value_counts().head(10)

    salary_missing_percentage = (
        missing_salary / total_rows * 100
        if total_rows
        else 0
    )

    report = f"""
RAW DATA VALIDATION REPORT
==========================

Source file:
{latest_file.name}

DATASET SIZE
------------
Rows: {total_rows}
Columns: {total_columns}

UNIQUENESS
----------
Duplicate job IDs: {duplicate_job_ids}
Unique job titles: {unique_titles}
Unique companies: {unique_companies}
Unique locations: {unique_locations}

SALARY COVERAGE
---------------
Vacancies without salary data: {missing_salary}
Salary missing percentage: {salary_missing_percentage:.1f}%

MISSING VALUES BY COLUMN
------------------------
{missing_values.to_string()}

TOP JOB TITLES
--------------
{top_titles.to_string()}

TOP COMPANIES
-------------
{top_companies.to_string()}

TOP LOCATIONS
-------------
{top_locations.to_string()}
"""

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    report_path = REPORTS_DIR / "raw_data_validation.txt"
    report_path.write_text(report, encoding="utf-8")

    print(report)
    print(f"\nОтчёт сохранён: {report_path}")


if __name__ == "__main__":
    main()
