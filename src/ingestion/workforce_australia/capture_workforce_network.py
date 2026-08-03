from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from playwright.sync_api import Response, sync_playwright


PROJECT_ROOT = Path(__file__).resolve().parents[3]

OUTPUT_DIR = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "workforce_australia"
    / "network_capture"
)

SEARCH_URL = (
    "https://www.workforceaustralia.gov.au/"
    "individuals/jobs/search"
    "?searchText=data%20analyst"
    "&pageNumber=1"
    "&pageSize=20"
    "&sort=None"
)


def safe_filename(value: str) -> str:
    """Create a filesystem-safe filename from a URL."""
    cleaned = value.replace("https://", "").replace("http://", "")

    for character in r'\/:*?"<>|&=%':
        cleaned = cleaned.replace(character, "_")

    return cleaned[:180]


def save_json_response(
    response: Response,
    counter: int,
) -> None:
    """Save JSON responses that may contain job-search data."""
    content_type = response.headers.get("content-type", "").lower()
    resource_type = response.request.resource_type
    url = response.url

    is_candidate = (
        resource_type in {"xhr", "fetch"}
        or "json" in content_type
        or "api" in url.lower()
        or "job" in url.lower()
        or "vacan" in url.lower()
        or "search" in url.lower()
    )

    if not is_candidate:
        return

    print("\n--- NETWORK RESPONSE ---")
    print("Status:", response.status)
    print("Type:", resource_type)
    print("Content-Type:", content_type)
    print("URL:", url)

    metadata: dict[str, Any] = {
        "status": response.status,
        "resource_type": resource_type,
        "content_type": content_type,
        "url": url,
        "request_method": response.request.method,
        "request_post_data": response.request.post_data,
    }

    base_name = f"{counter:03d}_{safe_filename(url)}"

    metadata_path = OUTPUT_DIR / f"{base_name}_metadata.json"
    metadata_path.write_text(
        json.dumps(metadata, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    try:
        body = response.body()
    except Exception as error:
        print("Не удалось прочитать тело ответа:", error)
        return

    if not body:
        return

    body_path = OUTPUT_DIR / f"{base_name}_body.bin"
    body_path.write_bytes(body)

    try:
        parsed = response.json()
    except Exception:
        return

    json_path = OUTPUT_DIR / f"{base_name}_body.json"
    json_path.write_text(
        json.dumps(parsed, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    print("JSON сохранён:", json_path.name)


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    counter = 0

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(
            headless=False,
        )

        context = browser.new_context(
            locale="en-AU",
            user_agent=(
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 "
                "(KHTML, like Gecko) "
                "Chrome/126.0 Safari/537.36"
            ),
        )

        page = context.new_page()

        def handle_response(response: Response) -> None:
            nonlocal counter
            counter += 1

            try:
                save_json_response(response, counter)
            except Exception as error:
                print("Ошибка обработки ответа:", error)

        page.on("response", handle_response)

        print("Открываю:")
        print(SEARCH_URL)

        page.goto(
            SEARCH_URL,
            wait_until="domcontentloaded",
            timeout=120_000,
        )

        print("\nСтраница открыта.")
        print("Жду загрузку JavaScript и сетевые запросы...")

        page.wait_for_timeout(20_000)

        screenshot_path = OUTPUT_DIR / "workforce_search_page.png"
        page.screenshot(
            path=str(screenshot_path),
            full_page=True,
        )

        html_path = OUTPUT_DIR / "rendered_page.html"
        html_path.write_text(
            page.content(),
            encoding="utf-8",
        )

        print("\nЗаголовок страницы:")
        print(page.title())

        print("\nТекущий URL:")
        print(page.url)

        print("\nСкриншот:")
        print(screenshot_path)

        print("\nHTML после JavaScript:")
        print(html_path)

        print("\nФайлов сетевого захвата:")
        print(len(list(OUTPUT_DIR.iterdir())))

        print(
            "\nБраузер закроется через 10 секунд. "
            "Если видишь CAPTCHA или окно согласия, "
            "можно нажать вручную."
        )

        page.wait_for_timeout(10_000)
        browser.close()


if __name__ == "__main__":
    main()
