# SPDX-License-Identifier: MIT

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class BookEntry:
    book_id: int
    book_path: str
    asin: str
    title: str
    author: str
    pages: int
    image_url: str
    amazon_url: str
    date: str | None = None
    detail_authors: str | None = None
    detail_pages: int | None = None
    review: dict | None = None
    bookcases: list[str] | None = None

    def to_dict(self) -> dict:
        d: dict = {
            "book_id": self.book_id,
            "book_path": self.book_path,
            "asin": self.asin,
            "title": self.title,
            "author": self.author,
            "pages": self.pages,
            "image_url": self.image_url,
            "amazon_url": self.amazon_url,
        }
        if self.date is not None:
            d["date"] = self.date
        if self.detail_authors is not None:
            d["detail_authors"] = self.detail_authors
        if self.detail_pages is not None:
            d["detail_pages"] = self.detail_pages
        if self.review is not None:
            d["review"] = self.review
        if self.bookcases is not None:
            d["bookcases"] = self.bookcases
        return d
