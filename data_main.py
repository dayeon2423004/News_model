import pandas as pd
from news import newsdata
import datetime

articles = newsdata()

# ✅ 날짜를 문자열로 변환
for article in articles:
    if isinstance(article["날짜"], datetime.datetime):
        article["날짜"] = article["날짜"].strftime("%Y-%m-%d %H:%M:%S")

# ✅ 데이터 확인
print(f"기사 수: {len(articles)}")
print(articles[0])  # 첫 번째 기사만 보기

# ✅ DataFrame 생성 후 저장
df = pd.DataFrame(articles)
df.to_csv("my_data.csv", index=False, encoding='utf-8-sig')
