# １５０件収集コード

import csv
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

# =====================
# 設定
# =====================
output_file = "v2_collected_articles.csv"
max_total = 150  # 合計目標件数
page_num = 1
collected_data = []
existing_titles = set()
fail_count = 0
max_fails = 10  # 連続10回失敗したら止める

# =====================
# 既存のCSV読み込み
# =====================
if os.path.exists(output_file):
    with open(output_file, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            existing_titles.add(row["title"])
            collected_data.append(row)

print(f"🔎 既存記事数: {len(collected_data)}件")

# =====================
# ブラウザ設定
# =====================
options = webdriver.ChromeOptions()
options.add_argument("--headless")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
driver.implicitly_wait(10)

try:
    while len(collected_data) < max_total:
        url = f"https://www.yna.co.kr/news?site=navi_news&p={page_num}"
        print(f"\n📄 ページ移動: {url}")
        driver.get(url)
        time.sleep(2)

        articles = driver.find_elements(By.CSS_SELECTOR, "a[href*='/view/']")
        article_data = []

        for article in articles:
            link = article.get_attribute("href")
            title = article.text.strip()
            if title and title not in existing_titles:
                article_data.append((title, link))

        success_in_page = 0  # ←このページで成功した件数

        for title, link in article_data:
            try:
                driver.get(link)
                time.sleep(2)
            except Exception as e:
                print(f"❌ アクセス失敗（{title}）: {e}")
                continue

            content = None
            try:
                content_element = driver.find_element(By.CSS_SELECTOR, ".article-text")
                content = content_element.text
            except:
                try:
                    content_element = driver.find_element(By.CSS_SELECTOR, ".story-news")
                    content = content_element.text
                except:
                    print(f"❌ 本文が見つかりませんでした（{title}）")
                    continue

            try:
                date_element = driver.find_element(By.CSS_SELECTOR, ".update-time")
                date_text = date_element.text.strip()
            except:
                date_text = "日付なし"

            if content:
                collected_data.append({
                    "title": title,
                    "date": date_text,
                    "content": content,
                    "url": link
                })
                existing_titles.add(title)
                success_in_page += 1
                print(f"✅ {len(collected_data)}件目: {title}")

            if len(collected_data) >= max_total:
                break

        if success_in_page == 0:
            fail_count += 1
            print(f"⚠️ このページで成功ゼロ。連続失敗数: {fail_count}")
        else:
            fail_count = 0

        if fail_count >= max_fails:
            print("⚠️ 連続失敗が多いため、安全のため停止します。")
            raise KeyboardInterrupt

        page_num += 1

except KeyboardInterrupt:
    print("🛑 ユーザーが中断しました")

except Exception as e:
    print(f"🔥 予期せぬエラー: {e}")

finally:
    driver.quit()
    with open(output_file, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["title", "date", "content", "url"])
        writer.writeheader()
        writer.writerows(collected_data)

    print(f"🎉 完了！合計 {len(collected_data)} 件をCSVに保存しました（重複なし）！")
