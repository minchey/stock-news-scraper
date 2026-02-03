import requests
from bs4 import BeautifulSoup

url = "https://news.naver.com"
response = requests.get(url)

soup = BeautifulSoup(response.text, "html.parser")

links = soup.find_all("a")

for link in links:
    text = link.get_text().strip()
    if len(text) > 15:
        print(text)