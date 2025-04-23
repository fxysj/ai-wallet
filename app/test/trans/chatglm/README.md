太好了，我们现在进入实战的中高级阶段：使用 **ChatGLM2-6B + LoRA 微调** 进行中文任务微调！

---

## 🚀 使用 ChatGLM2-6B + LoRA（PEFT）进行中文模型微调

### ✅ 应用场景：用较小资源微调大模型（如 ChatGLM2-6B），用于中文问答、摘要、情感分析等任务。

---

## 一、环境准备（pip 安装）

```bash
pip install transformers accelerate datasets peft bitsandbytes
```

---

## 二、完整代码示例（含注释）  
下面以 ChatGLM2-6B 模型微调中文问答任务为例，使用 `LoRA` 参数高效微调技术，仅调整小量参数。

### 📄 `finetune_chatglm2_lora.py`

```python
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
```

---

## 三、数据格式要求（`train.json` 示例）

```json
[
  {
    "instruction": "请对下列句子进行情感分析：",
    "input": "这家餐厅的菜又贵又难吃。",
    "output": "负面"
  },
  {
    "instruction": "请总结以下内容的要点：",
    "input": "苹果公司发布了新一代MacBook Pro，采用M3芯片...",
    "output": "苹果发布新MacBook Pro，搭载M3芯片"
  }
]
```

---

## 四、说明

| 部分                 | 作用 |
|----------------------|------|
| `LoRA`               | 仅微调部分模块的低秩子空间，参数量下降 95%+，训练效率大幅提升 |
| `ChatGLM2-6B`        | THUDM 开源的大模型，支持中英对话任务、问答任务 |
| `peft.get_peft_model`| 用于注入低秩适配器（LoRA）到目标模块 |
| `Trainer`            | HuggingFace 封装的训练器，简化训练流程 |

---

## 🧠 推荐实践

- ✅ 使用你的中文私有语料数据集
- ✅ 开启 `deepspeed` or `fsdp` 进一步降低显存
- ✅ 使用 wandb or TensorBoard 监控指标

---

如果你想继续我可以为你拓展：

✅ 加入 DeepSpeed/FSDP + PEFT  
✅ 多 GPU 执行配置  
✅ 使用 ChatGLM3 / Baichuan2 / LLaMA3 中文微调版本  
✅ 实现推理 API、量化保存模型  

需要我继续完善这些内容吗？你想微调哪个具体模型/任务也可以直接说 😎