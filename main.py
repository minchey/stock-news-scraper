import requests
from bs4 import BeautifulSoup
import time

# ======================
# 1. 설정
# ======================

LIST_URL = "https://news.naver.com/section/101"

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
    "주식", "증시", "코스피", "코스닥",
    "삼성", "SK", "하이닉스", "엔비디아",
    "금리", "환율", "물가", "CPI",
    "AI", "반도체", "HBM"
]

# ======================
# 2. 필터 함수
# ======================

def is_target_media(media: str) -> bool:
    return any(m in media for m in TARGET_MEDIA)

def has_keyword(title: str) -> bool:
    return any(keyword in title for keyword in KEYWORDS)

# ======================
# 3. 기사 요약 추출
# ======================

def get_article_summary(article_url: str) -> str:
    try:
        response = requests.get(article_url, headers=HEADERS, timeout=5)
        soup = BeautifulSoup(response.text, "html.parser")

        # 네이버 뉴스 본문
        content = soup.select_one("#dic_area")
        if not content:
            return ""

        # 첫 문단만 추출
        paragraphs = content.get_text("\n", strip=True).split("\n")
        return paragraphs[0]

    except Exception:
        return ""

# ======================
# 4. 뉴스 수집
# ======================

response = requests.get(LIST_URL, headers=HEADERS)
soup = BeautifulSoup(response.text, "html.parser")

scraped_news = []

articles = soup.select("div.sa_text")

for article in articles:
    title_tag = article.select_one("a.sa_text_title")
    media_tag = article.select_one("div.sa_text_press")

    if not title_tag or not media_tag:
        continue

    title = title_tag.get_text(strip=True)
    media = media_tag.get_text(strip=True)
    link = title_tag["href"]

    # 1차 필터
    if not (is_target_media(media) and has_keyword(title)):
        continue

    summary = get_article_summary(link)

    scraped_news.append({
        "media": media,
        "title": title,
        "summary": summary
    })

    time.sleep(0.3)  # 서버 배려

# ======================
# 5. 결과 출력
# ======================

print(f"최종 분석 대상 뉴스 수: {len(scraped_news)}")
print("-" * 60)

for news in scraped_news:
    print(f"[{news['media']}] {news['title']}")
    print(f"요약: {news['summary']}")
    print("-" * 60)
