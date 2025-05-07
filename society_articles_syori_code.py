# 前処理　ノイズ削除、日付１つに統一
# jsonに保存した記事ファイルの前処理

import json
import re

def clean_article_content(text):
    if not text:
        return ""
    
    patterns = [
        r'\b구독\b', r'\b이미지 확대\b', r'\b유튜브로 보기\b', r'\byoutube\b',
        r'헬로 아카이브 구매하기', r'\[[^\]]*자료사진[^\]]*\]', r'\[[^\]]*\]',
        r'\([^)]+\)',  # 括弧内全般（例：(서울=연합뉴스) など）
        r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+',  # メール
        r'\b저작권자\(c\)[^\n]+', r'무단 전재 및 재배포 금지', r'▶.*?더보기',
        r'영상보기', r'사진.*?제공', r'\d{4}\.\d{2}\.\d{2}.*?입력',
        r'\n*관련 기사.*?\n*', r'\n*관련 링크.*?\n*', r'※.*?\n', r'■.*?뉴스',
        r'\b스크랩\b', r'\b인쇄\b', r'\b닫기\b', r'\b공유하기\b', r'\b모바일경향\b',
        r'\b저장\b', r'\b공유\b', r'\b댓글\b', r'\b좋아요\b', r'^\[영상\]', r'…',
        r'[▶◀■◆★●■□△▲▼→←※※#]+', r'【.*?】', r'^\s+', r'\s+$'
    ]
    
    for pattern in patterns:
        text = re.sub(pattern, ' ', text, flags=re.MULTILINE)
    
    # 連続空白・改行を1つにまとめる
    text = re.sub(r'\s+', ' ', text)
    
    return text.strip()

def simplify_date(date_field):
    if isinstance(date_field, list) and date_field:
        return date_field[0]
    elif isinstance(date_field, str):
        return date_field
    else:
        return ""

def process_json(input_path, output_path):
    with open(input_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    for article in data:
        article['content'] = clean_article_content(article.get('content', ''))
        article['date'] = simplify_date(article.get('date'))

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    input_file = "society_articles.json"
    output_file = "final_cleaned_articles.json"
    process_json(input_file, output_file)
    print(f"前処理完了！→ {output_file}")


