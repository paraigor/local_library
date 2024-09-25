import requests
from bs4 import BeautifulSoup

url = "https://www.franksonnenbergonline.com/blog/are-you-grateful/"
response = requests.get(url)
response.raise_for_status()

soup = BeautifulSoup(response.text, "lxml")

title_text = soup.find("h1", class_="entry-title").text

img = soup.find("img", class_="attachment-post-image")["src"]

post_content = soup.find("div", class_="entry-content").text

print(title_text)
print()
print(img)
print()
print(post_content)
