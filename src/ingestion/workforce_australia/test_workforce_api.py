from __future__ import annotations

import json
from pathlib import Path

import requests


PROJECT_ROOT = Path(__file__).resolve().parents[3]

OUTPUT_DIR = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "workforce_australia"
    / "api_test"
)

API_URL = (
    "https://www.workforceaustralia.gov.au/"
    "api/v1/global/vacancies/"
)

PARAMS = {
    "searchText": "data analyst",
    "pageNumber": 1,
    "pageSize": 20,
}

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 "
        "(KHTML, like Gecko) "
        "Chrome/126.0 Safari/537.36"
    ),
    "Accept": "application/json",
    "Accept-Language": "en-AU,en;q=0.9",
    "Referer": (
        "https://www.workforceaustralia.gov.au/"
        "individuals/jobs/search"
    ),
}


def describe_value(name: str, value: object) -> None:
    print(f"\n{name}:")

    if isinstance(value, list):
        print(f"  тип: list")
        print(f"  элементов: {len(value)}")

        if value:
            first_item = value[0]
            print(f"  тип первого элемента: {type(first_item).__name__}")

            if isinstance(first_item, dict):
                print("  ключи первого элемента:")

                for key in first_item:
                    print(f"    - {key}")

    elif isinstance(value, dict):
        print("  тип: dict")
        print("  ключи:")

        for key in value:
            print(f"    - {key}")

    else:
        print(f"  тип: {type(value).__name__}")
        print(f"  значение: {value}")


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print("Отправляю запрос:")
    print(API_URL)
    print("Параметры:", PARAMS)

    response = requests.get(
        API_URL,
        params=PARAMS,
        headers=HEADERS,
        timeout=60,
    )

    print("\nHTTP status:", response.status_code)
    print("Content-Type:", response.headers.get("Content-Type"))
    print("Финальный URL:", response.url)
    print("Размер ответа:", len(response.content), "байт")

    response.raise_for_status()

    try:
        data = response.json()
    except requests.JSONDecodeError as error:
        raw_path = OUTPUT_DIR / "response_not_json.txt"
        raw_path.write_text(response.text, encoding="utf-8")

        raise RuntimeError(
            f"Ответ не является JSON. Сохранён в {raw_path}"
        ) from error

    output_path = OUTPUT_DIR / "data_analyst_page_1.json"

    output_path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print("\nJSON сохранён:")
    print(output_path)

    print("\nТип ответа:", type(data).__name__)

    if isinstance(data, dict):
        print("\nКлючи верхнего уровня:")

        for key, value in data.items():
            print(f"- {key}: {type(value).__name__}")

        print("\nПодробная структура:")

        for key, value in data.items():
            describe_value(key, value)

    elif isinstance(data, list):
        print("Количество элементов:", len(data))

        if data and isinstance(data[0], dict):
            print("\nКлючи первой вакансии:")

            for key in data[0]:
                print("-", key)

    print("\nТест API завершён успешно.")


if __name__ == "__main__":
    main()
