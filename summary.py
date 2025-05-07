# summary code
# 500以内

import json
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

model_name = "psyche/KoT5-summarization"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSeq2SeqLM.from_pretrained(model_name)

def summarize_korean(text, min_length=300, max_token_length=450):
    input_text = "summarize: " + text
    input_ids = tokenizer.encode(input_text, return_tensors="pt", truncation=True, max_length=512)

    output_ids = model.generate(
        input_ids,
        min_length=min_length,
        max_length=max_token_length,  # ← トークン数の上限を少し小さく
        num_beams=4,
        early_stopping=True
    )

    summary = tokenizer.decode(output_ids[0], skip_special_tokens=True)

    # ✅ 500文字以内に自然に収める処理（句点・다で切る）
    if len(summary) > 500:
        cut_index = summary[:500].rfind("。")  # 日本語句点
        if cut_index != -1:
            summary = summary[:cut_index + 1]
        else:
            cut_index = summary[:500].rfind("다")  # 韓国語文末
            if cut_index != -1:
                summary = summary[:cut_index + 1]
            else:
                summary = summary[:500] + "…"

    return summary

filename = "final_cleaned_articles.json"

with open(filename, "r", encoding="utf-8") as f:
    data = json.load(f)

for i, article in enumerate(data):
    content = article.get("content", "")
    try:
        summary = summarize_korean(content, min_length=300, max_token_length=450)

        # 原文が短くて要約も短い場合は許容
        if len(summary) < 300 and len(content) < 350:
            pass
        elif len(summary) < 300:
            raise ValueError("要約が短すぎます")

        article["summary"] = summary
        print(f"[{i+1}/{len(data)}]  要約完了（{len(summary)}文字）")
    except Exception as e:
        article["summary"] = ""
        print(f"[{i+1}/{len(data)}]  要約失敗: {e}")

output_name = "summary_articles.json"
with open(output_name, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("すべての処理が完了しました！")