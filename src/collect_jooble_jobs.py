from __future__ import annotations

import csv
import json
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Any

import requests
from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw" / "jooble"
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

LOCATION = "Australia"
RESULTS_PER_PAGE = 20
MAX_PAGES_PER_SEARCH_TERM = 10
REQUEST_DELAY_SECONDS = 2


def safe_filename(value: str) -> str:
    return (
        value.strip()
        .lower()
        .replace(" ", "_")
        .replace("/", "_")
    )


def fetch_jobs(
    api_key: str,
    search_term: str,
    page: int,
) -> dict[str, Any]:
    url = f"https://jooble.org/api/{api_key}"

    payload = {
        "keywords": search_term,
        "location": LOCATION,
        "page": str(page),
        "ResultOnPage": str(RESULTS_PER_PAGE),
        "companysearch": "false",
    }

    response = requests.post(
        url,
        json=payload,
        timeout=30,
    )

    response.raise_for_status()
    return response.json()


def save_json(data: dict[str, Any], path: Path) -> None:
    path.write_text(
        json.dumps(
            data,
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )


def prepare_rows(
    data: dict[str, Any],
    search_term: str,
    page_number: int,
    collection_timestamp: str,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []

    for job in data.get("jobs", []):
        rows.append(
            {
                "job_id": job.get("id"),
                "job_title": job.get("title"),
                "company": job.get("company"),
                "location": job.get("location"),
                "description": job.get("snippet"),
                "salary_text": job.get("salary"),
                "employment_type": job.get("type"),
                "original_source": job.get("source"),
                "updated": job.get("updated"),
                "job_url": job.get("link"),
                "search_term": search_term,
                "api_page": page_number,
                "collection_timestamp": collection_timestamp,
                "source": "Jooble API",
            }
        )

    return rows


def save_csv(rows: list[dict[str, Any]], path: Path) -> None:
    if not rows:
        raise ValueError("Jooble API не вернул вакансий.")

    with path.open(
        "w",
        encoding="utf-8-sig",
        newline="",
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=list(rows[0].keys()),
        )
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    api_key = os.getenv("JOOBLE_API_KEY", "").strip()

    if not api_key:
        raise ValueError(
            "JOOBLE_API_KEY не найден в .env"
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
    collection_timestamp = datetime.now().isoformat(
        timespec="seconds"
    )

    all_rows: list[dict[str, Any]] = []
    request_number = 0

    print("МАССОВЫЙ СБОР JOOBLE")
    print("=====================")
    print(f"Поисковых запросов: {len(SEARCH_TERMS)}")
    print(
        "Максимум страниц на запрос: "
        f"{MAX_PAGES_PER_SEARCH_TERM}"
    )
    print()

    for search_term in SEARCH_TERMS:
        print(f"ПОИСКОВЫЙ ЗАПРОС: {search_term}")
        print("-" * 50)

        collected_for_term = 0

        for page in range(
            1,
            MAX_PAGES_PER_SEARCH_TERM + 1,
        ):
            request_number += 1

            print(
                f"Запрос {request_number}: "
                f"страница {page}"
            )

            try:
                data = fetch_jobs(
                    api_key=api_key,
                    search_term=search_term,
                    page=page,
                )
            except requests.RequestException as error:
                print(f"Ошибка API: {error}")
                break

            jobs = data.get("jobs", [])
            total_count = int(
                data.get("totalCount") or 0
            )

            print(
                f"Получено вакансий: {len(jobs)}; "
                f"всего найдено: {total_count}"
            )

            raw_filename = (
                f"jooble_{safe_filename(search_term)}_"
                f"{run_stamp}_page_{page:02d}.json"
            )

            save_json(
                data=data,
                path=RAW_DATA_DIR / raw_filename,
            )

            page_rows = prepare_rows(
                data=data,
                search_term=search_term,
                page_number=page,
                collection_timestamp=collection_timestamp,
            )

            all_rows.extend(page_rows)
            collected_for_term += len(page_rows)

            if not jobs:
                print("Пустая страница.")
                break

            if collected_for_term >= total_count:
                print(
                    "Все доступные результаты "
                    "по запросу получены."
                )
                break

            time.sleep(REQUEST_DELAY_SECONDS)

        print()

    output_path = (
        INTERIM_DATA_DIR
        / f"jooble_landing_raw_{run_stamp}.csv"
    )

    save_csv(
        rows=all_rows,
        path=output_path,
    )

    print("СБОР JOOBLE ЗАВЕРШЁН")
    print("=====================")
    print(f"Сохранено сырых строк: {len(all_rows):,}")
    print(
        "Дубли намеренно сохранены "
        "для последующей обработки в SQL."
    )
    print(f"Landing CSV сохранён: {output_path}")


if __name__ == "__main__":
    main()
