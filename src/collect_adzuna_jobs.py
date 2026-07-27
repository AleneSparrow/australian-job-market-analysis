import csv
import json
import os
from datetime import datetime
from pathlib import Path

import requests
from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"

load_dotenv(PROJECT_ROOT / ".env")


def fetch_jobs():
    app_id = os.getenv("ADZUNA_APP_ID")
    app_key = os.getenv("ADZUNA_APP_KEY")

    if not app_id or not app_key:
        raise ValueError(
            "Не найдены ADZUNA_APP_ID или ADZUNA_APP_KEY. Проверь файл .env."
        )

    url = "https://api.adzuna.com/v1/api/jobs/au/search/1"

    params = {
        "app_id": app_id,
        "app_key": app_key,
        "results_per_page": 20,
        "what": "data analyst",
        "content-type": "application/json",
    }

    response = requests.get(url, params=params, timeout=30)
    response.raise_for_status()

    return response.json()


def prepare_rows(data):
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
                "search_term": "data analyst",
                "collection_date": datetime.now().date().isoformat(),
                "source": "Adzuna API",
            }
        )

    return rows


def save_json(data, path):
    with path.open("w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)


def save_csv(rows, path):
    if not rows:
        raise ValueError("API не вернул вакансии.")

    with path.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)


def main():
    print("Запрашиваю вакансии Data Analyst...")

    data = fetch_jobs()
    rows = prepare_rows(data)

    RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)

    date_stamp = datetime.now().strftime("%Y-%m-%d")

    json_path = RAW_DATA_DIR / f"adzuna_data_analyst_{date_stamp}.json"
    csv_path = RAW_DATA_DIR / f"adzuna_data_analyst_{date_stamp}.csv"

    save_json(data, json_path)
    save_csv(rows, csv_path)

    print(f"Получено вакансий: {len(rows)}")
    print(f"JSON сохранён: {json_path}")
    print(f"CSV сохранён: {csv_path}")


if __name__ == "__main__":
    main()
