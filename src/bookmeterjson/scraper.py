# SPDX-License-Identifier: MIT

from __future__ import annotations

import contextlib
import json
import math
import time
from datetime import date
from pathlib import Path

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from .config import Config
from .models import BookEntry

BASE_URL = "https://bookmeter.com"
BOOKS_PER_PAGE = 20


def create_driver() -> webdriver.Chrome:
    options = Options()
    options.add_argument("--headless")
    return webdriver.Chrome(options=options)


def login(driver: webdriver.Chrome, email: str, password: str) -> None:
    driver.get(f"{BASE_URL}/login/")
    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_element_located((By.ID, "session_email_address")))
    driver.find_element(By.ID, "session_email_address").send_keys(email)
    driver.find_element(By.ID, "session_password").send_keys(password)
    driver.find_element(By.NAME, "button").click()
    time.sleep(5)


def get_page_count(driver: webdriver.Chrome, user_id: str, category: str) -> int:
    url = f"{BASE_URL}/users/{user_id}/books/{category}"
    driver.get(url)
    time.sleep(2)
    soup = BeautifulSoup(driver.page_source, "html.parser")
    count_el = soup.find(class_="content__count")
    if count_el is None:
        return 0
    total = int(count_el.string)
    return math.ceil(total / BOOKS_PER_PAGE)


def parse_data_modal(element) -> dict:
    raw = element.get("data-modal", "{}")
    return json.loads(raw)


def parse_book_entry(book_el, category: str) -> BookEntry:
    # Primary data-modal from thumbnail__action
    action_div = book_el.select_one(".thumbnail__action .js-modal-button")
    modal = parse_data_modal(action_div)
    book_info = modal.get("book", {})

    entry = BookEntry(
        book_id=book_info.get("id", 0),
        book_path=book_info.get("book_path", ""),
        asin=book_info.get("asin", ""),
        title=book_info.get("title", ""),
        author=book_info.get("author", ""),
        pages=book_info.get("page", 0),
        image_url=book_info.get("image_url", ""),
        amazon_url=book_info.get("amazon_url", ""),
    )

    if category == "read":
        # Read date from detail__date
        date_el = book_el.select_one(".detail__date")
        if date_el and date_el.text.strip():
            entry.date = date_el.text.strip()

        # User-overridable authors from detail__authors
        authors_el = book_el.select_one(".detail__authors")
        if authors_el:
            entry.detail_authors = authors_el.text.strip()

        # User-overridable page count from detail__page
        page_el = book_el.select_one(".detail__page")
        if page_el and page_el.text.strip():
            with contextlib.suppress(ValueError):
                entry.detail_pages = int(page_el.text.strip())

        # Edit modal with review and bookcases
        edit_div = book_el.select_one(".detail__edit .js-modal-button")
        if edit_div:
            edit_modal = parse_data_modal(edit_div)
            review = edit_modal.get("review")
            if review:
                entry.review = {
                    "text": review.get("text"),
                    "is_netabare": review.get("is_netabare"),
                    "read_at": review.get("read_at"),
                    "is_draft": review.get("is_draft"),
                }
            bookcases = edit_modal.get("bookcases")
            if bookcases:
                entry.bookcases = bookcases

    return entry


def scrape_category(
    driver: webdriver.Chrome, user_id: str, category: str
) -> list[BookEntry]:
    page_count = get_page_count(driver, user_id, category)
    if page_count == 0:
        return []

    entries: list[BookEntry] = []

    for page_num in range(1, page_count + 1):
        print(f"  page {page_num}/{page_count}")
        url = f"{BASE_URL}/users/{user_id}/books/{category}"
        params = []
        if category == "read":
            params.append("display_type=list")
        if page_num > 1:
            params.append(f"page={page_num}")
        if params:
            url += "?" + "&".join(params)

        driver.get(url)
        time.sleep(3)

        soup = BeautifulSoup(driver.page_source, "html.parser")
        for book_el in soup.select("li.group__book"):
            entries.append(parse_book_entry(book_el, category))

    return entries


def write_output(
    entries: list[BookEntry], user_id: str, category: str, output_dir: str
) -> Path:
    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    today = date.today().isoformat()
    filename = f"{user_id}-{category}-{today}.json"
    filepath = out_path / filename

    data = [entry.to_dict() for entry in entries]
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    return filepath


def run(config: Config) -> None:
    driver = create_driver()
    try:
        print("Logging in...")
        login(driver, config.email, config.password)

        for category in config.categories:
            print(f"Scraping: {category}")
            entries = scrape_category(driver, config.user_id, category)
            filepath = write_output(
                entries, config.user_id, category, config.output_dir
            )
            print(f"  -> {filepath} ({len(entries)} books)")
    finally:
        driver.quit()
