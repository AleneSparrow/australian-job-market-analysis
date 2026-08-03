from __future__ import annotations

import re
import sys
from pathlib import Path
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup


PROJECT_ROOT = Path(__file__).resolve().parents[3]
OUTPUT_DIR = PROJECT_ROOT / "data" / "raw" / "jsa"

SOURCES = [
    {
        "page_url": "https://www.jobsandskills.gov.au/data/internet-vacancy-index",
        "link_pattern": re.compile(
            r"Internet Vacancies,\s*ANZSCO4 Occupations,\s*States and Territories",
            re.IGNORECASE,
        ),
        "output_name": "jsa_ivi_anzsco4_states_latest.xlsx",
    },
    {
        "page_url": (
            "https://www.jobsandskills.gov.au/"
            "data/occupation-and-industry-profiles"
        ),
        "link_pattern": re.compile(
            r"Occupation profiles data",
            re.IGNORECASE,
        ),
        "output_name": "jsa_occupation_profiles_latest.xlsx",
    },
]

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 Safari/537.36"
    )
}


def find_download_url(page_url: str, pattern: re.Pattern[str]) -> str:
    """Find the download link located near a matching file title."""
    response = requests.get(page_url, headers=HEADERS, timeout=60)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    # First search links by their visible text or attributes.
    for link in soup.find_all("a", href=True):
        searchable_text = " ".join(
            [
                link.get_text(" ", strip=True),
                link.get("title", ""),
                link.get("aria-label", ""),
                link["href"],
            ]
        )

        if pattern.search(searchable_text):
            return urljoin(page_url, link["href"])

    # Some pages show the filename and place the Download link nearby.
    matching_text = soup.find(
        string=lambda value: bool(value and pattern.search(value))
    )

    if matching_text:
        container = matching_text.parent

        for parent in [container, *container.parents]:
            download_link = parent.find(
                "a",
                href=True,
                string=lambda value: bool(
                    value and "download" in value.lower()
                ),
            )

            if download_link:
                return urljoin(page_url, download_link["href"])

    raise RuntimeError(
        f"Не удалось найти ссылку на странице: {page_url}"
    )


def download_file(url: str, destination: Path) -> None:
    """Download a file without modifying its contents."""
    with requests.get(
        url,
        headers=HEADERS,
        timeout=120,
        stream=True,
    ) as response:
        response.raise_for_status()

        destination.parent.mkdir(parents=True, exist_ok=True)

        with destination.open("wb") as file:
            for chunk in response.iter_content(chunk_size=1024 * 1024):
                if chunk:
                    file.write(chunk)

    if destination.stat().st_size == 0:
        destination.unlink(missing_ok=True)
        raise RuntimeError(f"Получен пустой файл: {destination}")


def main() -> int:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    for source in SOURCES:
        destination = OUTPUT_DIR / source["output_name"]

        print(f"\nИсточник: {source['page_url']}")
        print("Ищу актуальную ссылку...")

        download_url = find_download_url(
            source["page_url"],
            source["link_pattern"],
        )

        print(f"Найдена ссылка: {download_url}")
        print(f"Скачиваю в: {destination}")

        download_file(download_url, destination)

        size_mb = destination.stat().st_size / (1024 * 1024)
        print(f"Готово: {destination.name} — {size_mb:.2f} MB")

    print("\nВсе файлы JSA успешно загружены.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except requests.RequestException as error:
        print(f"\nОшибка HTTP: {error}", file=sys.stderr)
        raise SystemExit(1)
    except Exception as error:
        print(f"\nОшибка: {error}", file=sys.stderr)
        raise SystemExit(1)
