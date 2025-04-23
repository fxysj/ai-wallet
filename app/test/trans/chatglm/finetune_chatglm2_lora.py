import torch
from transformers import AutoTokenizer, AutoModel
from peft import get_peft_model, LoraConfig, TaskType
from datasets import load_dataset
from torch.utils.data import DataLoader
from transformers import TrainingArguments, Trainer
from transformers import DataCollatorForSeq2Seq

# 加载 ChatGLM2 模型和分词器（支持多语言）
model_name = "THUDM/chatglm2-6b"
tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
model = AutoModel.from_pretrained(model_name, trust_remote_code=True, device_map="auto")

# 启用推理模式（节省内存）
model.eval()

# 构建 LoRA 配置
peft_config = LoraConfig(
    task_type=TaskType.CAUSAL_LM,  # 因果语言建模
    r=8,                           # Rank 值，控制 LoRA 子空间的维度
    lora_alpha=32,                # 放大因子
    lora_dropout=0.1,             # Dropout 避免过拟合
    bias="none",                  # 不对 bias 做 LoRA
    target_modules=["query_key_value"]  # 指定注入 LoRA 的模块（ChatGLM 特有模块名）
)

# 注入 LoRA 到原始模型中
model = get_peft_model(model, peft_config)

# 加载一个小规模中文问答数据集（你可以替换为 CMRC、DuReader 等）
dataset = load_dataset("json", data_files={"train": "data/train.json", "test": "data/test.json"})

# 数据格式预处理函数：将 "instruction" + "input" 拼接为 prompt，output 作为标签
def preprocess_function(example):
    prompt = example["instruction"] + "\n" + example["input"]
    inputs = tokenizer(prompt, truncation=True, padding="max_length", max_length=512)
    labels = tokenizer(example["output"], truncation=True, padding="max_length", max_length=512)
    inputs["labels"] = labels["input_ids"]
    return inputs

# 应用预处理
tokenized_dataset = dataset.map(preprocess_function)

# 构建 DataLoader 用于 Trainer
data_collator = DataCollatorForSeq2Seq(tokenizer=tokenizer, model=model)

# 设置训练参数
training_args = TrainingArguments(
    output_dir="./chatglm2-lora-output",
    per_device_train_batch_size=1,
    gradient_accumulation_steps=4,
    num_train_epochs=2,
    logging_steps=10,
    save_strategy="epoch",
    learning_rate=2e-4,
    fp16=True,
    remove_unused_columns=False
)

# 使用 HuggingFace Trainer 封装训练流程
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_dataset["train"],
    eval_dataset=tokenized_dataset["test"],
    tokenizer=tokenizer,
    data_collator=data_collator
)

# 开始训练
trainer.train()
