import requests

url = "https://news.naver.com"

response = requests.get(url)

print(response.status_code)
print(response.text[:500])  # 앞부분만 출력