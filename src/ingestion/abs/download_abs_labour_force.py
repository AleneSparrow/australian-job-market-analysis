from __future__ import annotations

from pathlib import Path
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup


PROJECT_ROOT = Path(__file__).resolve().parents[3]

OUTPUT_DIR = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "abs"
    / "labour_force"
)

PAGE_URL = (
    "https://www.abs.gov.au/statistics/labour/"
    "employment-and-unemployment/"
    "labour-force-australia/latest-release"
)

WANTED_TABLES = {
    "Table 001": "abs_labour_force_table_001_australia.xlsx",
    "Table 010": "abs_labour_force_table_010_states.xlsx",
    "Table X28": "abs_labour_force_table_x28_underutilisation.xlsx",
}

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 Safari/537.36"
    )
}


def get_page() -> BeautifulSoup:
    print(f"Открываю страницу:\n{PAGE_URL}")

    response = requests.get(
        PAGE_URL,
        headers=HEADERS,
        timeout=60,
    )
    response.raise_for_status()

    return BeautifulSoup(response.text, "html.parser")


def find_download_link(
    soup: BeautifulSoup,
    table_name: str,
) -> str:
    heading = soup.find(
        lambda tag: (
            tag.name in {"h3", "h4", "h5"}
            and table_name.lower()
            in tag.get_text(" ", strip=True).lower()
        )
    )

    if heading is None:
        raise RuntimeError(
            f"Не найден заголовок для {table_name}"
        )

    current = heading

    while current is not None:
        current = current.find_next()

        if current is None:
            break

        if current.name in {"h3", "h4", "h5"}:
            break

        if current.name == "a" and current.get("href"):
            text = current.get_text(" ", strip=True).lower()
            href = current["href"]

            if (
                "download xlsx" in text
                or href.lower().endswith(".xlsx")
            ):
                return urljoin(PAGE_URL, href)

    raise RuntimeError(
        f"Не найдена XLSX-ссылка для {table_name}"
    )


def download_file(
    url: str,
    destination: Path,
) -> None:
    print(f"Скачиваю:\n{url}")

    response = requests.get(
        url,
        headers=HEADERS,
        timeout=120,
    )
    response.raise_for_status()

    content = response.content

    if not content.startswith(b"PK"):
        raise RuntimeError(
            "Файл не похож на XLSX/ZIP-контейнер"
        )

    destination.write_bytes(content)

    size_mb = destination.stat().st_size / (1024 * 1024)

    print(
        f"Сохранено: {destination.name} "
        f"— {size_mb:.2f} MB"
    )


def main() -> None:
    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    soup = get_page()

    for table_name, filename in WANTED_TABLES.items():
        print(f"\nИщу {table_name}")

        url = find_download_link(
            soup,
            table_name,
        )

        destination = OUTPUT_DIR / filename

        download_file(
            url,
            destination,
        )

    print("\nВсе таблицы Labour Force скачаны.")
    print(f"Папка:\n{OUTPUT_DIR}")


if __name__ == "__main__":
    main()
