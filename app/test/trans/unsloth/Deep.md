好的！下面是一个 **基于 Unsloth + DeepSpeed + LLaMA3/ChatGLM2 + LoRA 的中文大模型微调完整示例**，支持在消费级 GPU 上进行低资源微调，具备以下优势：

- 使用 **Unsloth** 高效适配 LoRA / QLoRA
- 使用 **DeepSpeed ZeRO Stage 2/3** 实现内存优化
- 支持中文任务（情感分类、问答、摘要等）

---

## 🧩 一、环境准备

推荐 Python 3.10 + CUDA 11.8/12.1（支持 Ampere 或更新 GPU）

```bash
conda create -n unsloth_ds python=3.10 -y
conda activate unsloth_ds

pip install "unsloth[deepspeed] @ git+https://github.com/unslothai/unsloth.git"
pip install peft accelerate bitsandbytes deepspeed
```

---

## 🧠 二、加载 LLaMA3/ChatGLM2 模型 + Unsloth

> 下面以 LLaMA3-8B 为例（ChatGLM2 使用 HuggingFace 格式也可用）

```python
from unsloth import FastLanguageModel
import torch

model, tokenizer = FastLanguageModel.from_pretrained(
    model_name="unsloth/Meta-Llama-3.1-8B",  # 或 chatglm2-hf 版本
    max_seq_length=2048,
    dtype=torch.float16,
    load_in_4bit=True,  # QLoRA
)
```

---

## 🧰 三、LoRA 配置

```python
from peft import LoraConfig, get_peft_model, TaskType

lora_config = LoraConfig(
    task_type=TaskType.CAUSAL_LM,
    r=8,
    lora_alpha=32,
    lora_dropout=0.1,
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj"],
)

model = get_peft_model(model, lora_config)
```

---

## 📚 四、准备中文数据集（自定义格式）

格式如下（instruction tuning）：

```json
[
  {
    "instruction": "请将下面的句子翻译成英文：",
    "input": "你好，欢迎来到北京。",
    "output": "Hello, welcome to Beijing."
  }
]
```

加载和预处理：

```python
from datasets import load_dataset

dataset = load_dataset("json", data_files="data.json", split="train")

def preprocess(example):
    prompt = example["instruction"] + "\n" + example["input"]
    input_ids = tokenizer(prompt, truncation=True, padding="max_length", max_length=512)
    label_ids = tokenizer(example["output"], truncation=True, padding="max_length", max_length=512)["input_ids"]
    input_ids["labels"] = label_ids
    return input_ids

dataset = dataset.map(preprocess)
```

---

## ⚙️ 五、DeepSpeed 配置文件（保存为 `ds_config.json`）

```json
{
  "train_batch_size": 4,
  "gradient_accumulation_steps": 4,
  "optimizer": {
    "type": "AdamW",
    "params": {
      "lr": 2e-4,
      "betas": [0.9, 0.999],
      "eps": 1e-8,
      "weight_decay": 0.01
    }
  },
  "fp16": {
    "enabled": true
  },
  "zero_optimization": {
    "stage": 2,
    "offload_optimizer": {
      "device": "cpu"
    },
    "allgather_partitions": true,
    "allgather_bucket_size": 2e8,
    "overlap_comm": true,
    "reduce_scatter": true,
    "reduce_bucket_size": 2e8
  },
  "gradient_clipping": 1.0
}
```

---

## 🏋️ 六、启动微调训练

```python
from transformers import TrainingArguments, Trainer, DataCollatorForSeq2Seq

training_args = TrainingArguments(
    output_dir="./output_unsloth_deepspeed",
    per_device_train_batch_size=1,
    gradient_accumulation_steps=4,
    num_train_epochs=3,
    learning_rate=2e-4,
    fp16=True,
    logging_steps=10,
    save_strategy="epoch",
    remove_unused_columns=False,
    deepspeed="ds_config.json",  # 🧠 启用 DeepSpeed！
    report_to="none",  # 可选：wandb
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

## 💾 七、保存微调模型

```python
model.save_pretrained("output_unsloth_deepspeed")
tokenizer.save_pretrained("output_unsloth_deepspeed")
```

---

## ✅ 八、推理示例

```python
prompt = "请将下面的句子翻译成英文：\n你好，欢迎来到北京。"
inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
outputs = model.generate(**inputs, max_new_tokens=50)
print(tokenizer.decode(outputs[0], skip_special_tokens=True))
```

---

## 🔚 总结

| 模块       | 描述                                             |
|------------|--------------------------------------------------|
| `Unsloth`  | 高效适配 LLaMA3、LoRA，兼容 Transformers Trainer |
| `DeepSpeed`| 支持 ZeRO2/ZeRO3 分布式优化，节省显存提升吞吐    |
| 数据格式   | 支持 `instruction + input + output` 中文任务     |
| 支持模型   | LLaMA3、ChatGLM2、Qwen、Baichuan 等              |

---

需要我进一步提供：👉 ChatGLM2 + QLoRA + DeepSpeed 的完整代码，或 DeepSpeed ZeRO-3 多卡训练启动命令？