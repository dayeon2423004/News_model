# voice
# Api key
# command : uvicorn api_voice:app --reload

from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from transformers import BartForConditionalGeneration, PreTrainedTokenizerFast
from newspaper import Article
from gtts import gTTS
import uuid
import os

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 必要に応じてオリジン指定可
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MODEL_DIR = "./kobart_fine_tuned"
model = BartForConditionalGeneration.from_pretrained(MODEL_DIR)
tokenizer = PreTrainedTokenizerFast.from_pretrained(MODEL_DIR)

TEMP_DIR = "./temp_audio"
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
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"記事の取得に失敗しました: {e}")

    if not text.strip():
        raise HTTPException(status_code=404, detail="記事本文が空です")

    inputs = tokenizer(text, return_tensors="pt", max_length=1024, truncation=True)
    summary_ids = model.generate(inputs["input_ids"], max_length=300, min_length=30, length_penalty=2.0, num_beams=4)
    summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)

    # 音声ファイルを一時保存
    filename = f"{uuid.uuid4().hex}.mp3"
    filepath = os.path.join(TEMP_DIR, filename)
    tts = gTTS(summary, lang="ko")
    tts.save(filepath)

    # 要約文と音声ファイルのURLを返す
    return {
        "summary": summary,
        "audio_url": f"/audio/{filename}"
    }

# 音声ファイル提供エンドポイント
@app.get("/audio/{filename}")
def get_audio(filename: str):
    filepath = os.path.join(TEMP_DIR, filename)
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="音声ファイルが存在しません")
    return FileResponse(filepath, media_type="audio/mpeg", filename="summary.mp3")