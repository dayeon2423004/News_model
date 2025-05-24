# voice
# Api key
# 실행 command : uvicorn new_api_voice:app --reload

from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from transformers import MT5ForConditionalGeneration, T5Tokenizer
from transformers import BartForConditionalGeneration, PreTrainedTokenizerFast
from newspaper import Article
from gtts import gTTS
import uuid
import os
import pymysql
from 매일자동실행 import start_scheduler
import asyncio

from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request

from fastapi.responses import HTMLResponse

app = FastAPI()

# --- CORS 허용 설정 ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})




# # 데이터 베이스 연결
# def save_to_db(title, content, url, date, summary, personality, audio_url):
#     conn = pymysql.connect(
#         host='localhost',
#         user='root',
#         passwd='0000',
#         database='SHOW_NEWSMODEL',
#         port=3306,
#         charset='utf8mb4'
#     )
#     cursor = conn.cursor()
#     insert_sql = '''
#         INSERT INTO news_summary (title, content, url, date, summary, personality, audio_url)
#         VALUES (%s, %s, %s, %s, %s, %s, %s)
#     '''
#     cursor.execute(insert_sql, (title, content, url, date, summary, personality, audio_url))
#     conn.commit()
#     cursor.close()
#     conn.close()

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],  # 모든 출처(*)에서 오는 요청을 허용하는 CORS 설정입니다. 프론트엔드와 통신할 때 사용
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# MODEL_DIR1 = "kobart_fine_tuned"
MODEL_DIR2 = "./finetuned-koelectra"

MODEL_DIR1 = "./kobart_fine_tuned"
model1 = BartForConditionalGeneration.from_pretrained(MODEL_DIR1)
tokenizer1 = PreTrainedTokenizerFast.from_pretrained(MODEL_DIR1)

tokenizer2 = AutoTokenizer.from_pretrained(MODEL_DIR2)
model2 = AutoModelForSequenceClassification.from_pretrained(MODEL_DIR2)


TEMP_DIR = "./temp_audio" # 음성 파일 임시 저장 폴더
os.makedirs(TEMP_DIR, exist_ok=True)

class URLRequest(BaseModel):
    url: str

@app.post("/summarize/audio")
def summarize_article_audio(request: URLRequest):
    try:
        article = Article(request.url, language='ko')
        article.download()
        article.parse()
        text = article.text
        title = article.title
        publish_date = article.publish_date
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"기사 수집에 실패했습니다.: {e}")

    if not text.strip():
        raise HTTPException(status_code=404, detail="기사 본문이 비어 있습니다.")

    # 1. 요약 생성
    inputs = tokenizer1(text, return_tensors="pt", max_length=1024, truncation=True)
    summary_ids = model1.generate(inputs["input_ids"], max_length=300, min_length=30, length_penalty=2.0, num_beams=4)
    summary = tokenizer1.decode(summary_ids[0], skip_special_tokens=True)

    # 2. 감정 분석
    emo_inputs = tokenizer2(text, return_tensors="pt", truncation=True, max_length=512)
    emo_outputs = model2(**emo_inputs)
    predicted_label = int(emo_outputs.logits.argmax(dim=1))

    # 감정 라벨 정의 (예시: KoELECTRA 감정 모델이 3클래스인 경우)
    label_map = {
        0: "비판",
        1: "중립",
        2: "긍정"
    }
    emotion = label_map.get(predicted_label, "알 수 없음") # 3 또는 4가 나올 경우 알 수 없음 반환
    personality = emotion  # DB에 저장할 감정도 동일하게 사용  

    # TTS 이용한 음성 생성
    filename = f"{uuid.uuid4().hex}.mp3"
    filepath = os.path.join(TEMP_DIR, filename)
    tts = gTTS(summary, lang="ko")
    tts.save(filepath)

    # 날짜 처리
    date_str = publish_date.strftime("%Y-%m-%d") if publish_date else datetime.now().strftime("%Y-%m-%d")

    # # DB 저장
    # save_to_db(
    #     title=title,
    #     content=text,
    #     url=request.url,
    #     date=date_str,
    #     summary=summary,
    #     personality=personality,
    #     audio_url=filename
    # )

    # 3. 반환
    return {
        "summary": summary,
        "emotion": emotion,
        "audio_url": f"/audio/{filename}"
    }

# 音声ファイル提供エンドポイント
@app.get("/audio/{filename}")
def get_audio(filename: str):
    filepath = os.path.join(TEMP_DIR, filename)
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="음성 파일이 존재하지 않습니다.")
    return FileResponse(filepath, media_type="audio/mpeg", filename="summary.mp3")


# @app.on_event("startup")
# async def startup_event():
#     # 서버가 완전히 기동된 후 지연을 주고 스케줄러 시작
#     async def delayed_scheduler_start():
#         await asyncio.sleep(3)  # 3초 대기 (필요에 따라 조정)
#         start_scheduler()
    
#     asyncio.create_task(delayed_scheduler_start())
