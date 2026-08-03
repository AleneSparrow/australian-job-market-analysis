from pathlib import Path
import zipfile

import requests


PROJECT_ROOT = Path(__file__).resolve().parents[3]

OUTPUT_DIR = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "abs"
    / "job_vacancies"
)

URL = (
    "https://www.abs.gov.au/statistics/labour/jobs/"
    "job-vacancies-australia/may-2026/"
    "Time-series-spreadsheets-all.zip"
)

ZIP_PATH = OUTPUT_DIR / "abs_job_vacancies_may_2026.zip"
EXTRACT_DIR = OUTPUT_DIR / "may_2026"


def download_file() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print(f"Скачиваю:\n{URL}")
    print(f"\nСохраняю в:\n{ZIP_PATH}")

    response = requests.get(URL, timeout=120)
    response.raise_for_status()

    ZIP_PATH.write_bytes(response.content)

    size_kb = ZIP_PATH.stat().st_size / 1024
    print(f"\nZIP скачан: {size_kb:.1f} KB")


def validate_zip() -> None:
    if not zipfile.is_zipfile(ZIP_PATH):
        raise RuntimeError(
            "Скачанный файл не является корректным ZIP-архивом"
        )

    print("ZIP-архив корректный")


def extract_zip() -> None:
    EXTRACT_DIR.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(ZIP_PATH, "r") as archive:
        archive.extractall(EXTRACT_DIR)

        print("\nФайлы внутри архива:")

        for name in archive.namelist():
            print(f"  - {name}")


def main() -> None:
    download_file()
    validate_zip()
    extract_zip()

    print(f"\nГотово. Файлы распакованы в:\n{EXTRACT_DIR}")


if __name__ == "__main__":
    main()
