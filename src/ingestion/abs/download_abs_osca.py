from pathlib import Path

import requests


PROJECT_ROOT = Path(__file__).resolve().parents[3]
OUTPUT_DIR = PROJECT_ROOT / "data" / "raw" / "abs" / "osca"

BASE_URL = (
    "https://www.abs.gov.au/statistics/classifications/"
    "osca-occupation-standard-classification-australia/"
    "2024-version-1-0/data-downloads"
)

FILES = {
    "osca_structure.xlsx": f"{BASE_URL}/OSCA%20structure.xlsx",
    "osca_category_descriptions.xlsx": (
        f"{BASE_URL}/OSCA%20Category%20Descriptions.xlsx"
    ),
    "osca_correspondence_tables.xlsx": (
        f"{BASE_URL}/OSCA%20correspondence%20tables%20v2.xlsx"
    ),
    "osca_titles_index.xlsx": (
        f"{BASE_URL}/"
        "OSCA%20index%20of%20principal%20titles%20"
        "alternative%20titles%20and%20specialisations.xlsx"
    ),
}

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}


def download_file(filename: str, url: str) -> None:
    destination = OUTPUT_DIR / filename

    print(f"\nСкачиваю: {filename}")
    print(url)

    response = requests.get(
        url,
        headers=HEADERS,
        timeout=120,
    )
    response.raise_for_status()

    content_type = response.headers.get("Content-Type", "").lower()

    if "spreadsheet" not in content_type and "octet-stream" not in content_type:
        raise RuntimeError(
            f"Вместо Excel получен тип: {content_type}"
        )

    destination.write_bytes(response.content)

    if destination.stat().st_size < 10_000:
        destination.unlink(missing_ok=True)
        raise RuntimeError(
            f"Файл подозрительно маленький: {filename}"
        )

    size_kb = destination.stat().st_size / 1024
    print(f"Готово: {size_kb:.1f} KB")


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    for filename, url in FILES.items():
        download_file(filename, url)

    print("\nВсе файлы OSCA успешно скачаны.")
    print(f"Папка: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
