import argparse
import logging
from pathlib import Path
from time import sleep
from urllib.parse import unquote, urljoin

import requests
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename
from requests.exceptions import ConnectionError, HTTPError

logging.basicConfig(format="%(levelname)s: %(message)s")


def check_for_redirect(response):
    if response.history:
        raise HTTPError


def download_txt(url, filename, folder="books"):
    book_folder = Path(folder)
    book_folder.mkdir(exist_ok=True)

    book_filename = f"{sanitize_filename(filename)}.txt"
    book_filename = book_filename.replace(" ", "_")
    book_path = book_folder / book_filename

    try:
        response = requests.get(url, allow_redirects=False)
        response.raise_for_status()
        check_for_redirect(response)
    except (ConnectionError, HTTPError):
        logging.warning(f"Книга <{filename}>. Нет текста для скачивания.")
        sleep(5)
        return

    with open(book_path, "wb") as file:
        file.write(response.content)


def download_img(url, filename, folder="book_covers"):
    img_folder = Path(folder)
    img_folder.mkdir(exist_ok=True)

    img_filename = f"{sanitize_filename(unquote(filename))}"
    img_path = img_folder / img_filename

    try:
        response = requests.get(url)
        response.raise_for_status()
    except (ConnectionError, HTTPError):
        logging.warning(f"Файл обложки <{filename}> отсутствует.")
        sleep(5)
        return

    with open(img_path, "wb") as file:
        file.write(response.content)


def parse_book_page(response):
    soup = BeautifulSoup(response.text, "lxml")

    header = soup.find("h1").text
    book_title = header.split("::")[0].strip()
    book_author = header.split("::")[1].strip()

    book_img = soup.find("div", class_="bookimage").find("img")["src"]
    book_img_url = urljoin("https://tululu.org", book_img)
    book_img_filename = book_img.split("/")[-1]

    genres_html = soup.find("span", class_="d_book").find_all("a")
    genres = []
    for genre_html in genres_html:
        genre = genre_html.text
        genres.append(genre)

    comments_html = soup.find_all("div", class_="texts")
    comments = []
    for comment_html in comments_html:
        comment = comment_html.find("span").text
        comments.append(comment)

    content = {
        "book_title": book_title,
        "book_author": book_author,
        "book_img_url": book_img_url,
        "book_img_filename": book_img_filename,
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

    for book_id in range(args.start_id, args.end_id + 1):
        try:
            url = f"https://tululu.org/b{book_id}/"
            response = requests.get(url, allow_redirects=False)
            response.raise_for_status()
            check_for_redirect(response)
        except (ConnectionError, HTTPError):
            logging.warning(f"Книги с id={book_id} нет на сайте.")
            sleep(5)
            continue

        content = parse_book_page(response)
        download_book_url = f"https://tululu.org/txt.php?id={book_id}"

        download_txt(download_book_url, content["book_title"])
        download_img(content["book_img_url"], content["book_img_filename"])


if __name__ == "__main__":
    main()
