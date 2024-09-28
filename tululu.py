import requests
from bs4 import BeautifulSoup
from requests.exceptions import ConnectionError, HTTPError

book_page_url = "https://tululu.org/b"
url = book_page_url + str(1)

# for book_id in range(1, 11):
#     try:
#         url = book_page_url + str(book_id)
#         response = requests.get(url)
#         response.raise_for_status()
#     except (ConnectionError, HTTPError):
#         continue

#     soup = BeautifulSoup(response.text, "lxml")

#     title_text = soup.find("h1").text
#     title_splitted = title_text.split("::")
#     title = title_splitted[0].strip()
#     img = soup.find("div", class_="bookimage").find("img")["src"]

#     print("Заголовок:", title)
#     print(img)

response = requests.get(url, allow_redirects=False)
response.raise_for_status()

soup = BeautifulSoup(response.text, "lxml")
img = soup.find("div", class_="bookimage").find("img")["src"]

print(img)
