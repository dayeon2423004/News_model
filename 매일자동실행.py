# scheduler.py
from apscheduler.schedulers.background import BackgroundScheduler
from 네이버뉴스크롤링 import crawl_articles

def start_scheduler():
    scheduler = BackgroundScheduler()
    # 뉴스 크롤링 자동화
    scheduler.add_job(crawl_articles, 'cron', hour=7, minute=0)  # 매일 오전 7시
    scheduler.start()

    # 뉴스 크롤링(서버 시작 직후)
    crawl_articles()