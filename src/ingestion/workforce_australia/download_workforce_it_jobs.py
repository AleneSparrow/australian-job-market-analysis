from __future__ import annotations

import argparse
import json
import logging
import re
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


PROJECT_ROOT = Path(__file__).resolve().parents[3]

OUTPUT_ROOT = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "workforce_australia"
    / "it_jobs"
)

API_URL = (
    "https://www.workforceaustralia.gov.au/"
    "api/v1/global/vacancies/"
)

SEARCH_TERMS = [
    # Software development
    "software engineer",
    "software developer",
    "full stack developer",
    "backend developer",
    "frontend developer",
    "web developer",
    "mobile developer",
    "ios developer",
    "android developer",

    # Data and analytics
    "data analyst",
    "business intelligence analyst",
    "business analyst",
    "data engineer",
    "data scientist",
    "analytics engineer",
    "machine learning engineer",
    "artificial intelligence engineer",
    "BI developer",
    "ETL developer",
    "database developer",
    "database administrator",

    # Infrastructure, cloud and operations
    "devops engineer",
    "cloud engineer",
    "cloud architect",
    "platform engineer",
    "site reliability engineer",
    "systems engineer",
    "systems administrator",
    "network engineer",
    "network administrator",

    # Cybersecurity
    "cyber security",
    "cybersecurity analyst",
    "security engineer",
    "information security",
    "security analyst",

    # Testing and quality
    "QA engineer",
    "software tester",
    "test analyst",
    "test automation engineer",

    # Architecture, delivery and support
    "solutions architect",
    "technical architect",
    "IT project manager",
    "IT support",
    "service desk analyst",
    "technical support engineer",

    # Technology-specific searches
    "Python developer",
    "Java developer",
    ".NET developer",
    "C# developer",
    "JavaScript developer",
    "React developer",
    "Power BI developer",
    "Tableau developer",
    "SQL developer",
    "SAP consultant",
]

DEFAULT_PAGE_SIZE = 100
DEFAULT_MAX_PAGES_PER_QUERY = 200
DEFAULT_DELAY_SECONDS = 1.5

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


def utc_now() -> str:
    """Return the current UTC time in ISO format."""
    return datetime.now(timezone.utc).isoformat()


def timestamp_for_folder() -> str:
    """Return a timestamp safe for directory names."""
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def safe_folder_name(value: str) -> str:
    """Convert a search term into a safe folder name."""
    value = value.strip().lower()
    value = value.replace(".net", "dotnet")
    value = value.replace("c#", "c_sharp")
    value = re.sub(r"[^a-z0-9]+", "_", value)
    return value.strip("_")


def configure_logging(run_directory: Path) -> logging.Logger:
    """Create console and file logging."""
    logger = logging.getLogger("workforce_downloader")
    logger.setLevel(logging.INFO)
    logger.handlers.clear()

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(message)s"
    )

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    file_handler = logging.FileHandler(
        run_directory / "download.log",
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger


def create_session() -> requests.Session:
    """Create an HTTP session with automatic retries."""
    retry_strategy = Retry(
        total=5,
        connect=5,
        read=5,
        status=5,
        backoff_factor=2,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET"],
        respect_retry_after_header=True,
        raise_on_status=False,
    )

    adapter = HTTPAdapter(
        max_retries=retry_strategy,
        pool_connections=10,
        pool_maxsize=10,
    )

    session = requests.Session()
    session.headers.update(HEADERS)
    session.mount("https://", adapter)
    session.mount("http://", adapter)

    return session


def find_job_items(data: Any) -> list[dict[str, Any]]:
    """
    Locate the list of vacancy search results in the API response.

    Workforce Australia may return records either directly or inside
    objects such as {"score": ..., "result": {...}}.
    """
    preferred_keys = (
        "results",
        "items",
        "vacancies",
        "jobs",
        "data",
        "content",
    )

    if isinstance(data, list):
        dictionary_items = [
            item for item in data if isinstance(item, dict)
        ]

        if any(
            "result" in item or "vacancyId" in item
            for item in dictionary_items
        ):
            return dictionary_items

        for item in dictionary_items:
            nested = find_job_items(item)

            if nested:
                return nested

        return []

    if isinstance(data, dict):
        for key in preferred_keys:
            value = data.get(key)

            if isinstance(value, list):
                dictionary_items = [
                    item for item in value if isinstance(item, dict)
                ]

                if any(
                    "result" in item or "vacancyId" in item
                    for item in dictionary_items
                ):
                    return dictionary_items

            if isinstance(value, (dict, list)):
                nested = find_job_items(value)

                if nested:
                    return nested

        for value in data.values():
            if isinstance(value, (dict, list)):
                nested = find_job_items(value)

                if nested:
                    return nested

    return []


def extract_vacancy_id(item: dict[str, Any]) -> str | None:
    """Extract vacancyId from either a direct or wrapped record."""
    record: Any = item.get("result", item)

    if not isinstance(record, dict):
        return None

    vacancy_id = record.get("vacancyId")

    if vacancy_id is None:
        return None

    return str(vacancy_id)


def save_json(path: Path, data: Any) -> None:
    """Save JSON using UTF-8 without modifying its structure."""
    path.parent.mkdir(parents=True, exist_ok=True)

    temporary_path = path.with_suffix(path.suffix + ".tmp")

    temporary_path.write_text(
        json.dumps(
            data,
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    temporary_path.replace(path)


def download_page(
    session: requests.Session,
    search_term: str,
    page_number: int,
    page_size: int,
) -> tuple[dict[str, Any] | list[Any], str]:
    """Download one API result page."""
    params = {
        "searchText": search_term,
        "pageNumber": page_number,
        "pageSize": page_size,
    }

    response = session.get(
        API_URL,
        params=params,
        timeout=(30, 120),
    )

    if response.status_code != 200:
        raise requests.HTTPError(
            f"HTTP {response.status_code}: "
            f"{response.text[:500]}",
            response=response,
        )

    content_type = response.headers.get(
        "Content-Type",
        "",
    ).lower()

    if "json" not in content_type:
        raise RuntimeError(
            f"Ожидался JSON, но получен Content-Type: "
            f"{content_type}"
        )

    try:
        data = response.json()
    except requests.JSONDecodeError as error:
        raise RuntimeError(
            "API вернул некорректный JSON"
        ) from error

    return data, response.url


def download_search_term(
    session: requests.Session,
    run_directory: Path,
    search_term: str,
    page_size: int,
    max_pages: int,
    delay_seconds: float,
    logger: logging.Logger,
    resume: bool,
) -> dict[str, Any]:
    """Download all result pages for one search term."""
    query_directory = (
        run_directory
        / "queries"
        / safe_folder_name(search_term)
    )

    query_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    query_started_at = utc_now()
    unique_ids: set[str] = set()
    downloaded_pages = 0
    reused_pages = 0
    raw_records = 0
    stopped_reason = "maximum page limit reached"
    last_request_url: str | None = None

    logger.info("=" * 70)
    logger.info("Запрос: %s", search_term)

    for page_number in range(1, max_pages + 1):
        output_path = (
            query_directory
            / f"page_{page_number:04d}.json"
        )

        if resume and output_path.exists():
            logger.info(
                "[%s] Страница %s уже существует — читаю локально",
                search_term,
                page_number,
            )

            try:
                data = json.loads(
                    output_path.read_text(encoding="utf-8")
                )
            except json.JSONDecodeError:
                logger.warning(
                    "Локальный JSON повреждён. "
                    "Страница будет скачана заново."
                )
            else:
                reused_pages += 1
                items = find_job_items(data)
                raw_records += len(items)

                for item in items:
                    vacancy_id = extract_vacancy_id(item)

                    if vacancy_id:
                        unique_ids.add(vacancy_id)

                if not items:
                    stopped_reason = (
                        "existing page contained no vacancies"
                    )
                    break

                if len(items) < page_size:
                    stopped_reason = (
                        "existing page contained fewer records "
                        "than pageSize"
                    )
                    break

                continue

        logger.info(
            "[%s] Скачиваю страницу %s",
            search_term,
            page_number,
        )

        try:
            data, request_url = download_page(
                session=session,
                search_term=search_term,
                page_number=page_number,
                page_size=page_size,
            )
        except Exception:
            logger.exception(
                "[%s] Ошибка на странице %s",
                search_term,
                page_number,
            )
            stopped_reason = (
                f"request failed on page {page_number}"
            )
            break

        last_request_url = request_url
        items = find_job_items(data)

        page_metadata = {
            "source": "Workforce Australia",
            "api_url": API_URL,
            "request_url": request_url,
            "search_term": search_term,
            "page_number": page_number,
            "page_size": page_size,
            "downloaded_at_utc": utc_now(),
            "records_detected": len(items),
            "response": data,
        }

        save_json(
            output_path,
            page_metadata,
        )

        downloaded_pages += 1
        raw_records += len(items)

        page_ids: set[str] = set()

        for item in items:
            vacancy_id = extract_vacancy_id(item)

            if vacancy_id:
                page_ids.add(vacancy_id)
                unique_ids.add(vacancy_id)

        logger.info(
            "[%s] Страница %s: %s записей, "
            "%s vacancyId",
            search_term,
            page_number,
            len(items),
            len(page_ids),
        )

        if not items:
            stopped_reason = "API returned no vacancies"
            break

        if len(items) < page_size:
            stopped_reason = (
                "API returned fewer records than pageSize"
            )
            break

        time.sleep(delay_seconds)

    query_manifest = {
        "source": "Workforce Australia",
        "search_term": search_term,
        "folder": str(
            query_directory.relative_to(PROJECT_ROOT)
        ),
        "started_at_utc": query_started_at,
        "finished_at_utc": utc_now(),
        "page_size": page_size,
        "downloaded_pages": downloaded_pages,
        "reused_pages": reused_pages,
        "raw_records_across_pages": raw_records,
        "unique_vacancy_ids_for_query": len(unique_ids),
        "stopped_reason": stopped_reason,
        "last_request_url": last_request_url,
    }

    save_json(
        query_directory / "query_manifest.json",
        query_manifest,
    )

    logger.info(
        "[%s] Готово: страниц %s, записей %s, "
        "уникальных vacancyId %s",
        search_term,
        downloaded_pages + reused_pages,
        raw_records,
        len(unique_ids),
    )

    return {
        **query_manifest,
        "_vacancy_ids": sorted(unique_ids),
    }


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Download Australian IT vacancies from "
            "Workforce Australia."
        )
    )

    parser.add_argument(
        "--page-size",
        type=int,
        default=DEFAULT_PAGE_SIZE,
        help="Number of vacancies requested per page.",
    )

    parser.add_argument(
        "--max-pages",
        type=int,
        default=DEFAULT_MAX_PAGES_PER_QUERY,
        help="Safety limit per search term.",
    )

    parser.add_argument(
        "--delay",
        type=float,
        default=DEFAULT_DELAY_SECONDS,
        help="Delay between API requests in seconds.",
    )

    parser.add_argument(
        "--fresh",
        action="store_true",
        help=(
            "Create a new timestamped download run. "
            "Without this option, the latest_run folder is used."
        ),
    )

    parser.add_argument(
        "--no-resume",
        action="store_true",
        help="Download pages again even when local files exist.",
    )

    parser.add_argument(
        "--limit-queries",
        type=int,
        default=None,
        help="Run only the first N search terms for testing.",
    )

    return parser.parse_args()


def main() -> None:
    args = parse_arguments()

    if args.page_size < 1:
        raise ValueError("--page-size must be at least 1")

    if args.max_pages < 1:
        raise ValueError("--max-pages must be at least 1")

    if args.delay < 0:
        raise ValueError("--delay cannot be negative")

    OUTPUT_ROOT.mkdir(
        parents=True,
        exist_ok=True,
    )

    if args.fresh:
        run_name = f"run_{timestamp_for_folder()}"
    else:
        run_name = "latest_run"

    run_directory = OUTPUT_ROOT / run_name
    run_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    logger = configure_logging(run_directory)
    session = create_session()

    search_terms = SEARCH_TERMS

    if args.limit_queries is not None:
        search_terms = search_terms[: args.limit_queries]

    logger.info("Workforce Australia IT downloader")
    logger.info("Папка запуска: %s", run_directory)
    logger.info("Поисковых запросов: %s", len(search_terms))
    logger.info("Page size: %s", args.page_size)
    logger.info("Максимум страниц на запрос: %s", args.max_pages)
    logger.info("Пауза: %.1f сек.", args.delay)

    run_started_at = utc_now()
    query_results: list[dict[str, Any]] = []
    all_unique_ids: set[str] = set()

    for query_number, search_term in enumerate(
        search_terms,
        start=1,
    ):
        logger.info(
            "Запрос %s из %s",
            query_number,
            len(search_terms),
        )

        result = download_search_term(
            session=session,
            run_directory=run_directory,
            search_term=search_term,
            page_size=args.page_size,
            max_pages=args.max_pages,
            delay_seconds=args.delay,
            logger=logger,
            resume=not args.no_resume,
        )

        vacancy_ids = result.pop("_vacancy_ids")
        all_unique_ids.update(vacancy_ids)
        query_results.append(result)

        if query_number < len(search_terms):
            time.sleep(args.delay)

    manifest = {
        "source": "Workforce Australia",
        "api_url": API_URL,
        "dataset_scope": "Australian IT job vacancies",
        "run_started_at_utc": run_started_at,
        "run_finished_at_utc": utc_now(),
        "run_folder": str(
            run_directory.relative_to(PROJECT_ROOT)
        ),
        "search_terms": search_terms,
        "number_of_search_terms": len(search_terms),
        "page_size": args.page_size,
        "maximum_pages_per_query": args.max_pages,
        "delay_seconds": args.delay,
        "total_downloaded_pages": sum(
            item["downloaded_pages"]
            for item in query_results
        ),
        "total_reused_pages": sum(
            item["reused_pages"]
            for item in query_results
        ),
        "raw_records_across_all_queries": sum(
            item["raw_records_across_pages"]
            for item in query_results
        ),
        "unique_vacancy_ids_across_all_queries": len(
            all_unique_ids
        ),
        "queries": query_results,
        "notes": [
            (
                "Raw API responses are stored separately "
                "for each search term and page."
            ),
            (
                "The same vacancy may appear under multiple "
                "search terms."
            ),
            (
                "No cleaning, deduplication or analytical "
                "transformation has been applied."
            ),
        ],
    }

    save_json(
        run_directory / "manifest.json",
        manifest,
    )

    save_json(
        run_directory / "vacancy_ids_index.json",
        {
            "created_at_utc": utc_now(),
            "count": len(all_unique_ids),
            "vacancy_ids": sorted(all_unique_ids),
        },
    )

    logger.info("=" * 70)
    logger.info("ВСЯ ЗАГРУЗКА ЗАВЕРШЕНА")
    logger.info(
        "Уникальных vacancyId по всем запросам: %s",
        len(all_unique_ids),
    )
    logger.info(
        "Manifest: %s",
        run_directory / "manifest.json",
    )


if __name__ == "__main__":
    main()
