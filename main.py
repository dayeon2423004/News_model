# API key

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from transformers import BartForConditionalGeneration, PreTrainedTokenizerFast
import torch
from newspaper import Article  # ←★ これを忘れずに！
import os

app = FastAPI()

# モデル読み込み（パスは適切に調整）
MODEL_DIR = "./kobart_fine_tuned"
model = BartForConditionalGeneration.from_pretrained(MODEL_DIR)
tokenizer = PreTrainedTokenizerFast.from_pretrained(MODEL_DIR)

class URLRequest(BaseModel):
    url: str

@app.post("/summarize")
def summarize_article(request: URLRequest):
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

    return {"summary": summary}
