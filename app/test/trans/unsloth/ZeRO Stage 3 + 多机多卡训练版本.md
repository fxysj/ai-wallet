ZeRO Stage 3 + 多机多卡训练版本 
下面是基于 **ChatGLM2 + QLoRA + DeepSpeed ZeRO Stage 3 + 多机多卡训练** 的完整示例代码和配置。该版本适用于跨多台服务器进行大规模分布式训练，极大降低显存压力，并提升训练效率。

---

## 🧠 模型与训练方案

| 项目 | 内容 |
|------|------|
| 模型 | `ChatGLM2-6B`（中文预训练模型） |
| 微调 | `QLoRA`（LoRA + 4bit量化） |
| 框架 | HuggingFace Transformers + PEFT + DeepSpeed |
| 分布式方案 | ZeRO Stage 3 + 多机多卡 (`deepspeed --hostfile`) |

---

## 📁 目录结构建议

```bash
project/
├── ds_config_zero3.json           # ZeRO Stage 3 配置文件
├── train_chatglm2_zero3.py       # 启动训练脚本
├── data/
│   └── alpaca_zh.json            # 中文数据集
├── hostfile                      # 主机 IP 列表
```

---

## 📦 1. DeepSpeed 配置（`ds_config_zero3.json`）

```json
{
  "train_micro_batch_size_per_gpu": 1,
  "gradient_accumulation_steps": 8,
  "gradient_clipping": 1.0,
  "bf16": {
    "enabled": true
  },
  "zero_optimization": {
    "stage": 3,
    "offload_optimizer": {
      "device": "cpu",
      "pin_memory": true
    },
    "offload_param": {
      "device": "cpu",
      "pin_memory": true
    },
    "overlap_comm": true,
    "contiguous_gradients": true,
    "reduce_bucket_size": 5e7,
    "stage3_prefetch_bucket_size": 5e7,
    "stage3_param_persistence_threshold": 1e5
  },
  "activation_checkpointing": {
    "partition_activations": true,
    "contiguous_memory_optimization": true
  },
  "aio": {
    "block_size": 1048576,
    "queue_depth": 8,
    "single_submit": false,
    "overlap_events": true,
    "thread_count": 1
  }
}
```

---

## 🧑‍💻 2. Python 微调脚本（`train_chatglm2_zero3.py`）

（与之前版本大体一致，仅补充关键说明）

```python
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, TrainingArguments, Trainer, DataCollatorForSeq2Seq
from datasets import load_dataset
from peft import prepare_model_for_kbit_training, LoraConfig, get_peft_model

model_name = "THUDM/chatglm2-6b"
tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    load_in_4bit=True,
    device_map="auto",
    trust_remote_code=True
)

model = prepare_model_for_kbit_training(model)
lora_config = LoraConfig(
    r=8,
    lora_alpha=32,
    target_modules=["query_key_value"],
    lora_dropout=0.05,
    bias="none",
    task_type="CAUSAL_LM"
)
model = get_peft_model(model, lora_config)

dataset = load_dataset("json", data_files="data/alpaca_zh.json", split="train")

def preprocess(example):
    prompt = f"### 问题：\n{example['instruction']}\n{example['input']}\n\n### 回答：\n"
    inputs = tokenizer(prompt, truncation=True, padding="max_length", max_length=512)
    labels = tokenizer(example["output"], truncation=True, padding="max_length", max_length=512)
    inputs["labels"] = labels["input_ids"]
    return inputs

dataset = dataset.map(preprocess)

training_args = TrainingArguments(
    output_dir="output_zero3",
    per_device_train_batch_size=1,
    gradient_accumulation_steps=8,
    learning_rate=2e-4,
    num_train_epochs=3,
    bf16=True,
    logging_steps=10,
    save_strategy="epoch",
    deepspeed="ds_config_zero3.json",
    remove_unused_columns=False,
    report_to="none",
)

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

## 🌐 3. 主机文件（`hostfile`）

```text
worker-1 slots=4
worker-2 slots=4
```

其中 `worker-1` 和 `worker-2` 是两台机器的 hostname 或内网 IP，`slots=4` 表示每台机器使用 4 个 GPU。

---

## 🚀 4. 启动训练

```bash
deepspeed --hostfile hostfile train_chatglm2_zero3.py
```

你也可以指定节点数 + GPU 数运行：

```bash
deepspeed --num_nodes 2 --num_gpus 4 train_chatglm2_zero3.py
```

---

## ✅ 5. 优势总结

| 模块 | 优点 |
|------|------|
| ZeRO Stage 3 | 参数 & 优化器 &梯度均分布内存 |
| 多机多卡 | 跨服务器并行训练 |
| QLoRA | 显存极省 + 精度高 |
| ChatGLM2 | 中文能力优秀，适用于指令微调 |

---

如需支持 `wandb` 训练监控，`SFTTrainer` 精调器、或者自动保存 `LoRA adapter`，我也可以帮你一一补充。是否还想集成推理部署（如 FastAPI + model.generate）？