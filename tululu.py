from pathlib import Path
from urllib.parse import unquote, urljoin, urlsplit

import requests
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
