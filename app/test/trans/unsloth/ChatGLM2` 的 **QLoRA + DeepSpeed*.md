当然可以！下面是基于 `ChatGLM2` 的 **QLoRA + DeepSpeed** 中文微调的完整代码示例（使用 HuggingFace + Transformers + peft + bitsandbytes + DeepSpeed）。可在消费级 GPU 上进行高效微调。

---

## ✅ 总览

| 模块 | 说明 |
|------|------|
| 模型 | `ChatGLM2-6B`（中文大模型） |
| 微调方法 | `QLoRA`（4bit 量化 + LoRA） |
| 加速框架 | `DeepSpeed`（ZeRO Stage 2/3） |
| 数据集 | 中文指令式微调数据集（如 Alpaca 格式） |

---

## 🧱 1. 安装依赖

```bash
pip install torch transformers datasets accelerate bitsandbytes peft deepspeed
```

---

## 📦 2. DeepSpeed 配置文件（`ds_config_zero2.json`）

```json
{
  "train_batch_size": 8,
  "train_micro_batch_size_per_gpu": 1,
  "gradient_accumulation_steps": 8,
  "gradient_clipping": 1.0,
  "fp16": {
    "enabled": true
  },
  "zero_optimization": {
    "stage": 2,
    "offload_optimizer": {
      "device": "cpu"
    }
  }
}
```

---

## 🧠 3. 微调脚本：`train_chatglm2_qlora_deepspeed.py`

```python
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, TrainingArguments, Trainer, DataCollatorForSeq2Seq
from peft import prepare_model_for_kbit_training, LoraConfig, get_peft_model
from datasets import load_dataset

# 1. 加载 Tokenizer 和 4bit 量化模型
model_name = "THUDM/chatglm2-6b"
tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    load_in_4bit=True,
    device_map="auto",
    trust_remote_code=True
)

# 2. LoRA 配置（QLoRA）
model = prepare_model_for_kbit_training(model)
lora_config = LoraConfig(
    r=8,
    lora_alpha=32,
    target_modules=["query_key_value"],  # ChatGLM 的 LoRA 插入点
    lora_dropout=0.05,
    bias="none",
    task_type="CAUSAL_LM"
)
model = get_peft_model(model, lora_config)

# 3. 加载 Alpaca 格式中文数据
# 格式：[{"instruction": ..., "input": ..., "output": ...}]
dataset = load_dataset("json", data_files="data/alpaca_zh.json", split="train")

def preprocess(example):
    prompt = f"### 问题：\n{example['instruction']}\n{example['input']}\n\n### 回答：\n"
    input_ids = tokenizer(prompt, truncation=True, max_length=512, padding="max_length")
    label_ids = tokenizer(example["output"], truncation=True, max_length=512, padding="max_length")["input_ids"]
    input_ids["labels"] = label_ids
    return input_ids

dataset = dataset.map(preprocess)

# 4. TrainingArguments 启用 DeepSpeed
training_args = TrainingArguments(
    output_dir="chatglm2_qlora_ds_output",
    per_device_train_batch_size=1,
    gradient_accumulation_steps=8,
    num_train_epochs=3,
    learning_rate=2e-4,
    fp16=True,
    logging_steps=10,
    save_strategy="epoch",
    deepspeed="ds_config_zero2.json",
    remove_unused_columns=False,
    report_to="none",
)

# 5. Trainer 启动训练
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=dataset,
    tokenizer=tokenizer,
    data_collator=DataCollatorForSeq2Seq(tokenizer, model),
)

trainer.train()
```

---

## 🚀 4. 启动训练

```bash
deepspeed train_chatglm2_qlora_deepspeed.py
```

---

## 🧪 5. 推理示例

```python
model.eval()
prompt = "### 问题：\n请将以下句子翻译成英文。\n你好，欢迎来到北京。\n\n### 回答：\n"
inputs = tokenizer(prompt, return_tensors="pt").to("cuda")
with torch.no_grad():
    outputs = model.generate(**inputs, max_new_tokens=100)
print(tokenizer.decode(outputs[0], skip_special_tokens=True))
```

---

## 🏁 6. 总结

| 模块 | 内容 |
|------|------|
| 模型 | ChatGLM2-6B |
| 微调 | QLoRA（4bit量化 + LoRA） |
| 框架 | HuggingFace + DeepSpeed |
| 优势 | 显存需求低，支持中大型中文任务 |

---

需要我接着给出 **ZeRO Stage 3 + 多机多卡训练版本**，或支持 **wandb 监控 + PEFT 模型导出** 吗？