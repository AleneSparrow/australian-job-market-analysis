from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parent.parent
INTERIM_DATA_DIR = PROJECT_ROOT / "data" / "interim"
PROCESSED_DATA_DIR = PROJECT_ROOT / "data" / "processed"
REPORTS_DIR = PROJECT_ROOT / "reports"


def find_classified_dataset():
    file_path = (
        INTERIM_DATA_DIR
        / "jobs_with_title_classification.csv"
    )

    if not file_path.exists():
        raise FileNotFoundError(
            "Не найден файл "
            "data/interim/jobs_with_title_classification.csv."
        )

    return file_path


def find_manual_review_file():
    file_path = (
        REPORTS_DIR
        / "titles_manual_review_completed.csv"
    )

    if not file_path.exists():
        raise FileNotFoundError(
            "Не найден файл "
            "reports/titles_manual_review_completed.csv."
        )

    return file_path


def normalize_text_column(series):
    return (
        series
        .fillna("")
        .astype(str)
        .str.strip()
    )


def main():
    classified_path = find_classified_dataset()
    review_path = find_manual_review_file()

    print(f"Основной файл: {classified_path.name}")
    print(f"Ручная проверка: {review_path.name}")

    jobs = pd.read_csv(classified_path)
    manual_review = pd.read_csv(review_path)

    required_columns = {
        "job_title",
        "company",
        "search_term",
        "manual_decision",
        "manual_reason",
    }

    missing_columns = (
        required_columns
        - set(manual_review.columns)
    )

    if missing_columns:
        raise ValueError(
            "В файле ручной проверки отсутствуют колонки: "
            + ", ".join(sorted(missing_columns))
        )

    allowed_decisions = {
        "keep",
        "remove",
        "review",
    }

    manual_review["manual_decision"] = (
        normalize_text_column(
            manual_review["manual_decision"]
        )
        .str.lower()
    )

    invalid_decisions = set(
        manual_review.loc[
            ~manual_review["manual_decision"].isin(
                allowed_decisions
            ),
            "manual_decision",
        ]
    )

    invalid_decisions.discard("")

    if invalid_decisions:
        raise ValueError(
            "Найдены неправильные manual_decision: "
            + ", ".join(sorted(invalid_decisions))
        )

    merge_keys = [
        "job_title",
        "company",
        "search_term",
    ]

    for column in merge_keys:
        jobs[column] = normalize_text_column(
            jobs[column]
        )

        manual_review[column] = normalize_text_column(
            manual_review[column]
        )

    manual_review = manual_review[
        merge_keys
        + [
            "manual_decision",
            "manual_reason",
        ]
    ].drop_duplicates(
        subset=merge_keys,
        keep="last",
    )

    merged = jobs.merge(
        manual_review,
        on=merge_keys,
        how="left",
        validate="many_to_one",
    )

    merged["final_decision"] = (
        merged["manual_decision"]
    )

    automatic_keep_mask = (
        merged["manual_decision"].isna()
        & (
            merged["relevance_status"]
            == "relevant"
        )
    )

    automatic_remove_mask = (
        merged["manual_decision"].isna()
        & (
            merged["relevance_status"]
            == "irrelevant"
        )
    )

    automatic_review_mask = (
        merged["manual_decision"].isna()
        & (
            merged["relevance_status"]
            == "review"
        )
    )

    merged.loc[
        automatic_keep_mask,
        "final_decision",
    ] = "keep"

    merged.loc[
        automatic_remove_mask,
        "final_decision",
    ] = "remove"

    merged.loc[
        automatic_review_mask,
        "final_decision",
    ] = "review"

    unresolved = merged[
        merged["final_decision"] == "review"
    ].copy()

    clean_jobs = merged[
        merged["final_decision"] == "keep"
    ].copy()

    removed_jobs = merged[
        merged["final_decision"] == "remove"
    ].copy()

    clean_jobs = clean_jobs.drop_duplicates(
        subset=["job_id"],
        keep="first",
    )

    PROCESSED_DATA_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    REPORTS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    clean_path = (
        PROCESSED_DATA_DIR
        / "jobs_clean.csv"
    )

    removed_path = (
        REPORTS_DIR
        / "removed_jobs.csv"
    )

    unresolved_path = (
        REPORTS_DIR
        / "unresolved_jobs.csv"
    )

    clean_jobs.to_csv(
        clean_path,
        index=False,
        encoding="utf-8-sig",
    )

    removed_jobs.to_csv(
        removed_path,
        index=False,
        encoding="utf-8-sig",
    )

    unresolved.to_csv(
        unresolved_path,
        index=False,
        encoding="utf-8-sig",
    )

    report = f"""
MANUAL REVIEW APPLICATION REPORT
================================

INPUT DATA
----------
Total classified rows: {len(jobs)}
Manual review rows: {len(manual_review)}

FINAL DECISIONS
---------------
Kept rows: {len(clean_jobs)}
Removed rows: {len(removed_jobs)}
Unresolved rows: {len(unresolved)}

OUTPUT FILES
------------
Clean dataset:
{clean_path}

Removed jobs:
{removed_path}

Unresolved jobs:
{unresolved_path}
"""

    report_path = (
        REPORTS_DIR
        / "manual_review_application_report.txt"
    )

    report_path.write_text(
        report,
        encoding="utf-8",
    )

    print(report)

    if len(unresolved) > 0:
        print(
            "Внимание: остались вакансии со статусом review. "
            "Они не вошли в jobs_clean.csv."
        )


if __name__ == "__main__":
    main()
