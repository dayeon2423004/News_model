# モデル一貫

import json
from datasets import Dataset
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, Seq2SeqTrainer, Seq2SeqTrainingArguments
import torch
from transformers import AutoTokenizer

# 1. summary_articles.json の読み込み
with open("summary_articles.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# 2. 本文（content）と要約（summary）を抽出してデータセットを作成
articles = [{"content": article["content"], "summary": article["summary"]} for article in data]

# 3. データセットを Hugging Face の Dataset に変換
dataset = Dataset.from_dict({
    "content": [article["content"] for article in articles],
    "summary": [article["summary"] for article in articles]
})

# 4. データセットをトレーニングと評価用に分ける（例：80%トレーニング、20%評価）
train_size = int(0.8 * len(dataset))
train_dataset = dataset.select(range(train_size))
eval_dataset = dataset.select(range(train_size, len(dataset)))

# 5. モデルとトークナイザーの読み込み（例: T5 または KoBART）
model_name = "google/mt5-small"  # もしくは KoBART や他のモデルに変更可能
tokenizer = AutoTokenizer.from_pretrained("google/mt5-small", use_fast=False)
model = AutoModelForSeq2SeqLM.from_pretrained(model_name)

# 6. データの前処理（トークナイズ）
def preprocess_function(examples):
    # 入力に "summarize: " を追加
    inputs = ["summarize: " + doc for doc in examples["content"]]
    model_inputs = tokenizer(inputs, max_length=512, truncation=True, padding="max_length")

    with tokenizer.as_target_tokenizer():
        labels = tokenizer(examples["summary"], max_length=128, truncation=True, padding="max_length")

    model_inputs["labels"] = labels["input_ids"]
    return model_inputs

# トークナイズをデータセットに適用
train_dataset = train_dataset.map(preprocess_function, batched=True)
eval_dataset = eval_dataset.map(preprocess_function, batched=True)

# 7. トレーニング設定
training_args = Seq2SeqTrainingArguments(
    output_dir="./results",  # 結果の保存
    eval_steps=100,  # 100ステップごとに評価
    save_strategy="epoch",  # エポックごとにモデルを保存
    learning_rate=3e-5,
    per_device_train_batch_size=4,
    per_device_eval_batch_size=4,
    num_train_epochs=3,
    weight_decay=0.01,
    save_total_limit=2,
    predict_with_generate=True,
    logging_dir="./logs",
    logging_steps=100,
    fp16=torch.cuda.is_available(),  # GPU使用時はTrue
    report_to="none",  # wandbの無効化
)

# 8. Trainer 作成
trainer = Seq2SeqTrainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=eval_dataset,
    tokenizer=tokenizer,
)

# 9. 学習実行
trainer.train()

# 10. モデルの保存
trainer.save_model("./fine_tuned_model")
tokenizer.save_pretrained("./fine_tuned_model")

# 11. 推論（要約）の関数
def summarize_text(text):
    # 長文を入力としてトークナイズ
    inputs = tokenizer("summarize: " + text, return_tensors="pt", max_length=512, truncation=True)
    inputs = inputs.to(model.device)  # この行を追加
    summary_ids = model.generate(inputs["input_ids"], max_length=150, num_beams=4, early_stopping=True)
    summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)
    return summary

# 12. 長文を分割して要約を行う関数
def split_text(text, max_length=500):
    sentences = text.split("。")  # 日本語の場合、句点で分ける
    sections = []
    current_section = ""

    for sentence in sentences:
        if len(current_section + sentence) < max_length:
            current_section += sentence + "。"
        else:
            sections.append(current_section)
            current_section = sentence + "。"

    if current_section:
        sections.append(current_section)

    return sections

# 13. テストデータの読み込み（test_articles.json）
with open("test_articles.json", "r", encoding="utf-8") as f:
    test_data = json.load(f)

# 14. テストデータの要約生成
for i, article in enumerate(test_data):
    text_to_summarize = article["content"]  # テストデータの本文
    sections = split_text(text_to_summarize)  # 長文を分割
    summaries = [summarize_text(section) for section in sections]  # 各セクションを要約
    final_summary = " ".join(summaries)  # 最後に全ての要約を統合
    print(f"記事{i+1}の要約: {final_summary}")