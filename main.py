from pathlib import Path

import requests
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename
from requests.exceptions import ConnectionError, HTTPError


def check_for_redirect(response):
    if response.status_code != 200:
        raise HTTPError


book_folder = Path("books")
book_folder.mkdir(exist_ok=True)

book_text_url = "https://tululu.org/txt.php"
book_page_url = "https://tululu.org/b"

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
    book_filename = f"{book_id}. {sanitize_filename(title)}.txt"
    book_path = book_folder / book_filename

    payload = {"id": book_id}
    try:
        response = requests.get(
            book_text_url, params=payload, allow_redirects=False
        )
        response.raise_for_status()
        check_for_redirect(response)
    except (ConnectionError, HTTPError):
        continue

    with open(book_path, "wb") as file:
        file.write(response.content)
