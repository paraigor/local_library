import argparse
import json
import logging
import sys
from time import sleep
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename
from requests.exceptions import ConnectionError, HTTPError, Timeout

from tululu import (
    check_for_redirect,
    download_img,
    download_txt,
    parse_book_page,
)

logger = logging.getLogger(__file__)


def get_last_page_of_genre_section():
    url = "https://tululu.org/l55/"
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    check_for_redirect(response)

    soup = BeautifulSoup(response.text, "lxml")

    return int(soup.select(".npage")[-1].text)


def create_parser(last_page_of_genre):
    parser = argparse.ArgumentParser(
        description="""Script for downloading science fiction books from tululu.org site.
                    All science fiction books downloaded default."""
    )
    parser.add_argument(
        "--start_page",
        type=int,
        default=1,
        help="Start page number of science fiction section",
    )
    parser.add_argument(
        "--end_page",
        type=int,
        default=last_page_of_genre,
        help="End page number of science fiction section",
    )
    parser.add_argument(
        "--dest_folder",
        default="books",
        help="Folder name to store books",
    )
    parser.add_argument(
        "--skip_imgs",
        action="store_true",
        default=False,
        help="Book cover images willn't be downloaded",
    )
    parser.add_argument(
        "--skip_txt",
        action="store_true",
        default=False,
        help="Book texts willn't be downloaded",
    )

    return parser


def get_book_urls(page_number):
    url = f"https://tululu.org/l55/{page_number}/"
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    check_for_redirect(response)

    soup = BeautifulSoup(response.text, "lxml")
    selector = ".d_book .bookimage a"
    page_book_links = soup.select(selector)
    page_book_urls = [
        urljoin(response.url, book_link["href"])
        for book_link in page_book_links
    ]

    return page_book_urls


def main():
    logging.basicConfig(format="%(levelname)s: %(message)s")
    try:
        last_page_of_genre = get_last_page_of_genre_section()
    except (ConnectionError, HTTPError, Timeout):
        sys.exit("Раздел с научной фантастикой на сайте не доступен")

    parser = create_parser(last_page_of_genre)
    args = parser.parse_args()

    start_page = args.start_page
    end_page = (
        args.end_page
        if args.end_page <= last_page_of_genre
        else last_page_of_genre
    )

    book_folder = sanitize_filename(args.dest_folder)

    book_urls = []
    for page_number in range(start_page, end_page + 1):
        try:
            page_book_urls = get_book_urls(page_number)
        except (ConnectionError, HTTPError, Timeout):
            logger.warning(
                f"Страница {page_number} раздела научной фантастики недоступна"
            )
            sleep(5)
            continue
        book_urls.extend(page_book_urls)

    books = []

    for book_url in book_urls:
        try:
            response = requests.get(book_url, timeout=10)
            response.raise_for_status()
            check_for_redirect(response)
        except (ConnectionError, HTTPError, Timeout):
            logger.warning(f"Книга {book_url} недоступна на сайте")
            sleep(5)
            continue

        content = parse_book_page(response)
        try:
            book_path = (
                download_txt(book_url, content["book_title"], book_folder)
                if not args.skip_txt
                else None
            )
            book_cover_path = (
                download_img(book_url, content["book_img_src"], book_folder)
                if not args.skip_imgs
                else None
            )
        except (ConnectionError, HTTPError, Timeout):
            logger.warning(
                f"Книга {book_url}. Недоступен материал для скачивания"
            )
            sleep(5)
            continue
        content["book_path"] = str(book_path)
        content["book_cover_path"] = str(book_cover_path)

        books.append(content)

    with open("books.json", "w", encoding="utf8") as json_file:
        json.dump(books, json_file, ensure_ascii=False)


if __name__ == "__main__":
    main()
