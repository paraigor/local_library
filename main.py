from pathlib import Path
from urllib.parse import unquote, urljoin, urlsplit

import requests
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename
from requests.exceptions import ConnectionError, HTTPError


def check_for_redirect(response):
    if response.status_code != 200:
        raise HTTPError


def download_txt(url, filename, folder="books"):
    book_folder = Path(folder)
    book_folder.mkdir(exist_ok=True)

    book_filename = f"{sanitize_filename(filename)}.txt"
    book_path = book_folder / book_filename

    try:
        response = requests.get(url, allow_redirects=True)
        response.raise_for_status()
        check_for_redirect(response)
    except (ConnectionError, HTTPError):
        return

    with open(book_path, "wb") as file:
        file.write(response.content)

    return book_path


def download_img(url, filename, folder="books"):
    book_folder = Path(folder)
    book_folder.mkdir(exist_ok=True)

    img_filename = f"{sanitize_filename(unquote(filename))}"
    img_path = book_folder / img_filename

    response = requests.get(url)
    response.raise_for_status()

    with open(img_path, "wb") as file:
        file.write(response.content)

    return img_path


def parse_book_page(response):
    sheme, netloc, *_ = urlsplit(response.url)
    book_site_url = sheme + "://" + netloc
    soup = BeautifulSoup(response.text, "lxml")

    header = soup.find("h1").text
    book_title = header.split("::")[0].strip()
    book_author = header.split("::")[1].strip()

    book_img = soup.find("div", class_="bookimage").find("img")["src"]
    book_img_url = urljoin(book_site_url, book_img)
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


book_text_url = "https://tululu.org/txt.php"
book_page_url = "https://tululu.org/b9/"

try:
    response = requests.get(book_page_url)
    response.raise_for_status()
    check_for_redirect(response)
except (ConnectionError, HTTPError):
    print("Ошибочка")

print(parse_book_page(response))
