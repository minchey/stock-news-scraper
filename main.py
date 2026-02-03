import requests
from bs4 import BeautifulSoup

import time

import json
from datetime import datetime

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

# ======================
# 6. 프롬프트 생성
# ======================

def build_prompt(news_list: list) -> str:
    prompt_header = """
너는 주식·경제 뉴스를 분석하는 금융 시장 애널리스트다.
단기 투자자 관점에서 아래 뉴스들을 분석하라.

가능하면 오늘 뉴스 전체를 종합해
시장 분위기를 한 단락으로 요약한 뒤
개별 뉴스를 분석하라.

[분석 기준]
1. 뉴스 성격: 호재 / 악재 / 중립
2. 영향 범위: 단기 / 중기 / 장기
3. 관련 섹터 또는 종목
4. 투자 관점 요약 (3줄 이내)
5. 주의할 점

[출력 규칙]
- 뉴스 하나당 분석 블록 하나
- 불필요한 서론 없이 바로 분석
- 과도한 확신 표현은 피할 것

[뉴스 데이터]
"""

    body = ""
    for idx, news in enumerate(news_list, start=1):
        body += f"""
[{idx}]
언론사: {news['media']}
제목: {news['title']}
요약: {news['summary']}
발행시각: {news['published_at']}
"""

    return prompt_header + body

# ======================
# 7. 프롬프트 파일 생성
# ======================

today = datetime.now().strftime("%Y-%m-%d")

prompt_text = build_prompt(scraped_news)

with open(f"analysis_prompt_{today}.txt", "w", encoding="utf-8") as f:
    f.write(prompt_text)

print("프롬프트 파일 생성 완료: analysis_prompt.txt")
