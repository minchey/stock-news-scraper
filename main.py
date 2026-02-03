import requests
from bs4 import BeautifulSoup

import time

import json
from datetime import datetime

import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

response = client.chat.completions.create(
    model="gpt-4.1-mini",
    messages=[
        {"role": "user", "content": "한 문장으로 오늘 주식 시장을 표현해줘"}
    ]
)

print("AI 응답:")
print(response.choices[0].message.content)



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
# 3. 기사 상세 정보 추출
# ======================

def get_article_detail(article_url: str) -> dict:
    try:
        response = requests.get(article_url, headers=HEADERS, timeout=5)
        soup = BeautifulSoup(response.text, "html.parser")

        # 본문
        content = soup.select_one("#dic_area")
        if not content:
            return {}

        paragraphs = content.get_text("\n", strip=True).split("\n")
        summary = paragraphs[0]

        # 날짜/시간
        date_tag = soup.select_one(
            "span.media_end_head_info_datestamp_time"
        )
        published_at = date_tag.get_text(strip=True) if date_tag else ""

        return {
            "summary": summary,
            "published_at": published_at
        }

    except Exception:
        return {}

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

    detail = get_article_detail(link)
    if not detail:
        continue

    scraped_news.append({
        "media": media,
        "title": title,
        "summary": detail["summary"],
        "published_at": detail["published_at"],
        "collected_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })

    time.sleep(0.3)

# ======================
# 5. JSON 파일 저장
# ======================

filename = f"news_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

with open(filename, "w", encoding="utf-8") as f:
    json.dump(scraped_news, f, ensure_ascii=False, indent=2)

print(f"저장 완료: {filename}")
print(f"총 뉴스 수: {len(scraped_news)}")
