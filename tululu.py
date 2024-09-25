import requests
from bs4 import BeautifulSoup

url = "https://tululu.org/b1/"
response = requests.get(url)
response.raise_for_status()

soup = BeautifulSoup(response.text, "lxml")

title_text = soup.find("h1").text
title_splitted = title_text.split("::")
title = title_splitted[0].strip()
author = title_splitted[1].strip()

print("Заголовок:", title)
print("Автор:", author)
