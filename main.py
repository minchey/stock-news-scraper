import requests
from bs4 import BeautifulSoup

# ======================
# 1. 설정
# ======================

URL = "https://news.naver.com/section/101"  # 네이버 경제 섹션

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

TARGET_MEDIA = [
    "한국경제", "한경", "매일경제", "서울경제",
    "머니투데이", "이데일리", "아시아경제",
    "조선비즈", "전자신문", "디지털데일리",
    "연합뉴스", "연합뉴스TV"
]

KEYWORDS = [
    # 시장
    "주식", "증시", "코스피", "코스닥", "시총",
    "급등", "급락", "반등", "하락",

    # 기업
    "삼성", "SK", "하이닉스", "엔비디아",
    "현대차", "LG", "카카오", "네이버",

    # 거시경제
    "금리", "환율", "물가", "CPI", "인플레이션",
    "연준", "FOMC",

    # 기술
    "AI", "반도체", "HBM", "데이터센터"
]

# ======================
# 2. 필터 함수
# ======================

def is_target_media(media: str) -> bool:
    return any(m in media for m in TARGET_MEDIA)

def has_keyword(title: str) -> bool:
    return any(keyword in title for keyword in KEYWORDS)

def is_useful_news(news: dict) -> bool:
    return (
        is_target_media(news["media"])
        and has_keyword(news["title"])
    )

# ======================
# 3. 뉴스 수집
# ======================

response = requests.get(URL, headers=HEADERS)
soup = BeautifulSoup(response.text, "html.parser")

scraped_news = []

# 기사 카드 단위
articles = soup.select("div.sa_text")

for article in articles:
    title_tag = article.select_one("a.sa_text_title")
    media_tag = article.select_one("div.sa_text_press")

    if not title_tag or not media_tag:
        continue

    title = title_tag.get_text(strip=True)
    media = media_tag.get_text(strip=True)

    scraped_news.append({
        "title": title,
        "media": media
    })

# ======================
# 4. 필터 적용
# ======================

filtered_news = []

for news in scraped_news:
    if is_useful_news(news):
        filtered_news.append(news)

# ======================
# 5. 결과 출력
# ======================

print(f"전체 수집 뉴스 수: {len(scraped_news)}")
print(f"필터 통과 뉴스 수: {len(filtered_news)}")
print("-" * 50)

for news in filtered_news:
    print(f"[{news['media']}] {news['title']}")
