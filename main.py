from pathlib import Path

import requests

book_folder = Path("books")
book_folder.mkdir(exist_ok=True)

url = "https://tululu.org/txt.php"

for book_id in range(1, 11):
    book_filename = f"book_{book_id:02}.txt"
    book_path = book_folder / book_filename

    payload = {"id": book_id}

    response = requests.get(url, params=payload)
    response.raise_for_status()

    with open(book_path, "wb") as file:
        file.write(response.content)
