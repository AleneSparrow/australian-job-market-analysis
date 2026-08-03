from pathlib import Path

import requests
from bs4 import BeautifulSoup


PROJECT_ROOT = Path(__file__).resolve().parents[3]

OUTPUT_DIR = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "workforce_australia"
)

URL = (
    "https://www.workforceaustralia.gov.au/"
    "individuals/jobs/search"
)

PARAMS = {
    "searchText": "data analyst",
    "pageNumber": 1,
    "pageSize": 20,
    "sort": "None",
}

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 "
        "(KHTML, like Gecko) "
        "Chrome/126.0 Safari/537.36"
    ),
    "Accept-Language": "en-AU,en;q=0.9",
}


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print("Открываю Workforce Australia...")
    print(URL)
    print("Параметры:", PARAMS)

    response = requests.get(
        URL,
        params=PARAMS,
        headers=HEADERS,
        timeout=60,
    )

    print("\nHTTP status:", response.status_code)
    print("Content-Type:", response.headers.get("Content-Type"))
    print("Размер ответа:", len(response.content), "байт")
    print("Финальный URL:", response.url)

    response.raise_for_status()

    html_path = OUTPUT_DIR / "workforce_data_analyst_page_1.html"
    html_path.write_bytes(response.content)

    print("\nHTML сохранён:")
    print(html_path)

    soup = BeautifulSoup(response.text, "html.parser")

    text = soup.get_text(" ", strip=True)

    print("\nПервые 1000 символов текста:")
    print(text[:1000])

    links = []

    for link in soup.find_all("a", href=True):
        href = link["href"]

        if "/individuals/jobs/details/" in href:
            title = link.get_text(" ", strip=True)

            links.append(
                {
                    "title": title,
                    "href": href,
                }
            )

    print("\nНайдено ссылок на вакансии:", len(links))

    for item in links[:10]:
        print("-", item["title"])
        print(" ", item["href"])


if __name__ == "__main__":
    main()
