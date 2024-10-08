from pathlib import Path
from urllib.parse import unquote, urljoin, urlsplit

import requests
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename
from requests.exceptions import HTTPError


def check_for_redirect(response):
    if response.history:
        raise HTTPError


def download_txt(url, title, folder):
    book_folder = Path(folder)
    book_folder.mkdir(exist_ok=True)

    book_id = "".join([s for s in urlsplit(url)[2] if s.isdigit()])

    book_filename = f"{book_id} {sanitize_filename(title)}.txt"
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


def download_img(url, img_src, folder):
    img_url = urljoin(url, img_src)
    folder_name = folder + "_img"
    img_folder = Path(folder_name)
    img_folder.mkdir(exist_ok=True)
    img_filename = f"{sanitize_filename(unquote(img_src.split('/')[-1]))}"
    img_path = img_folder / img_filename

    response = requests.get(img_url, timeout=10)
    response.raise_for_status()

    with open(img_path, "wb") as file:
        file.write(response.content)

    return img_path


def parse_book_page(response):
    soup = BeautifulSoup(response.text, "lxml")

    header = soup.select_one("h1").text
    book_title = header.split("::")[0].strip()
    book_author = header.split("::")[1].strip()

    book_img_selector = ".bookimage img"
    book_img_src = soup.select_one(book_img_selector)["src"]

    genres_selector = "span.d_book a"
    genres_html = soup.select(genres_selector)
    genres = [genre_html.text for genre_html in genres_html]

    comments_selector = ".texts span"
    comments_html = soup.select(comments_selector)
    comments = [comment_html.text for comment_html in comments_html]

    content = {
        "book_title": book_title,
        "book_author": book_author,
        "book_img_src": book_img_src,
        "genres": genres,
        "comments": comments,
    }

    return content
