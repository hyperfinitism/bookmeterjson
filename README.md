# bookmeterjson

A scraper for [bookmeter.com](https://bookmeter.com/) that exports your book lists as JSON.

## Features

- Scrapes all four book categories: Read (読んだ), Reading (読んでる), Stacked (積読), Wish (読みたい)
- Extracts full book info from page HTM
  - Book ID, ASIN, title, author, pages, image URL, Amazon URL
  - User-registered authors and pages, Read date, review, and bookcases (for "read" category)
- Outputs one JSON file per category: `{user_id}-{category}-{yyyy-mm-dd}.json`
- Credentials stored in `configs.yaml`

## Requirements

- Python >= 3.11
- Google Chrome

## Setup

```bash
pip install git+https://github.com/hyperfinitism/bookmeterjson
```

Create `configs.yaml` in the working directory with your bookmeter credentials:

```yaml
user_id: "012345"
email: "example@example.com"
password: "password"

categories:
  - read
  - reading
  - stacked
  - wish

output_dir: "./output"
```

## Usage

```bash
bookmeterjson
```

With a custom config path:

```bash
python -m bookmeterjson --config path/to/configs.yaml
```

## Output

Each JSON file contains an array of book entries:

```jsonc
[
  {
    "book_id": 12345678,
    "book_path": "/books/12345678",
    "asin": "ABCDE01234", // null if the source is not Amazon.co.jp (e.g. user-registered)
    "title": "Book Title",
    "author": "Author(s)",
    "pages": 625, // 0 if the page information is not set
    "image_url": "https://m.media-amazon.com/images/I/...", // "https://bookmeter.com/images/common/book.png" if the book thumbnail is not set
    "amazon_url": "https://www.amazon.co.jp/dp/...", // "https://www.amazon.co.jp/dp" if the source is not Amazon.co.jp (e.g. user-registed)
    "detail_authors": "Author(s)", // user can manually override this entry
    "detail_pages": 725, // user can manually override this entry
    "date": "2026/02/10",
    "review": {
      "text": null,
      "is_netabare": null,
      "read_at": "2026-02-10",
      "is_draft": true
    },
    "bookcases": ["Music"]
  }
]
```

For non-read categories, `detail_authors`, `detail_pages`, `date`, `review`, and `bookcases` fields are omitted.

## Warning

Do not use it very frequently (or manually adjust sleep time too shortly) to avoid overloading the server. Bookmeter's [Terms of Use](https://bookmeter.com/terms) Article 9.1.xvi prohibits intentionally placing excessive load on the service's servers or network.
