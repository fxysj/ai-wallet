# ✅ 中文数据集 + 中文模型训练 (基础示例)
# 使用 Transformers + Datasets + BertForSequenceClassification
# 模型：bert-base-chinese
# 数据：自定义中文情感分类 CSV（假设两列 text, label）

from datasets import load_dataset
from transformers import BertTokenizer, BertForSequenceClassification, Trainer, TrainingArguments
import torch

# ✅ 1. 加载自定义 CSV 中文数据集
# 假设数据格式为 CSV，包含 'text', 'label' 两列
dataset = load_dataset("csv", data_files={
    "train": "train.csv",
    "validation": "val.csv"
})

# ✅ 2. 加载 tokenizer
model_name = "bert-base-chinese"
tokenizer = BertTokenizer.from_pretrained(model_name)

# ✅ 3. 对文本进行编码（tokenize）
def preprocess(example):
    return tokenizer(
        example['text'],
        padding="max_length",
        truncation=True,
        max_length=128
    )

tokenized_dataset = dataset.map(preprocess, batched=True)
tokenized_dataset.set_format(type="torch", columns=["input_ids", "attention_mask", "label"])

# ✅ 4. 加载模型
model = BertForSequenceClassification.from_pretrained(model_name, num_labels=2)

# ✅ 5. 配置训练参数（可用于 FSDP、TensorBoard）
training_args = TrainingArguments(
    output_dir="./outputs",
    evaluation_strategy="epoch",
    save_strategy="epoch",
    per_device_train_batch_size=16,
    per_device_eval_batch_size=16,
    num_train_epochs=3,
    logging_dir="./logs",
    logging_steps=10,
    report_to="tensorboard",

    # ✅ 加入 FSDP 支持
    fsdp="full_shard auto_wrap",  # 使用 FSDP
    fsdp_transformer_layer_cls_to_wrap="BertLayer",  # 指定 FSDP 包裹的类
    fp16=True,  # 启用混合精度训练
)

# ✅ 6. 使用 Trainer API 训练模型
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_dataset["train"],
    eval_dataset=tokenized_dataset["validation"]
)

# ✅ 7. 开始训练
trainer.train()

# ✅ 8. 启动 TensorBoard 查看训练过程
# 运行命令：tensorboard --logdir=./logs
