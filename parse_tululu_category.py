import argparse
import json
import logging
from pathlib import Path
from time import sleep
from urllib.parse import unquote, urljoin, urlsplit

import requests
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename
from requests.exceptions import ConnectionError, HTTPError, Timeout

logging.basicConfig(format="%(levelname)s: %(message)s")


def check_for_redirect(response):
    if response.history:
        raise HTTPError


def get_books_urls():
    books_urls = []
    for page_number in range(1, 5):
        url = f"https://tululu.org/l55/{page_number}/"
        response = requests.get(url)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "lxml")
        selector = ".d_book .bookimage a"
        page_books_links = soup.select(selector)
        page_books_urls = [
            urljoin(response.url, book_link["href"])
            for book_link in page_books_links
        ]
        books_urls.extend(page_books_urls)

    return books_urls


def download_txt(url, filename, folder="books"):
    book_folder = Path(folder)
    book_folder.mkdir(exist_ok=True)

    book_id = "".join([s for s in urlsplit(url)[2] if s.isdigit()])

    book_filename = f"{book_id} {sanitize_filename(filename)}.txt"
    book_filename = book_filename.replace(" ", "_")
    book_path = book_folder / book_filename

    url = "https://tululu.org/txt.php"
    payload = {"id": book_id}

    response = requests.get(url, params=payload, timeout=10)
    response.raise_for_status()
    check_for_redirect(response)

    with open(book_path, "wb") as file:
        file.write(response.content)

    return book_path


def download_img(url, filename, folder="books_covers"):
    img_folder = Path(folder)
    img_folder.mkdir(exist_ok=True)

    img_filename = f"{sanitize_filename(unquote(filename))}"
    img_path = img_folder / img_filename

    response = requests.get(url, timeout=10)
    response.raise_for_status()

    with open(img_path, "wb") as file:
        file.write(response.content)

    return img_path


def parse_book_page(response):
    soup = BeautifulSoup(response.text, "lxml")
    book_url = response.url

    header = soup.select_one("h1").text
    book_title = header.split("::")[0].strip()
    book_author = header.split("::")[1].strip()

    book_img_selector = ".bookimage img"
    book_img_src = soup.select_one(book_img_selector)["src"]
    book_img_url = urljoin(book_url, book_img_src)
    book_img_filename = book_img_src.split("/")[-1]

    genres_selector = "span.d_book a"
    genres_html = soup.select(genres_selector)
    genres = [genre_html.text for genre_html in genres_html]

    comments_selector = ".texts span"
    comments_html = soup.select(comments_selector)
    comments = [comment_html.text for comment_html in comments_html]

    book_path = download_txt(book_url, book_title)
    book_cover_path = download_img(book_img_url, book_img_filename)

    content = {
        "book_title": book_title,
        "book_author": book_author,
        "book_path": str(book_path),
        "book_cover_path": str(book_cover_path),
        "genres": genres,
        "comments": comments,
    }

    return content


def main():
    parser = argparse.ArgumentParser(
        description="""Script for downloading books from tululu.org site.
                    Books with IDs from 1 to 10 downloaded default."""
    )
    parser.add_argument(
        "start_id",
        nargs="?",
        type=int,
        default=1,
        help="Start ID of book for range of book being downloaded",
    )
    parser.add_argument(
        "end_id",
        nargs="?",
        type=int,
        default=10,
        help="End ID of book for range of book being downloaded",
    )
    args = parser.parse_args()

    books_urls = get_books_urls()
    books = []

    for book_url in books_urls:
        try:
            response = requests.get(book_url, timeout=10)
            response.raise_for_status()
            check_for_redirect(response)
        except (ConnectionError, HTTPError, Timeout):
            logging.warning(f"Книги {book_url} нет на сайте.")
            sleep(5)
            continue

        try:
            content = parse_book_page(response)
        except (ConnectionError, HTTPError, Timeout):
            logging.warning(
                f"Книга {response.url}. Нет текста для скачивания."
            )
            sleep(5)
            continue

        books.append(content)
    print(len(books))
    with open("books.json", "w", encoding="utf8") as json_file:
        json.dump(books, json_file, ensure_ascii=False)


if __name__ == "__main__":
    main()
