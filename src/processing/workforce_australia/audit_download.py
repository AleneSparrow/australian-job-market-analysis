from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd


# Корень проекта:
# australian-job-market-analysis/
PROJECT_ROOT = Path(__file__).resolve().parents[3]

# Папка со всеми JSON Workforce Australia
INPUT_DIR = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "workforce_australia"
)

# Куда сохранить готовую сырую таблицу
OUTPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "interim"
    / "workforce_australia"
    / "workforce_jobs_raw.csv"
)


def find_job_records(data: Any) -> list[dict[str, Any]]:
    """
    Находит список вакансий внутри JSON.

    Сначала проверяет наиболее вероятные названия полей:
    result, results, jobs, items, vacancies.

    Если структура немного отличается, рекурсивно ищет
    вложенный список словарей.
    """

    preferred_keys = (
        "result",
        "results",
        "jobs",
        "items",
        "vacancies",
        "jobResults",
        "searchResults",
    )

    if isinstance(data, dict):
        # Сначала ищем по ожидаемым названиям полей
        for key in preferred_keys:
            value = data.get(key)

            if (
                isinstance(value, list)
                and value
                and all(isinstance(item, dict) for item in value)
            ):
                return value

        # Затем рекурсивно просматриваем все вложенные объекты
        for value in data.values():
            records = find_job_records(value)

            if records:
                return records

    elif isinstance(data, list):
        if data and all(isinstance(item, dict) for item in data):
            return data

        for item in data:
            records = find_job_records(item)

            if records:
                return records

    return []


def prepare_value(value: Any) -> Any:
    """
    Оставляет простые значения как есть.

    Вложенные списки и словари превращает в JSON-текст,
    чтобы они не потерялись при сохранении в CSV.
    """

    if isinstance(value, (dict, list)):
        return json.dumps(
            value,
            ensure_ascii=False,
            sort_keys=True,
        )

    return value


def flatten_job(job: dict[str, Any]) -> dict[str, Any]:
    """
    Разворачивает вложенные словари в плоские столбцы.

    Например:
    location.name -> location.name
    employer.name -> employer.name
    """

    flattened = pd.json_normalize(
        job,
        sep=".",
        max_level=None,
    ).to_dict(orient="records")[0]

    return {
        column: prepare_value(value)
        for column, value in flattened.items()
    }


def main() -> None:
    json_files = sorted(INPUT_DIR.rglob("page_*.json"))

    if not json_files:
        raise FileNotFoundError(
            "Не найдены файлы page_*.json в папке:\n"
            f"{INPUT_DIR}"
        )

    all_rows: list[dict[str, Any]] = []
    files_without_records: list[str] = []

    print(f"Найдено JSON-файлов: {len(json_files)}")

    for file_number, json_file in enumerate(json_files, start=1):
        try:
            with json_file.open(
                "r",
                encoding="utf-8",
            ) as file:
                page_data = json.load(file)

        except (json.JSONDecodeError, OSError) as error:
            print(f"Не удалось прочитать: {json_file}")
            print(f"Ошибка: {error}")
            continue

        job_records = find_job_records(page_data)

        if not job_records:
            files_without_records.append(
                str(json_file.relative_to(PROJECT_ROOT))
            )
            continue

        # Метаданные страницы из оболочки downloader-скрипта
        search_term = page_data.get("search_term")
        page_number = page_data.get("page_number")
        downloaded_at = page_data.get("downloaded_at_utc")
        source = page_data.get("source", "Workforce Australia")

        for position_on_page, job in enumerate(
            job_records,
            start=1,
        ):
            row = flatten_job(job)

            # Добавляем происхождение каждой строки
            row["_source"] = source
            row["_search_term"] = search_term
            row["_page_number"] = page_number
            row["_position_on_page"] = position_on_page
            row["_downloaded_at_utc"] = downloaded_at
            row["_source_file"] = str(
                json_file.relative_to(PROJECT_ROOT)
            )

            all_rows.append(row)

        if file_number % 100 == 0:
            print(
                f"Обработано файлов: {file_number}/{len(json_files)} | "
                f"Извлечено строк: {len(all_rows)}"
            )

    if not all_rows:
        raise RuntimeError(
            "В JSON-файлах не удалось найти ни одной вакансии."
        )

    dataframe = pd.DataFrame(all_rows)

    # Служебные столбцы ставим в начало таблицы
    metadata_columns = [
        "_source",
        "_search_term",
        "_page_number",
        "_position_on_page",
        "_downloaded_at_utc",
        "_source_file",
    ]

    remaining_columns = [
        column
        for column in dataframe.columns
        if column not in metadata_columns
    ]

    dataframe = dataframe[
        metadata_columns + remaining_columns
    ]

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    # utf-8-sig нужен, чтобы Excel нормально открыл текст
    dataframe.to_csv(
        OUTPUT_FILE,
        index=False,
        encoding="utf-8-sig",
    )

    print()
    print("ГОТОВО")
    print(f"JSON-файлов обработано: {len(json_files)}")
    print(f"Строк выгружено: {len(dataframe):,}")
    print(f"Столбцов: {len(dataframe.columns)}")
    print(f"CSV сохранён сюда:\n{OUTPUT_FILE}")

    if files_without_records:
        print()
        print(
            "Файлов без найденных вакансий: "
            f"{len(files_without_records)}"
        )
        print(
            "Это могут быть последние пустые страницы выдачи."
        )


if __name__ == "__main__":
    main()