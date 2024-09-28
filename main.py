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


book_text_url = "https://tululu.org/txt.php"
book_page_url = "https://tululu.org/b"
book_site_url = "https://tululu.org"

for book_id in range(1, 11):
    try:
        url = book_page_url + str(book_id)
        response = requests.get(url)
        response.raise_for_status()
    except (ConnectionError, HTTPError):
        continue

    soup = BeautifulSoup(response.text, "lxml")
    title_text = soup.find("h1").text
    title = title_text.split("::")[0].strip()
    # book_filename = f"{book_id}. {sanitize_filename(title)}.txt"
    # book_path = book_folder / book_filename

    # payload = {"id": book_id}
    # try:
    #     response = requests.get(
    #         book_text_url, params=payload, allow_redirects=False
    #     )
    #     response.raise_for_status()
    #     check_for_redirect(response)
    # except (ConnectionError, HTTPError):
    #     continue

    # with open(book_path, "wb") as file:
    #     file.write(response.content)
    book_img = soup.find("div", class_="bookimage")
    if book_img:
        img = book_img.find("img")["src"]
    else:
        continue

    img_url = urljoin(book_site_url, img)
    img_filename = urlsplit(img_url)[2].split("/")[-1]

    # download_img(img_url, img_filename)
    print(title)
    # comments = soup.find_all("div", class_="texts")

    # for comment in comments:
    #     text = comment.find("span").text
    #     print(text)
    genres_html = soup.find("span", class_="d_book").find_all("a")
    genres = []
    for genre in genres_html:
        text = genre.text
        genres.append(text)
    print(genres)
    print()
