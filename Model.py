# Model code

import json
from datasets import Dataset
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, Seq2SeqTrainer, Seq2SeqTrainingArguments
import torch

# 1. データの読み込み（converted_dataset.json）
with open("cleaned_dataset2.json", "r", encoding="utf-8") as f:
    converted_data = json.load(f)

# 2. Hugging Face Dataset 形式に変換
dataset = Dataset.from_dict({
    "content": [item["content"] for item in converted_data],
    "summary": [item["summary"] for item in converted_data]
})

# 3. トレーニング / 評価データに分割
train_size = int(0.8 * len(dataset))
train_dataset = dataset.select(range(train_size))
eval_dataset = dataset.select(range(train_size, len(dataset)))

# 4. モデルとトークナイザーの読み込み（KoBART）
model_name = "digit82/kobart-summarization"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSeq2SeqLM.from_pretrained(model_name)

# 5. データの前処理（トークナイズ）
def preprocess_function(examples):
    model_inputs = tokenizer(examples["content"], max_length=512, truncation=True, padding="max_length")

    # KoBARTではターゲットも同様にtokenizeする（as_target_tokenizerは非推奨）
    with tokenizer.as_target_tokenizer():
        labels = tokenizer(examples["summary"], max_length=128, truncation=True, padding="max_length")

    model_inputs["labels"] = labels["input_ids"]
    return model_inputs

train_dataset = train_dataset.map(preprocess_function, batched=True)
eval_dataset = eval_dataset.map(preprocess_function, batched=True)

# 6. トレーニング設定
training_args = Seq2SeqTrainingArguments(
    output_dir="./kobart_results",
    # evaluation_strategy="epoch", # この行を削除
    eval_strategy="epoch", # eval_strategy に変更
    save_strategy="epoch",
    learning_rate=3e-5,
    per_device_train_batch_size=4,
    per_device_eval_batch_size=4,
    num_train_epochs=3,
    weight_decay=0.01,
    save_total_limit=2,
    predict_with_generate=True,
    logging_dir="./logs",
    logging_steps=100,
    fp16=torch.cuda.is_available(),
    report_to="none",
)

# 7. Trainer 作成と学習
trainer = Seq2SeqTrainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=eval_dataset,
    tokenizer=tokenizer,
)

trainer.train()

# 8. モデル保存
trainer.save_model("./kobart_fine_tuned")
tokenizer.save_pretrained("./kobart_fine_tuned")

# 9. 推論関数
def summarize_text(text):
    inputs = tokenizer(text, return_tensors="pt", max_length=512, truncation=True)
    inputs = inputs.to(model.device)
    summary_ids = model.generate(inputs["input_ids"], max_length=150, num_beams=4, early_stopping=True)
    summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)
    return summary

# 10. 長文分割関数（韓国語用）
def split_text(text, max_length=500):
    sentences = text.split("다.")  # 韓国語の文末句点で分割（簡易）
    sections = []
    current = ""
    for sentence in sentences:
        if len(current + sentence) < max_length:
            current += sentence + "다."
        else:
            sections.append(current)
            current = sentence + "다."
    if current:
        sections.append(current)
    return sections

# 11. テストデータから要約
with open("cleaned_testdataset.json", "r", encoding="utf-8") as f:
    test_data = json.load(f)

for i, article in enumerate(test_data):
    text_to_summarize = article["content"]
    sections = split_text(text_to_summarize)
    summaries = [summarize_text(section) for section in sections]
    final_summary = " ".join(summaries)
    print(f"記事{i+1}の要약: {final_summary}")