import csv
import json
import os
import time
from datetime import datetime
from pathlib import Path

import requests
from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"
INTERIM_DATA_DIR = PROJECT_ROOT / "data" / "interim"

load_dotenv(PROJECT_ROOT / ".env")


SEARCH_TERMS = [
    "data analyst",
    "junior data analyst",
    "graduate data analyst",
    "business analyst",
    "business intelligence analyst",
    "bi analyst",
    "reporting analyst",
    "insights analyst",
    "analytics consultant",
    "data reporting analyst",
    "digital analyst",
    "product analyst",
    "customer insights analyst",
    "workforce analyst",
]

RESULTS_PER_PAGE = 50
PAGES_PER_SEARCH_TERM = 5
REQUEST_DELAY_SECONDS = 3


def fetch_jobs(app_id, app_key, search_term, page):
    url = f"https://api.adzuna.com/v1/api/jobs/au/search/{page}"

    params = {
        "app_id": app_id,
        "app_key": app_key,
        "results_per_page": RESULTS_PER_PAGE,
        "what": search_term,
        "content-type": "application/json",
    }

    response = requests.get(
        url,
        params=params,
        timeout=30,
    )

    response.raise_for_status()

    return response.json()


def prepare_rows(data, search_term, page_number):
    rows = []

    for job in data.get("results", []):
        company = job.get("company") or {}
        location = job.get("location") or {}
        category = job.get("category") or {}

        rows.append(
            {
                "job_id": job.get("id"),
                "job_title": job.get("title"),
                "company": company.get("display_name"),
                "location": location.get("display_name"),
                "category": category.get("label"),
                "description": job.get("description"),
                "created": job.get("created"),
                "salary_min": job.get("salary_min"),
                "salary_max": job.get("salary_max"),
                "contract_time": job.get("contract_time"),
                "contract_type": job.get("contract_type"),
                "redirect_url": job.get("redirect_url"),
                "search_term": search_term,
                "api_page": page_number,
                "collection_date": datetime.now().date().isoformat(),
                "source": "Adzuna API",
            }
        )

    return rows


def create_deduplication_key(row):
    job_id = row.get("job_id")

    if job_id:
        return f"id:{job_id}"

    fallback_values = [
        row.get("job_title"),
        row.get("company"),
        row.get("location"),
        row.get("redirect_url"),
    ]

    normalized_values = [
        str(value or "").strip().lower()
        for value in fallback_values
    ]

    return "fallback:" + "|".join(normalized_values)


def deduplicate_rows(rows):
    unique_rows = {}

    for row in rows:
        key = create_deduplication_key(row)

        if key not in unique_rows:
            row["matched_search_terms"] = row["search_term"]
            unique_rows[key] = row
            continue

        existing_row = unique_rows[key]

        existing_terms = set(
            existing_row["matched_search_terms"].split(" | ")
        )

        existing_terms.add(row["search_term"])

        existing_row["matched_search_terms"] = " | ".join(
            sorted(existing_terms)
        )

    return list(unique_rows.values())


def safe_filename(value):
    return (
        value.strip()
        .lower()
        .replace(" ", "_")
        .replace("/", "_")
    )


def save_json(data, path):
    with path.open("w", encoding="utf-8") as file:
        json.dump(
            data,
            file,
            ensure_ascii=False,
            indent=2,
        )


def save_csv(rows, path):
    if not rows:
        raise ValueError("API не вернул вакансии.")

    with path.open(
        "w",
        encoding="utf-8-sig",
        newline="",
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=rows[0].keys(),
        )

        writer.writeheader()
        writer.writerows(rows)


def main():
    app_id = os.getenv("ADZUNA_APP_ID")
    app_key = os.getenv("ADZUNA_APP_KEY")

    if not app_id or not app_key:
        raise ValueError(
            "Не найдены ADZUNA_APP_ID или ADZUNA_APP_KEY. "
            "Проверь файл .env."
        )

    RAW_DATA_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    INTERIM_DATA_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    run_stamp = datetime.now().strftime(
        "%Y-%m-%d_%H-%M-%S"
    )

    total_requests = (
        len(SEARCH_TERMS)
        * PAGES_PER_SEARCH_TERM
    )

    request_number = 0
    all_rows = []

    print("НАЧАЛО СБОРА")
    print("============")
    print(f"Поисковых запросов: {len(SEARCH_TERMS)}")
    print(f"Страниц на запрос: {PAGES_PER_SEARCH_TERM}")
    print(f"Максимум API-запросов: {total_requests}")

    for search_term in SEARCH_TERMS:
        print()
        print(f"ПОИСКОВЫЙ ЗАПРОС: {search_term}")
        print("-" * 50)

        for page in range(
            1,
            PAGES_PER_SEARCH_TERM + 1,
        ):
            request_number += 1

            print(
                f"Запрос {request_number}/{total_requests}: "
                f"страница {page}"
            )

            data = fetch_jobs(
                app_id=app_id,
                app_key=app_key,
                search_term=search_term,
                page=page,
            )

            jobs = data.get("results", [])

            print(f"Получено вакансий: {len(jobs)}")

            raw_filename = (
                f"adzuna_{safe_filename(search_term)}_"
                f"{run_stamp}_page_{page:02d}.json"
            )

            raw_path = RAW_DATA_DIR / raw_filename

            save_json(
                data=data,
                path=raw_path,
            )

            page_rows = prepare_rows(
                data=data,
                search_term=search_term,
                page_number=page,
            )

            all_rows.extend(page_rows)

            if not jobs:
                print(
                    "Пустая страница. "
                    "Переходим к следующему запросу."
                )
                break

            if request_number < total_requests:
                time.sleep(REQUEST_DELAY_SECONDS)

    landing_rows = all_rows

    csv_path = (
        INTERIM_DATA_DIR
        / f"adzuna_landing_raw_{run_stamp}.csv"
    )

    save_csv(
        rows=landing_rows,
        path=csv_path,
    )

    print()
    print("МАССОВЫЙ СБОР ЗАВЕРШЁН")
    print("=======================")
    print(f"Сохранено сырых строк: {len(landing_rows)}")
    print("Дубли намеренно сохранены для последующей обработки в SQL.")
    print(f"Landing CSV сохранён: {csv_path}")


if __name__ == "__main__":
    main()
