import re
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parent.parent
INTERIM_DATA_DIR = PROJECT_ROOT / "data" / "interim"
REPORTS_DIR = PROJECT_ROOT / "reports"


ROLE_PATTERNS = {
    "Data Analyst": [
        r"\bdata analyst\b",
        r"\bdata and reporting analyst\b",
        r"\bdata & reporting analyst\b",
        r"\bdata analytics analyst\b",
    ],
    "Business Analyst": [
        r"\bbusiness analyst\b",
        r"\bict business analyst\b",
        r"\btechnical business analyst\b",
        r"\bsystems business analyst\b",
    ],
    "BI / Reporting Analyst": [
        r"\bbi analyst\b",
        r"\bbusiness intelligence analyst\b",
        r"\breporting analyst\b",
        r"\bperformance analyst\b",
    ],
    "Insights Analyst": [
        r"\binsights analyst\b",
        r"\binsight analyst\b",
        r"\bpeople data.*insights analyst\b",
    ],
    "Analytics Consultant": [
        r"\banalytics consultant\b",
        r"\bdata consultant\b",
        r"\bdata & analytics.*consultant\b",
        r"\bdata and analytics.*consultant\b",
    ],
}


CLEARLY_IRRELEVANT_PATTERNS = [
    r"\bsales\b",
    r"\baccount executive\b",
    r"\bsoftware engineer\b",
    r"\bdata engineer\b",
    r"\bmachine learning engineer\b",
    r"\bhead of\b",
    r"\bdirector\b",
    r"\bdeveloper\b",
    r"\bproduct manager\b",
    r"\bproject manager\b",
    r"\brecruiter\b",
]


SENIORITY_PATTERNS = {
    "Junior": [
        r"\bjunior\b",
        r"\bgraduate\b",
        r"\bentry level\b",
        r"\bassociate analyst\b",
    ],
    "Senior": [
        r"\bsenior\b",
        r"\blead\b",
        r"\bprincipal\b",
        r"\bmanager\b",
        r"\bdirector\b",
        r"\bhead of\b",
    ],
}


def find_latest_csv():
    csv_files = list(
        INTERIM_DATA_DIR.glob("adzuna_multiple_roles_*.csv")
    )

    if not csv_files:
        raise FileNotFoundError(
            "Не найден файл adzuna_multiple_roles_*.csv "
            "в папке data/interim."
        )

    return max(
        csv_files,
        key=lambda path: path.stat().st_mtime,
    )


def normalize_title(title):
    if pd.isna(title):
        return ""

    normalized = str(title).lower().strip()
    normalized = re.sub(r"\s+", " ", normalized)

    return normalized


def classify_role_family(normalized_title):
    matched_families = []

    for role_family, patterns in ROLE_PATTERNS.items():
        if any(
            re.search(pattern, normalized_title)
            for pattern in patterns
        ):
            matched_families.append(role_family)

    if len(matched_families) == 1:
        return matched_families[0]

    if len(matched_families) > 1:
        return "Multiple analyst families"

    return "Other"


def classify_relevance(normalized_title, role_family):
    has_irrelevant_pattern = any(
        re.search(pattern, normalized_title)
        for pattern in CLEARLY_IRRELEVANT_PATTERNS
    )

    if role_family == "Other" and has_irrelevant_pattern:
        return "irrelevant"

    if role_family == "Other":
        return "review"

    if has_irrelevant_pattern:
        return "review"

    return "relevant"


def classify_seniority(normalized_title):
    for level, patterns in SENIORITY_PATTERNS.items():
        if any(
            re.search(pattern, normalized_title)
            for pattern in patterns
        ):
            return level

    return "Not specified"


def main():
    source_file = find_latest_csv()

    print(f"Классифицирую файл: {source_file.name}")

    df = pd.read_csv(source_file)

    df["normalized_job_title"] = (
        df["job_title"]
        .apply(normalize_title)
    )

    df["role_family"] = (
        df["normalized_job_title"]
        .apply(classify_role_family)
    )

    df["relevance_status"] = df.apply(
        lambda row: classify_relevance(
            row["normalized_job_title"],
            row["role_family"],
        ),
        axis=1,
    )

    df["seniority_level"] = (
        df["normalized_job_title"]
        .apply(classify_seniority)
    )

    output_file = (
        INTERIM_DATA_DIR
        / "jobs_with_title_classification.csv"
    )

    df.to_csv(
        output_file,
        index=False,
        encoding="utf-8-sig",
    )

    relevance_counts = (
        df["relevance_status"]
        .value_counts()
    )

    role_family_counts = (
        df["role_family"]
        .value_counts()
    )

    seniority_counts = (
        df["seniority_level"]
        .value_counts()
    )

    review_titles = (
        df.loc[
            df["relevance_status"].isin(
                ["review", "irrelevant"]
            ),
            [
                "job_title",
                "company",
                "search_term",
                "role_family",
                "relevance_status",
            ],
        ]
        .sort_values(
            ["relevance_status", "job_title"]
        )
    )

    review_file = (
        REPORTS_DIR
        / "titles_for_manual_review.csv"
    )

    REPORTS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    review_titles.to_csv(
        review_file,
        index=False,
        encoding="utf-8-sig",
    )

    report = f"""
JOB TITLE CLASSIFICATION REPORT
===============================

Source file:
{source_file.name}

TOTAL ROWS
----------
{len(df)}

RELEVANCE STATUS
----------------
{relevance_counts.to_string()}

ROLE FAMILIES
-------------
{role_family_counts.to_string()}

SENIORITY LEVELS
----------------
{seniority_counts.to_string()}

OUTPUT FILES
------------
Classified dataset:
{output_file.name}

Manual review list:
{review_file.name}
"""

    report_path = (
        REPORTS_DIR
        / "job_title_classification_report.txt"
    )

    report_path.write_text(
        report,
        encoding="utf-8",
    )

    print(report)
    print(
        "Важно: строки пока не удалены. "
        "К ним только добавлена классификация."
    )


if __name__ == "__main__":
    main()
