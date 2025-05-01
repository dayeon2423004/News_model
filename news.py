from selenium import webdriver
from selenium.webdriver.common.by import By
from newspaper import Article
import time
from API_summarizer import summarizer


# 페이지 제한
page_count = 0
max_pages = 3

drive = webdriver.Chrome() # bot으로 차단될 수 있으나, requests로 접근이 아닌 selenium을 사용해 사람처럼 작동시킴.
drive.get("https://www.google.com/search?q=%EC%9D%BC%EB%B3%B8+%EA%B8%B0%EC%88%A0&sca_esv=b6fb1ac6b7a40b74&biw=1275&bih=1311&tbm=nws&ei=SX4CaIucEaqo2roP6f_q2A8&ved=0ahUKEwjL5ObbgOKMAxUqlFYBHem_GvsQ4dUDCA4&uact=5&oq=%EC%9D%BC%EB%B3%B8+%EA%B8%B0%EC%88%A0&gs_lp=Egxnd3Mtd2l6LW5ld3MiDeydvOuzuCDquLDsiKAyChAAGIAEGEMYigUyBRAAGIAEMgUQABiABDIFEAAYgAQyBRAAGIAEMgUQABiABDIFEAAYgAQyBRAAGIAEMgUQABiABDIFEAAYgARI8g5QnAZYsg1wAXgAkAEBmAFzoAHnBqoBAzAuOLgBA8gBAPgBAZgCCKACsAbCAgQQABgewgIEEAAYA8ICCxAAGIAEGLEDGIMBwgIIEAAYgAQYsQOYAwCIBgGSBwMxLjegB9gssgcDMC43uAeqBg&sclient=gws-wiz-news")
time.sleep(2)

# 중복 검사를 위한 set()
visited_links = set()

def newsdata():
    global drive, visited_links, page_count, max_pages
    dict_data = []

    while page_count < max_pages:
    
        # 뉴스 기사 선택
        news_link = drive.find_elements(By.CSS_SELECTOR, "a.WlydOe")
        
        # herf 기능 꺼내 기사 수집
        for item in news_link:
            link = item.get_attribute("href")
            print(link) # 확인
            
            # 중복 확인
            if link in visited_links:
                continue
            try:
                # 기사 클릭 (Newspaper 시 동적 로딩 될 수 있기에 URL만 받기)
                # news_link[0].click()
                # 기사 수집
                article = Article(link, language = 'ko')
                # 다운로드
                article.download()
                # 파싱
                article.parse()
            except:
                continue

            clean_text = ' '.join(article.text.split())
            
            if not clean_text or not article.publish_date:
                print("본문 또는 날짜 없음. 패스")
                continue
            # elif len(clean_text.strip()) < 100:
            #     print("짧아서 패스.")
            #     continue

            # print("제목:", article.title)
            print("본문:", clean_text)
            print("URL:", link)
            # print("날짜:", article.publish_date)
            print("-----" * 5)

            data = {
                    "제목" : article.title,
                    "본문" : clean_text,
                    "URL" : link,
                    "날짜" : article.publish_date
                    }
            
            time.sleep(2)
            
            # 요약 실행
            summarizer_data = summarizer(clean_text)
            data.update(summarizer_data) 

            # # 뒤로 가기 (클릭을 하지 않아 자동적으로 필요 X.)
            # drive.back()

            # 데이터 추가
            dict_data.append(data)  

            time.sleep(2)
            
        # 다음 페이지 옮기기
        next_page = drive.find_element(By.CSS_SELECTOR, "a#pnnext")
        next_page.click()

        page_count += 1
        time.sleep(2)
        
    # 드라이브 종료 후 마지막에 리스트 of 딕셔너리 형태로 반환
    drive.quit()
    return dict_data

# test = newsdata()
# print(test)