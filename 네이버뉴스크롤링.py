from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import pandas as pd
from bs4 import BeautifulSoup
import random
import re
from datetime import datetime
import requests # FestAPI 서버로 요청보내기 위한 import

def crawl_articles():
    # 크롬 드라이버 설정
    options = Options()
    options.add_argument('--start-maximized')
    driver = webdriver.Chrome(options=options)

    # 조선일보 접속
    driver.get("https://www.chosun.com/")
    time.sleep(2)

    # 기사 링크 수집
    elements = driver.find_elements(By.CSS_SELECTOR, "a.story-card__headline")
    links = []

    for el in elements:
        href = el.get_attribute("href")
        if href and href.startswith("https://www.chosun.com") and href not in links:
            links.append(href)

    print(f"📰 수집된 기사 링크 수: {len(links)}")

    # 날짜가 있는 기사만 최대 5개 수집
    valid_articles = []
    random.shuffle(links)

    for link in links:
        if len(valid_articles) >= 5:
            break

        driver.get(link)
        time.sleep(2)
        soup = BeautifulSoup(driver.page_source, "html.parser")

        try:
            # 제목
            title_tag = soup.select_one(".article-header__headline span")
            title = title_tag.text.strip() if title_tag else "제목 없음"

            # 본문
            body_paragraphs = soup.find_all("p", class_=lambda c: c and "article-body__content-text" in c)
            body = "\n".join(p.text.strip() for p in body_paragraphs if p.text.strip())

            # 날짜 추출
            date_block = soup.select_one(".upDate")
            publish_date = None
            if date_block:
                raw_text = date_block.get_text(separator=" ", strip=True)
                date_match = re.search(r"\d{4}\.\d{2}\.\d{2}", raw_text)
                if date_match:
                    # 날짜 형식으로 변환
                    publish_date = datetime.strptime(date_match.group(0), "%Y.%m.%d")

            if not publish_date:
                print(f"⚠️ 날짜 없음 → 기사 스킵: {link}")
                continue

            print(f"\n📌 제목: {title}")
            print(f"🗓️ 날짜: {publish_date.date()}")
            print(f"🔗 URL: {link}")
            print(f"📰 본문 일부:\n{body[:300]}...\n{'-'*60}")

            valid_articles.append({
                "제목": title,
                "본문": body,
                "URL": link,
                "날짜": publish_date
            })

        except Exception as e:
            print(f"❌ 오류 발생: {link} - {e}")
            continue

    driver.quit()

    for article in valid_articles:
        response = requests.post("http://localhost:8000/summarize/audio", json={"url": article["URL"]})
        
        if response.status_code == 200:
            print(f"✅ 처리 성공: {article['제목']}")
        else:
            print(f"❌ 처리 실패: {article['제목']} - {response.text}")


# 추가 정보 : FestAPI서버에서는 uvicorn으로 실행해야 함. (uvicorn api_voice:app --reload)


# # 저장
# df = pd.DataFrame(valid_articles)
# df.to_csv("chosun_articles_with_date.csv", index=False, encoding='utf-8-sig', date_format="%Y-%m-%d")
# print("✅ 날짜 포함된 5개 기사 저장 완료: chosun_articles_with_date.csv")
