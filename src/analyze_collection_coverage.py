from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parent.parent
INTERIM_DATA_DIR = PROJECT_ROOT / "data" / "interim"
REPORTS_DIR = PROJECT_ROOT / "reports"


def find_latest_csv():
    csv_files = list(
        INTERIM_DATA_DIR.glob("adzuna_multiple_roles_*.csv")
    )

    if not csv_files:
        raise FileNotFoundError(
            "В папке data/interim не найден файл "
            "adzuna_multiple_roles_*.csv."
        )

    return max(
        csv_files,
        key=lambda path: path.stat().st_mtime,
    )


def main():
    latest_file = find_latest_csv()

    print(f"Анализирую файл: {latest_file.name}")

    df = pd.read_csv(latest_file)

    total_rows = len(df)

    search_term_counts = (
        df["search_term"]
        .value_counts()
        .sort_values(ascending=False)
    )

    title_counts = (
        df["job_title"]
        .value_counts()
        .head(30)
    )

    matched_term_counts = (
        df["matched_search_terms"]
        .fillna("")
        .apply(
            lambda value: (
                len(value.split(" | "))
                if value
                else 0
            )
        )
        .value_counts()
        .sort_index()
    )

    multi_match_rows = df[
        df["matched_search_terms"]
        .fillna("")
        .str.contains(r"\|", regex=True)
    ]

    multi_match_count = len(multi_match_rows)

    multi_match_percentage = (
        multi_match_count / total_rows * 100
        if total_rows
        else 0
    )

    most_common_overlaps = (
        multi_match_rows["matched_search_terms"]
        .value_counts()
        .head(20)
    )

    report = f"""
COLLECTION COVERAGE REPORT
==========================

Source file:
{latest_file.name}

DATASET SIZE
------------
Total unique vacancies: {total_rows}

VACANCIES BY PRIMARY SEARCH TERM
--------------------------------
{search_term_counts.to_string()}

NUMBER OF SEARCH TERMS MATCHED PER VACANCY
------------------------------------------
{matched_term_counts.to_string()}

OVERLAP BETWEEN SEARCH TERMS
----------------------------
Vacancies matched by multiple search terms: {multi_match_count}
Multiple-match percentage: {multi_match_percentage:.1f}%

MOST COMMON SEARCH-TERM OVERLAPS
--------------------------------
{most_common_overlaps.to_string()}

TOP 30 ORIGINAL JOB TITLES
--------------------------
{title_counts.to_string()}
"""

    REPORTS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    report_path = (
        REPORTS_DIR
        / "collection_coverage_report.txt"
    )

    report_path.write_text(
        report,
        encoding="utf-8",
    )

    print(report)
    print(f"\nОтчёт сохранён: {report_path}")


if __name__ == "__main__":
    main()
