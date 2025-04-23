以下是完整的 **ChatGLM3 + QLoRA + WandB** 精调示例代码，已补充详细注释，帮助你理解每一步的作用：

---

## ✅ 训练流程概览：

| 步骤 | 内容 |
|------|------|
| ✅ 模型加载 | 使用 ChatGLM3 + 4bit QLoRA |
| ✅ 数据准备 | 中文指令数据（支持 Alpaca 格式） |
| ✅ 微调框架 | 🤗 Transformers + PEFT + TRL 的 `SFTTrainer` |
| ✅ 日志监控 | 支持 WandB |

---

## ✅ 完整代码（含注释）：

```python
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig, TrainingArguments
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from datasets import load_dataset
from trl import SFTTrainer
import torch
import wandb

# === Step 1: 模型和量化配置 ===
model_name = "THUDM/chatglm3-6b"

bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,  # 使用 4bit 量化
    bnb_4bit_use_double_quant=True,
    bnb_4bit_quant_type="nf4",  # 精度更高的非对称量化
    bnb_4bit_compute_dtype=torch.bfloat16  # 使用 bfloat16 提升性能
)

model = AutoModelForCausalLM.from_pretrained(
    model_name,
    quantization_config=bnb_config,
    device_map="auto",
    trust_remote_code=True
)

tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
tokenizer.pad_token = tokenizer.eos_token  # 设置 pad_token 防止 padding 报错

# === Step 2: 应用 QLoRA 配置 ===
model = prepare_model_for_kbit_training(model)

lora_config = LoraConfig(
    r=8,
    lora_alpha=32,
    target_modules=["query_key_value"],  # ChatGLM3 关键模块
    lora_dropout=0.05,
    bias="none",
    task_type="CAUSAL_LM"
)

model = get_peft_model(model, lora_config)

# === Step 3: 中文数据集加载与处理 ===
dataset = load_dataset("json", data_files={
    "train": "data/train.json",
    "validation": "data/val.json"
})

def preprocess(example):
    prompt = f"### 指令：\n{example['instruction']}\n{example['input']}\n\n### 回答：\n"
    inputs = tokenizer(prompt, truncation=True, padding="max_length", max_length=512)
    labels = tokenizer(example["output"], truncation=True, padding="max_length", max_length=512)
    inputs["labels"] = labels["input_ids"]
    return inputs

train_dataset = dataset["train"].map(preprocess, remove_columns=dataset["train"].column_names)
eval_dataset = dataset["validation"].map(preprocess, remove_columns=dataset["validation"].column_names)

# === Step 4: WandB 日志 & 训练参数 ===
wandb.init(project="chatglm3-qlora", name="qlora-sft-run")

training_args = TrainingArguments(
    output_dir="output_sft",
    per_device_train_batch_size=1,
    gradient_accumulation_steps=8,
    num_train_epochs=3,
    learning_rate=2e-4,
    logging_steps=10,
    bf16=True,
    save_strategy="epoch",
    evaluation_strategy="epoch",
    report_to="wandb",
    run_name="chatglm3-qlora-sft"
)

# === Step 5: 启动训练 ===
trainer = SFTTrainer(
    model=model,
    tokenizer=tokenizer,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=eval_dataset
)

trainer.train()
```

---

## 📊 训练监控（WandB 图表说明）：

在 WandB Dashboard 中你会看到如下图表：

| 图表名称 | 含义 |
|----------|------|
| `train_loss` | 每步或每 epoch 的训练损失曲线 |
| `eval_loss` | 每个验证周期的损失值 |
| `lr` | 学习率调度（如使用 warmup 时） |
| `grad_norm` | 梯度范数，有助于观察梯度爆炸或消失 |

---

如你需要继续完成：
- ✅ `merge_and_unload()` 合并权重导出完整模型
- ✅ 使用 ChatGLM3 推理脚本
- ✅ SFTTrainer 支持持续训练与断点恢复

我也可以继续帮你加上，告诉我你的下一个目标即可！

下面是你提出的三大目标的完整实现代码，并配有中文注释，适用于使用 QLoRA 微调的 ChatGLM3 模型：

---

# ✅ 1. 合并权重并导出完整模型（merge_and_unload）

```python
from peft import PeftModel

# 加载训练后的 LoRA 模型
peft_model = PeftModel.from_pretrained(
    model,
    "output_sft",  # 你保存 LoRA adapter 的路径
)

# 合并 LoRA adapter 权重到 base model
peft_model = peft_model.merge_and_unload()

# 保存合并后的完整模型，适用于部署
peft_model.save_pretrained("merged_chatglm3_model")
tokenizer.save_pretrained("merged_chatglm3_model")

print("✅ 合并并保存完整模型完成！")
```

---

# ✅ 2. 推理脚本（使用 ChatGLM3 + 合并后的权重）

```python
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

# 加载合并后的模型和 tokenizer
model = AutoModelForCausalLM.from_pretrained(
    "merged_chatglm3_model",
    device_map="auto",
    trust_remote_code=True
).eval()

tokenizer = AutoTokenizer.from_pretrained("merged_chatglm3_model", trust_remote_code=True)

# 推理输入
instruction = "请写一首七言绝句，主题是春天。"
input_text = f"### 指令：\n{instruction}\n\n### 回答：\n"

inputs = tokenizer(input_text, return_tensors="pt").to(model.device)

# 推理
with torch.no_grad():
    outputs = model.generate(
        **inputs,
        max_new_tokens=128,
        do_sample=True,
        temperature=0.95,
        top_p=0.9
    )
    result = tokenizer.decode(outputs[0], skip_special_tokens=True)

# 输出结果
print("📜 模型生成结果：")
print(result)
```

---

# ✅ 3. 支持断点恢复与持续训练（SFTTrainer）

更新 `TrainingArguments`：

```python
from transformers import TrainingArguments

training_args = TrainingArguments(
    output_dir="output_sft",        # 模型输出目录
    save_total_limit=3,             # 最多保留的 checkpoint 数量
    per_device_train_batch_size=1,
    gradient_accumulation_steps=8,
    num_train_epochs=5,
    learning_rate=2e-4,
    logging_steps=10,
    bf16=True,
    save_strategy="epoch",
    evaluation_strategy="epoch",
    report_to="wandb",
    run_name="chatglm3-qlora-sft",
    load_best_model_at_end=True,   # 训练结束后加载最优模型
    resume_from_checkpoint=True    # 支持断点恢复
)
```

使用 `resume_from_checkpoint=True` 后，如果上一次训练中断，重新运行 `trainer.train()` 时会自动恢复。

完整训练调用方式：

```python
trainer = SFTTrainer(
    model=model,
    tokenizer=tokenizer,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=eval_dataset,
)

trainer.train()  # 将自动从 checkpoint 恢复（如果存在）
```

---

✅ **小结：**

| 功能 | 实现方式 |
|------|----------|
| 模型权重合并 | `merge_and_unload()` 后保存 |
| 模型推理 | 使用 `generate()` 生成文本 |
| 持续训练与断点恢复 | `resume_from_checkpoint=True` |

如你还想添加：
- INT4 导出 ONNX 加速推理  
- ChatGLM3 多轮对话结构优化  
- Streamlit 或 FastAPI 封装推理服务  

我也可以一并帮你集成～只管说！


太好了，我们现在将「ChatGLM3 多轮对话」封装为 **FastAPI 接口服务**，支持：

- ✅ 多轮对话（上下文记忆）
- ✅ 多用户支持（通过 `user_id` 进行会话隔离）
- ✅ 可部署的推理接口

---

## ✅ 项目结构

```
chatglm3_api/
├── app.py             ← FastAPI 主应用入口
├── model_utils.py     ← 模型加载 & 多轮对话封装
├── history_store.py   ← 用户多轮上下文历史管理
└── requirements.txt
```

---

## ✅ 1. `model_utils.py`：模型加载与推理封装

```python
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

# 加载模型和分词器
model_path = "merged_chatglm3_model"
tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)
model = AutoModelForCausalLM.from_pretrained(model_path, trust_remote_code=True, device_map="auto").eval()

def build_prompt(history):
    """将多轮 history 构建为 prompt 字符串"""
    prompt = ""
    for turn in history:
        if turn["role"] == "user":
            prompt += f"<|user|>\n{turn['content']}\n"
        elif turn["role"] == "assistant":
            prompt += f"<|assistant|>\n{turn['content']}\n"
    prompt += "<|assistant|>\n"
    return prompt

def chatglm_infer(history):
    """根据历史对话推理模型的回复"""
    prompt = build_prompt(history)
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)

    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=256,
            do_sample=True,
            top_p=0.9,
            temperature=0.8,
            pad_token_id=tokenizer.eos_token_id
        )

    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    reply = response.split("<|assistant|>\n")[-1].strip()
    return reply
```

---

## ✅ 2. `history_store.py`：会话历史存储（支持多用户）

```python
from collections import defaultdict

# 内存中的用户历史存储
history_dict = defaultdict(list)

def get_user_history(user_id: str):
    return history_dict[user_id]

def append_user_message(user_id: str, role: str, content: str):
    history_dict[user_id].append({"role": role, "content": content})

def clear_user_history(user_id: str):
    history_dict[user_id] = []
```

---

## ✅ 3. `app.py`：FastAPI 服务主程序

```python
from fastapi import FastAPI, Request
from pydantic import BaseModel
from history_store import get_user_history, append_user_message, clear_user_history
from model_utils import chatglm_infer
import uvicorn

app = FastAPI()

class ChatRequest(BaseModel):
    user_id: str
    message: str
    reset: bool = False  # 可选参数：重置会话

@app.post("/chat")
def chat_endpoint(req: ChatRequest):
    if req.reset:
        clear_user_history(req.user_id)
        return {"reply": "✅ 对话已重置"}

    # 添加用户消息
    append_user_message(req.user_id, "user", req.message)

    # 获取回复
    history = get_user_history(req.user_id)
    reply = chatglm_infer(history)

    # 添加机器人回复
    append_user_message(req.user_id, "assistant", reply)

    return {"reply": reply}
```

---

## ✅ 4. `requirements.txt`

```text
fastapi
uvicorn
transformers
torch
```

---

## ✅ 5. 启动服务

```bash
pip install -r requirements.txt
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

---

## ✅ 示例调用（使用 curl 或 Postman）

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"user_id": "user123", "message": "你好"}'
```

---

## ✅ 接下来还能干啥？

- ✅ 增加 `max_history_turns` 限制长度防止OOM
- ✅ 持久化存储 history（用 Redis / SQLite）
- ✅ 使用前端（Streamlit 或 Vue）搭建聊天UI
- ✅ 支持异步 WebSocket 实时返回

---

需要我帮你接 WebSocket 聊天或嵌入前端 UI 吗？🧠😎


非常实用的优化！在使用 ChatGLM3 多轮对话时，如果历史对话太长，会导致：

内存（显存）占用过大

推理速度变慢

模型生成质量下降（重要信息被截断）

我们可以在 get_user_history 中增加一个参数 max_history_turns，用于控制每次输入模型的历史轮数。

✅ 修改后的 model_utils.py

def build_prompt(history, max_turns=5):
    """
    将历史构造成 prompt 字符串，最多保留最近的 max_turns 轮。
    一轮 = 一问一答（user+assistant）
    """
    recent_history = history[-max_turns * 2:]  # 每轮包含 user 和 assistant
    prompt = ""
    for turn in recent_history:
        if turn["role"] == "user":
            prompt += f"<|user|>\n{turn['content']}\n"
        elif turn["role"] == "assistant":
            prompt += f"<|assistant|>\n{turn['content']}\n"
    prompt += "<|assistant|>\n"
    return prompt

def chatglm_infer(history, max_turns=5):
    """封装推理流程，限制最多保留 max_turns 轮上下文"""
    prompt = build_prompt(history, max_turns=max_turns)
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)

    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=256,
            do_sample=True,
            top_p=0.9,
            temperature=0.8,
            pad_token_id=tokenizer.eos_token_id
        )

    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    reply = response.split("<|assistant|>\n")[-1].strip()
    return reply
✅ 修改 app.py 以传入轮数限制

@app.post("/chat")
def chat_endpoint(req: ChatRequest):
    if req.reset:
        clear_user_history(req.user_id)
        return {"reply": "✅ 对话已重置"}

    append_user_message(req.user_id, "user", req.message)

    history = get_user_history(req.user_id)

    # 控制上下文轮数，防止输入过长 OOM
    reply = chatglm_infer(history, max_turns=5)

    append_user_message(req.user_id, "assistant", reply)
    return {"reply": reply}
✅ 效果
会话仍然保留全部历史在内存中（用于持久化等）

每次推理仅使用最近 max_turns 轮历史上下文（默认 5）

降低显存开销 & 防止 OOM & 提升稳定性 ✅


好的，我们可以使用 Redis 来持久化多轮对话历史，确保服务重启后仍能恢复用户上下文，同时也便于横向扩展（多机部署时共享用户状态）。

下面是完整的封装方案（使用 `redis-py`）：

---

## ✅ 1. 安装依赖

```bash
pip install redis
```

---

## ✅ 2. 设计 Redis 存储结构

我们为每个用户使用一个 Redis 键，例如：

```
chat_history:{user_id} => List（JSON序列化的消息对象）
```

---

## ✅ 3. 封装历史管理模块（`history_store.py`）

```python
import redis
import json

# 连接 Redis（默认本地）
r = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)

HISTORY_PREFIX = "chat_history"

def _get_key(user_id):
    return f"{HISTORY_PREFIX}:{user_id}"

def append_user_message(user_id, role, content):
    msg = {"role": role, "content": content}
    r.rpush(_get_key(user_id), json.dumps(msg))

def get_user_history(user_id) -> list:
    raw_list = r.lrange(_get_key(user_id), 0, -1)
    return [json.loads(item) for item in raw_list]

def clear_user_history(user_id):
    r.delete(_get_key(user_id))

def trim_user_history(user_id, max_messages=10):
    """
    可选：保留最近 max_messages 条历史（每条为 user 或 assistant 的消息）
    """
    r.ltrim(_get_key(user_id), -max_messages, -1)
```

---

## ✅ 4. 在 `FastAPI` 中使用 Redis 历史模块

```python
from fastapi import FastAPI
from pydantic import BaseModel
from history_store import (
    append_user_message, get_user_history, clear_user_history, trim_user_history
)
from model_utils import chatglm_infer

app = FastAPI()

class ChatRequest(BaseModel):
    user_id: str
    message: str
    reset: bool = False

@app.post("/chat")
def chat(req: ChatRequest):
    if req.reset:
        clear_user_history(req.user_id)
        return {"reply": "✅ 对话历史已清空"}

    append_user_message(req.user_id, "user", req.message)

    history = get_user_history(req.user_id)

    reply = chatglm_infer(history, max_turns=5)

    append_user_message(req.user_id, "assistant", reply)

    # 可选：限制 Redis 存储长度
    trim_user_history(req.user_id, max_messages=10)

    return {"reply": reply}
```

---

## ✅ 5. 推理优化（参考 ChatGLM3 多轮对话格式）

结合之前的 `build_prompt(history)` 函数，将 `history` 限制为最近若干轮（例如 5 轮），可避免 OOM。

---

## ✅ Bonus：支持 Redis Cluster / 云托管（如阿里云 Redis）

```python
# 使用 URL 连接 Redis 云服务
r = redis.from_url("redis://:password@your-redis-host:6379/0", decode_responses=True)
```

---

需要我帮你接入缓存过期时间（如历史自动清除）、用户身份验证、WebSocket 多轮对话接口？或者再进一步支持 **多语言多用户并发场景**？🚀



很好，接入 Redis 的 **缓存过期时间机制** 可以帮助我们：

- ✅ 自动清除过期对话，防止 Redis 占用内存过多  
- ✅ 实现“短期记忆”对话系统，例如：只记 30 分钟内的历史  
- ✅ 实现 Session 式记忆逻辑（超时则清除）

---

## ✅ 修改 Redis 存储结构：设置键过期时间

我们在每次写入对话历史时，通过 `expire()` 或 `rpush(..., ex=TTL)` 设置过期时间（单位：秒）

---

## ✅ 代码更新：`history_store.py`

```python
import redis
import json

# Redis 连接
r = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)

HISTORY_PREFIX = "chat_history"
DEFAULT_TTL_SECONDS = 30 * 60  # 30分钟

def _get_key(user_id):
    return f"{HISTORY_PREFIX}:{user_id}"

def append_user_message(user_id, role, content, ttl=DEFAULT_TTL_SECONDS):
    msg = {"role": role, "content": content}
    key = _get_key(user_id)
    r.rpush(key, json.dumps(msg))
    # 每次更新都刷新 TTL
    r.expire(key, ttl)

def get_user_history(user_id) -> list:
    raw_list = r.lrange(_get_key(user_id), 0, -1)
    return [json.loads(item) for item in raw_list]

def clear_user_history(user_id):
    r.delete(_get_key(user_id))

def trim_user_history(user_id, max_messages=10):
    r.ltrim(_get_key(user_id), -max_messages, -1)
```

---

## ✅ 在 FastAPI 中使用（不变，但历史会自动过期）

```python
append_user_message(req.user_id, "user", req.message)

history = get_user_history(req.user_id)

reply = chatglm_infer(history, max_turns=5)

append_user_message(req.user_id, "assistant", reply)

trim_user_history(req.user_id, max_messages=10)
```

---

## ✅ Bonus：设置不同 TTL 逻辑（可按用户/场景自定义）

```python
def get_user_ttl(user_id):
    if user_id.startswith("vip"):
        return 3600  # VIP 用户保留 1 小时
    return DEFAULT_TTL_SECONDS
```

然后 `append_user_message(req.user_id, ..., ttl=get_user_ttl(req.user_id))`。

---

是否还想支持「对话 session id」、「持久历史文件备份」、「设置自动清除历史的定时任务」等？我可以一并帮你实现。


太好了，咱们一步步来，把你提到的三个功能 **全部支持上**：

---

## ✅ 1. 支持「对话 session id」

### ✅ 目的：
- 支持一个用户同时开启多个对话（类似 ChatGPT 左侧会话列表）
- 每次对话独立存储，不混淆上下文

### ✅ 结构设计：

Redis 的键变为：

```
chat_history:{user_id}:{session_id}
```

### ✅ 修改代码：

```python
def _get_key(user_id, session_id):
    return f"{HISTORY_PREFIX}:{user_id}:{session_id}"

def append_user_message(user_id, session_id, role, content, ttl=DEFAULT_TTL_SECONDS):
    msg = {"role": role, "content": content}
    key = _get_key(user_id, session_id)
    r.rpush(key, json.dumps(msg))
    r.expire(key, ttl)

def get_user_history(user_id, session_id) -> list:
    key = _get_key(user_id, session_id)
    raw_list = r.lrange(key, 0, -1)
    return [json.loads(item) for item in raw_list]

def clear_user_history(user_id, session_id):
    r.delete(_get_key(user_id, session_id))
```

在 API 中，每次请求带上 `session_id` 即可。

---

## ✅ 2. 支持「持久历史文件备份」

### ✅ 背景：
- Redis 是内存数据库，历史随时可能因 OOM 或重启丢失
- 可以定期持久化到本地 JSON 文件做备份

### ✅ Python 定时备份脚本示例（可挂 crontab 或 APScheduler）：

```python
import redis
import json
from datetime import datetime

r = redis.Redis(host="localhost", port=6379, decode_responses=True)
HISTORY_PREFIX = "chat_history"

def backup_all_histories():
    keys = r.keys(f"{HISTORY_PREFIX}:*")
    data = {}
    for key in keys:
        history = r.lrange(key, 0, -1)
        data[key] = [json.loads(msg) for msg in history]

    with open(f"backup_chat_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    backup_all_histories()
```

---

## ✅ 3. 支持「自动清除历史定时任务」

### ✅ Redis 自带 TTL，不需你主动删除，但你可以用定时脚本「彻底清理已失效的历史备份或超期会话」

如果你还希望清除长期 inactive 的 Redis 键、日志备份，可以设置如下 cron：

### ✅ 示例 crontab：

```bash
# 每天 3 点备份一次 Redis 聊天记录
0 3 * * * /usr/bin/python3 /path/to/backup_script.py

# 每 7 天清理一次本地备份（保留最近5个）
0 4 */7 * * find /path/to/backups -name '*.json' | sort | head -n -5 | xargs rm -f
```

---

## ✅ 如果你用的是 FastAPI + uvicorn：

你可以使用 `APScheduler` 内部定时任务：

```python
from apscheduler.schedulers.background import BackgroundScheduler

scheduler = BackgroundScheduler()
scheduler.add_job(backup_all_histories, 'cron', hour=3, minute=0)
scheduler.start()
```

---

需要我帮你封装成 FastAPI 全功能对话服务示例（带 session、持久化、恢复能力、最大上下文控制）吗？我可以给你一整套完整模板。


好的！下面是一个 **基于 ChatGLM3 的 FastAPI 对话服务完整模板**，支持：

---

### ✅ 功能特性：

1. **多轮对话管理（session_id）**
2. **Redis 记录历史 + 过期自动清除（TTL）**
3. **最大轮数控制（max_history_turns）防止 OOM**
4. **自动备份对话记录（持久化恢复）**
5. **接口支持断点恢复（restart after crash）**

---

## 📦 依赖安装（推荐虚拟环境）

```bash
pip install fastapi uvicorn redis transformers apscheduler
```

---

## 🧠 项目结构：

```
chat_api/
├── main.py                # FastAPI 主程序
├── history.py             # 历史记录封装（Redis + TTL）
├── backup.py              # 备份逻辑
├── model.py               # 加载 ChatGLM3 模型
└── config.py              # 配置
```

---

### 🧩 config.py

```python
REDIS_HOST = "localhost"
REDIS_PORT = 6379
REDIS_DB = 0

HISTORY_PREFIX = "chat_history"
DEFAULT_TTL_SECONDS = 3600  # 1 小时
MAX_HISTORY_TURNS = 10
```

---

### 🧩 history.py

```python
import redis
import json
from config import *

r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, decode_responses=True)

def _get_key(user_id, session_id):
    return f"{HISTORY_PREFIX}:{user_id}:{session_id}"

def append_message(user_id, session_id, role, content):
    msg = {"role": role, "content": content}
    key = _get_key(user_id, session_id)
    r.rpush(key, json.dumps(msg))
    r.expire(key, DEFAULT_TTL_SECONDS)

    # 控制最多 max_turns 条
    if r.llen(key) > MAX_HISTORY_TURNS * 2:
        r.lpop(key)
        r.lpop(key)

def get_history(user_id, session_id):
    key = _get_key(user_id, session_id)
    raw = r.lrange(key, 0, -1)
    return [json.loads(msg) for msg in raw]

def clear_history(user_id, session_id):
    r.delete(_get_key(user_id, session_id))
```

---

### 🧩 model.py

```python
from transformers import AutoTokenizer, AutoModel
import torch

model_name = "THUDM/chatglm3-6b"  # 替换为你的模型
tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
model = AutoModel.from_pretrained(model_name, trust_remote_code=True).cuda().eval()

def chat_with_history(history, query):
    messages = history + [{"role": "user", "content": query}]
    response, _ = model.chat(tokenizer, messages)
    return response
```

---

### 🧩 backup.py

```python
import json
from datetime import datetime
from config import *
from history import r

def backup_all_histories():
    keys = r.keys(f"{HISTORY_PREFIX}:*")
    data = {}

    for key in keys:
        messages = r.lrange(key, 0, -1)
        data[key] = [json.loads(m) for m in messages]

    with open(f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
```

---

### 🚀 main.py （FastAPI 主程序）

```python
from fastapi import FastAPI, Request
from pydantic import BaseModel
from history import append_message, get_history, clear_history
from model import chat_with_history
from backup import backup_all_histories
from apscheduler.schedulers.background import BackgroundScheduler

app = FastAPI()

# 定时备份
scheduler = BackgroundScheduler()
scheduler.add_job(backup_all_histories, "cron", hour=3)
scheduler.start()

class ChatRequest(BaseModel):
    user_id: str
    session_id: str
    query: str

@app.post("/chat")
async def chat(req: ChatRequest):
    history = get_history(req.user_id, req.session_id)
    response = chat_with_history(history, req.query)

    # 更新历史
    append_message(req.user_id, req.session_id, "user", req.query)
    append_message(req.user_id, req.session_id, "assistant", response)

    return {"response": response}

@app.get("/clear")
def clear(user_id: str, session_id: str):
    clear_history(user_id, session_id)
    return {"message": "history cleared"}

@app.get("/backup")
def backup():
    backup_all_histories()
    return {"message": "backup done"}
```

---

## 🧪 启动服务：

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

---

## 🛠 请求示例：

```json
POST /chat
{
  "user_id": "user123",
  "session_id": "sessionABC",
  "query": "你好，ChatGLM3！"
}
```

---

## 🎯 后续可加功能：

- ✅ WebSocket 实时回复
- ✅ 加入 wandb 日志追踪
- ✅ 接入前端页面（Gradio / Vue）
- ✅ 支持用户上下文记忆存入 MySQL
- ✅ 微调 ChatGLM3 并部署微调版本

---

如果你想，我可以继续帮你加上 WebSocket 支持、前端页面、微调 ChatGLM3 并部署的代码模板，是否继续？


好的！以下是如何为你的 **FastAPI** 聊天服务集成 **WebSocket 实时回复** 的完整示例。

### 🧩 功能实现：

- **WebSocket 支持**：允许客户端实时接收消息。
- **支持 ChatGLM3 模型**：通过 WebSocket 连接时，聊天内容会实时返回，并且在 Redis 中持久化历史记录。

---

### 🔧 项目结构（增加 WebSocket 支持）

```
chat_api/
├── main.py                # FastAPI 主程序
├── history.py             # 历史记录封装（Redis + TTL）
├── backup.py              # 备份逻辑
├── model.py               # 加载 ChatGLM3 模型
├── config.py              # 配置
└── websocket.py           # WebSocket 相关封装
```

---

### 🧩 websocket.py

```python
import redis
import json
from fastapi import WebSocket
from config import *
from history import append_message, get_history

r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, decode_responses=True)

def _get_key(user_id, session_id):
    return f"{HISTORY_PREFIX}:{user_id}:{session_id}"

async def chat_with_history_and_send(websocket: WebSocket, user_id: str, session_id: str, query: str):
    # 获取当前对话历史
    history = get_history(user_id, session_id)

    # 模型推理
    from model import chat_with_history  # 动态导入模型，以便管理依赖
    response = chat_with_history(history, query)

    # 将用户消息和模型回复保存到历史记录中
    append_message(user_id, session_id, "user", query)
    append_message(user_id, session_id, "assistant", response)

    # 发送实时消息
    await websocket.send_text(response)
```

---

### 🧩 main.py（集成 WebSocket）

```python
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from websocket import chat_with_history_and_send
from apscheduler.schedulers.background import BackgroundScheduler
from backup import backup_all_histories
from history import append_message, get_history

app = FastAPI()

# 定时备份
scheduler = BackgroundScheduler()
scheduler.add_job(backup_all_histories, "cron", hour=3)
scheduler.start()

class ChatRequest(BaseModel):
    user_id: str
    session_id: str
    query: str

@app.websocket("/ws/chat/{user_id}/{session_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str, session_id: str):
    await websocket.accept()
    try:
        while True:
            # 等待接收用户的消息
            data = await websocket.receive_text()
            # 实时回复用户
            await chat_with_history_and_send(websocket, user_id, session_id, data)
    except WebSocketDisconnect:
        print(f"Client {user_id} disconnected")

@app.post("/chat")
async def chat(req: ChatRequest):
    history = get_history(req.user_id, req.session_id)
    from model import chat_with_history  # 动态导入模型
    response = chat_with_history(history, req.query)

    # 更新历史
    append_message(req.user_id, req.session_id, "user", req.query)
    append_message(req.user_id, req.session_id, "assistant", response)

    return {"response": response}

@app.get("/clear")
def clear(user_id: str, session_id: str):
    clear_history(user_id, session_id)
    return {"message": "history cleared"}

@app.get("/backup")
def backup():
    backup_all_histories()
    return {"message": "backup done"}
```

---

### 🧩 运行 FastAPI 服务：

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

---

### 🧪 使用 WebSocket 进行聊天：

1. **客户端**可以通过 **WebSocket** 连接到 `/ws/chat/{user_id}/{session_id}` 地址，进行实时聊天。
2. 每当用户发送消息时，系统会通过模型生成响应并实时返回。

#### WebSocket 客户端示例（Python）：

```python
import asyncio
import websockets

async def chat():
    uri = "ws://localhost:8000/ws/chat/user123/sessionABC"  # 这里替换为用户和会话ID
    async with websockets.connect(uri) as websocket:
        await websocket.send("你好，ChatGLM3！")  # 发送消息
        response = await websocket.recv()  # 接收消息
        print(f"ChatGLM3 回复：{response}")

# 运行聊天
asyncio.get_event_loop().run_until_complete(chat())
```

---

#### WebSocket 客户端示例（JavaScript）：

```javascript
const socket = new WebSocket("ws://localhost:8000/ws/chat/user123/sessionABC");

socket.onopen = function(event) {
  console.log("WebSocket连接已打开");
  socket.send("你好，ChatGLM3！");
};

socket.onmessage = function(event) {
  console.log("ChatGLM3 回复：", event.data);
};

socket.onclose = function(event) {
  console.log("WebSocket连接已关闭");
};

socket.onerror = function(event) {
  console.log("WebSocket发生错误");
};
```

---

### 🎯 后续扩展：

- **前端实时聊天页面**：使用 Vue 或 React 配合 WebSocket 实现实时聊天界面。
- **WebSocket 客户端和服务器双向推送**：实现更加丰富的实时交互功能。
- **连接 Redis 缓存和消息队列**：让多个 WebSocket 客户端共享对话历史。
- **结合浏览器通知**：在前端集成浏览器通知推送，增强用户体验。

---

这样，你就能实现一个 **支持实时推理和 WebSocket 的 ChatGLM3** 聊天服务！如果你需要进一步优化，或者有其他功能需求，随时告诉我！


要在 **FastAPI** WebSocket 实时聊天服务中集成 **WandB** 日志追踪，我们可以使用 `wandb` 库来记录训练和推理过程中的相关指标，如输入、输出、推理时间等。

以下是如何将 **WandB** 集成到你的 **FastAPI + WebSocket** 聊天服务中，进行实时日志追踪和监控的完整代码示例。

### 1. 安装依赖

首先，安装 `wandb` 和其他依赖：

```bash
pip install wandb fastapi uvicorn redis apscheduler
```

### 2. 配置 WandB

在代码中，你需要初始化 **WandB** 项目并记录相关信息。以下是相关配置和集成的步骤：

### 🧩 `websocket.py` — 集成 WandB 日志追踪

```python
import redis
import json
import wandb
from fastapi import WebSocket
from config import *
from history import append_message, get_history

r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, decode_responses=True)

# 初始化WandB项目
wandb.init(project="chatglm3-chat-service", entity="your-wandb-username")

def _get_key(user_id, session_id):
    return f"{HISTORY_PREFIX}:{user_id}:{session_id}"

async def chat_with_history_and_send(websocket: WebSocket, user_id: str, session_id: str, query: str):
    # 获取当前对话历史
    history = get_history(user_id, session_id)

    # 模型推理
    from model import chat_with_history  # 动态导入模型，以便管理依赖
    response = chat_with_history(history, query)

    # 将用户消息和模型回复保存到历史记录中
    append_message(user_id, session_id, "user", query)
    append_message(user_id, session_id, "assistant", response)

    # 记录WandB日志：用户输入、系统响应、会话历史
    wandb.log({
        "user_input": query,
        "system_response": response,
        "session_id": session_id,
        "user_id": user_id,
        "turn_count": len(history),  # 历史消息轮次
    })

    # 发送实时消息
    await websocket.send_text(response)
```

### 🧩 `main.py` — WebSocket 和 POST 请求集成 WandB

```python
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from websocket import chat_with_history_and_send
from apscheduler.schedulers.background import BackgroundScheduler
from backup import backup_all_histories
from history import append_message, get_history
import wandb

app = FastAPI()

# 初始化WandB项目
wandb.init(project="chatglm3-chat-service", entity="your-wandb-username")

# 定时备份
scheduler = BackgroundScheduler()
scheduler.add_job(backup_all_histories, "cron", hour=3)
scheduler.start()

class ChatRequest(BaseModel):
    user_id: str
    session_id: str
    query: str

@app.websocket("/ws/chat/{user_id}/{session_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str, session_id: str):
    await websocket.accept()
    try:
        while True:
            # 等待接收用户的消息
            data = await websocket.receive_text()
            # 实时回复用户
            await chat_with_history_and_send(websocket, user_id, session_id, data)
    except WebSocketDisconnect:
        print(f"Client {user_id} disconnected")

@app.post("/chat")
async def chat(req: ChatRequest):
    history = get_history(req.user_id, req.session_id)
    from model import chat_with_history  # 动态导入模型
    response = chat_with_history(history, req.query)

    # 更新历史
    append_message(req.user_id, req.session_id, "user", req.query)
    append_message(req.user_id, req.session_id, "assistant", response)

    # 记录WandB日志：用户输入、系统响应
    wandb.log({
        "user_input": req.query,
        "system_response": response,
        "session_id": req.session_id,
        "user_id": req.user_id,
        "turn_count": len(history),
    })

    return {"response": response}

@app.get("/clear")
def clear(user_id: str, session_id: str):
    clear_history(user_id, session_id)
    return {"message": "history cleared"}

@app.get("/backup")
def backup():
    backup_all_histories()
    return {"message": "backup done"}
```

### 🧩 配置 WandB

1. **初始化 WandB**：
   - 在代码中初始化 `wandb.init()` 来开始记录日志。
   - 确保在 `wandb.init()` 中提供 `project` 和 `entity` 参数，分别表示项目名称和你的 WandB 用户名。
   
2. **日志记录**：
   - 在推理过程中，通过 `wandb.log()` 将关键数据（如用户输入、系统响应、会话历史等）记录下来。
   - `wandb.log()` 是用来记录每一步的日志数据，可以记录文本、数字、图像等多种类型的数据。

3. **监控模型**：
   - 通过在每次推理时记录输入、输出、对话轮次等信息，可以在 **WandB Dashboard** 上实时监控模型的性能。
   - 例如：观察不同输入的响应时间、历史对话长度与模型生成的响应质量。

### 🧩 使用 WandB 监控训练

- **监控图表**：你可以在 **WandB Dashboard** 中看到每次记录的图表，包括：
  - 用户输入的分布情况
  - 模型生成的响应分布
  - 其他指标（如会话轮次）

---

### 🧪 启动 FastAPI 服务并启用 WandB 监控

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

### 📊 WandB Dashboard 查看

- 登陆 [WandB](https://wandb.ai/) 后，可以进入 **项目页面**，查看日志信息并创建图表。
- 你将能够看到日志中的 **用户输入** 和 **系统响应**，并能够通过图表分析模型行为。

---

### 结语

通过集成 **WandB**，你可以实时监控 FastAPI 服务中每次推理的输入、输出以及模型的状态，从而有助于调优和改进模型的表现。



微调 ChatGLM3 并将其部署为一个可供实时使用的服务是一个复杂的流程。这里，我们将逐步完成以下任务：

1. **微调 ChatGLM3**：首先，我们将使用 LoRA（Low-Rank Adaptation）微调 ChatGLM3，以便在有限的计算资源上有效调整其性能。
2. **部署微调版本**：在微调完成后，我们将部署这个微调的模型为一个 **FastAPI** 服务，支持实时推理请求。

### 1. 微调 ChatGLM3

首先确保你已经准备好了合适的计算资源（如多GPU环境）来进行微调。如果你还没有安装 ChatGLM3 和其他依赖，可以按照以下步骤进行安装。

#### 安装依赖

```bash
pip install deepspeed transformers datasets accelerate torch wandb
pip install git+https://github.com/THU-KEG/ChatGLM-6B.git
pip install peft
```

#### 微调代码：LoRA 微调 ChatGLM3

```python
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import get_peft_model, LoraConfig, TaskType
from datasets import load_dataset
from tqdm import tqdm
from transformers import Trainer, TrainingArguments
import wandb

# 配置WandB
wandb.init(project="chatglm3-finetuning", entity="your-wandb-username")

# 加载ChatGLM3模型和Tokenizer
model_name = "THU-KEG/chatglm-6b"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name)

# 配置LoRA微调
lora_config = LoraConfig(
    r=8, 
    lora_alpha=16,
    lora_dropout=0.1,
    task_type=TaskType.CAUSAL_LM,
)
model = get_peft_model(model, lora_config)

# 加载数据集（使用自定义数据集或MRPC）
dataset = load_dataset("glue", "mrpc", split="train")

# 数据预处理
def preprocess_function(examples):
    return tokenizer(examples['sentence1'], examples['sentence2'], padding=True, truncation=True)

encoded_dataset = dataset.map(preprocess_function, batched=True)

# 配置训练参数
training_args = TrainingArguments(
    output_dir="./chatglm3-finetuned",
    evaluation_strategy="epoch",  # 每个epoch评估一次
    logging_dir="./logs",
    logging_steps=100,
    per_device_train_batch_size=4,
    per_device_eval_batch_size=8,
    num_train_epochs=3,
    weight_decay=0.01,
    save_strategy="epoch",  # 保存模型策略
    fp16=True,  # 使用混合精度训练
    deepspeed="./deepspeed_config.json",  # DeepSpeed配置文件
)

# 使用 Trainer API 训练模型
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=encoded_dataset,
    eval_dataset=encoded_dataset,
    tokenizer=tokenizer,
)

# 启动训练
trainer.train()
```

#### 训练配置文件：`deepspeed_config.json`

```json
{
  "train_batch_size": 16,
  "gradient_accumulation_steps": 2,
  "fp16": {
    "enabled": true
  },
  "zero_optimization": {
    "stage": 2
  },
  "offload_optimizer": {
    "device": "cpu",
    "pin_memory": true
  }
}
```

### 2. 部署微调后的 ChatGLM3 模型

微调完成后，保存模型并准备部署：

```python
# 保存微调后的模型
model.save_pretrained("./chatglm3-finetuned")
tokenizer.save_pretrained("./chatglm3-finetuned")
```

#### 创建 FastAPI 服务

现在，我们可以将微调后的模型部署为一个 FastAPI 服务，支持实时推理。

```python
from fastapi import FastAPI, WebSocket
from transformers import AutoTokenizer, AutoModelForCausalLM
from pydantic import BaseModel
import torch

# 加载微调后的模型
model = AutoModelForCausalLM.from_pretrained("./chatglm3-finetuned")
tokenizer = AutoTokenizer.from_pretrained("./chatglm3-finetuned")

# FastAPI应用实例
app = FastAPI()

class ChatRequest(BaseModel):
    user_id: str
    session_id: str
    query: str

# 推理函数
def chat_with_model(query: str):
    inputs = tokenizer(query, return_tensors="pt").to("cuda")
    output = model.generate(inputs["input_ids"], max_length=512)
    return tokenizer.decode(output[0], skip_special_tokens=True)

@app.websocket("/ws/chat/{user_id}/{session_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str, session_id: str):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            response = chat_with_model(data)
            await websocket.send_text(response)
    except WebSocketDisconnect:
        print(f"Client {user_id} disconnected")

@app.post("/chat")
async def chat(req: ChatRequest):
    response = chat_with_model(req.query)
    return {"response": response}
```

#### 启动 FastAPI 服务

在终端中启动 FastAPI 应用：

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

### 3. 添加模型监控（WandB）

在上面的代码中，我们已经初始化了 WandB 并在微调期间记录了每个推理步骤的数据。在 FastAPI 服务中，你也可以记录实时的推理日志，如用户输入和模型输出。

```python
import wandb

# 配置WandB
wandb.init(project="chatglm3-chat-service", entity="your-wandb-username")

# 在推理过程中记录WandB日志
def chat_with_model(query: str):
    inputs = tokenizer(query, return_tensors="pt").to("cuda")
    output = model.generate(inputs["input_ids"], max_length=512)
    response = tokenizer.decode(output[0], skip_special_tokens=True)
    
    # 记录日志到WandB
    wandb.log({
        "user_input": query,
        "system_response": response
    })
    
    return response
```

### 4. 完整的微调与部署流程

总结一下，完整的流程包括：

1. **模型微调**：使用 LoRA 微调 ChatGLM3，并保存微调后的模型。
2. **FastAPI 服务**：将微调后的模型部署为 FastAPI 服务，支持实时 WebSocket 推理。
3. **日志监控**：通过 WandB 记录推理过程中的日志，便于监控和分析。

### 5. 后续优化

- **性能优化**：可以根据实际负载调整 `batch_size` 和 `gradient_accumulation_steps`。
- **多机多卡训练**：使用 DeepSpeed 或其他分布式框架扩展训练，支持多GPU环境。
- **负载均衡**：可以使用反向代理如 Nginx 或其他负载均衡器来处理大规模并发请求。

---

这样，你就完成了从微调 ChatGLM3 到部署为 FastAPI 服务并加上监控的全过程。如果你希望进一步扩展功能，如集成 Redis 持久化历史记录或定时任务等，也可以继续在现有基础上进行优化。




为了在 ChatGLM3 微调和 FastAPI 服务中集成用户上下文记忆并将其存入 MySQL，你可以按照以下步骤进行扩展。我们将创建一个模型来存储用户上下文，并在每次对话时更新和查询 MySQL 数据库。

### 1. 设置 MySQL 数据库

首先，我们需要设置 MySQL 数据库，并创建一个用于存储用户对话历史的表。

#### 创建 MySQL 数据库和表

```sql
CREATE DATABASE chat_memory;

USE chat_memory;

CREATE TABLE user_context (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    session_id VARCHAR(255) NOT NULL,
    conversation TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 2. 安装 MySQL 依赖

在 FastAPI 项目中使用 MySQL，首先你需要安装相关的依赖库，如 `mysql-connector-python` 和 `SQLAlchemy`。

```bash
pip install mysql-connector-python sqlalchemy
```

### 3. 配置数据库连接

我们将使用 SQLAlchemy 来与 MySQL 进行交互。以下是创建数据库连接的配置。

#### 创建 `db.py` 配置数据库连接

```python
from sqlalchemy import create_engine, Column, Integer, String, Text, TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import mysql.connector

# MySQL数据库连接字符串
DATABASE_URL = "mysql+mysqlconnector://username:password@localhost/chat_memory"

# 创建SQLAlchemy基础类
Base = declarative_base()

# 定义UserContext模型
class UserContext(Base):
    __tablename__ = "user_context"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(255), nullable=False)
    session_id = Column(String(255), nullable=False)
    conversation = Column(Text, nullable=False)
    timestamp = Column(TIMESTAMP, default="CURRENT_TIMESTAMP")

# 创建数据库引擎
engine = create_engine(DATABASE_URL)

# 创建数据库会话
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建数据库表
Base.metadata.create_all(bind=engine)

# 获取会话
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

### 4. 修改 FastAPI 服务以支持用户上下文

接下来，我们将扩展 FastAPI 服务，将用户的对话上下文保存到 MySQL 中，并在需要时检索和更新它。

#### 更新 FastAPI 服务：保存与检索用户对话上下文

```python
from fastapi import FastAPI, WebSocket, Depends, HTTPException
from transformers import AutoTokenizer, AutoModelForCausalLM
from pydantic import BaseModel
from sqlalchemy.orm import Session
from db import get_db, UserContext
import torch
import wandb

# 初始化 FastAPI 和 WandB
app = FastAPI()

# 加载微调后的模型
model = AutoModelForCausalLM.from_pretrained("./chatglm3-finetuned")
tokenizer = AutoTokenizer.from_pretrained("./chatglm3-finetuned")

# 配置WandB
wandb.init(project="chatglm3-chat-service", entity="your-wandb-username")

# 推理函数
def chat_with_model(query: str):
    inputs = tokenizer(query, return_tensors="pt").to("cuda")
    output = model.generate(inputs["input_ids"], max_length=512)
    response = tokenizer.decode(output[0], skip_special_tokens=True)
    
    # 记录日志到WandB
    wandb.log({
        "user_input": query,
        "system_response": response
    })
    
    return response

# 获取或创建用户上下文
def get_user_context(db: Session, user_id: str, session_id: str):
    context = db.query(UserContext).filter(UserContext.user_id == user_id, UserContext.session_id == session_id).first()
    if not context:
        context = UserContext(user_id=user_id, session_id=session_id, conversation="")
        db.add(context)
        db.commit()
    return context

# 更新用户上下文
def update_user_context(db: Session, user_id: str, session_id: str, new_conversation: str):
    context = db.query(UserContext).filter(UserContext.user_id == user_id, UserContext.session_id == session_id).first()
    if context:
        context.conversation = new_conversation
        db.commit()

# WebSocket 连接处理：支持用户上下文
@app.websocket("/ws/chat/{user_id}/{session_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str, session_id: str, db: Session = Depends(get_db)):
    await websocket.accept()
    
    # 获取或创建用户上下文
    user_context = get_user_context(db, user_id, session_id)
    
    try:
        while True:
            data = await websocket.receive_text()
            
            # 获取当前对话上下文
            conversation_history = user_context.conversation
            full_query = conversation_history + "\nUser: " + data + "\nAI:"

            # 执行推理
            response = chat_with_model(full_query)

            # 更新用户上下文
            updated_conversation = conversation_history + "\nUser: " + data + "\nAI:" + response
            update_user_context(db, user_id, session_id, updated_conversation)

            # 发送响应
            await websocket.send_text(response)

    except WebSocketDisconnect:
        print(f"Client {user_id} disconnected")

# HTTP 请求处理：支持用户上下文
class ChatRequest(BaseModel):
    user_id: str
    session_id: str
    query: str

@app.post("/chat")
async def chat(req: ChatRequest, db: Session = Depends(get_db)):
    user_context = get_user_context(db, req.user_id, req.session_id)
    
    # 获取当前对话上下文
    conversation_history = user_context.conversation
    full_query = conversation_history + "\nUser: " + req.query + "\nAI:"

    # 执行推理
    response = chat_with_model(full_query)

    # 更新用户上下文
    updated_conversation = conversation_history + "\nUser: " + req.query + "\nAI:" + response
    update_user_context(db, req.user_id, req.session_id, updated_conversation)

    return {"response": response}
```

### 5. 启动服务

1. 启动 FastAPI 服务：

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

2. 访问 `http://localhost:8000/docs` 查看 FastAPI 自动生成的文档界面，并测试 `/chat` 接口。

### 6. 代码解释

1. **数据库连接**：通过 SQLAlchemy 连接 MySQL 数据库，并定义了 `UserContext` 表来存储用户的对话上下文。每个用户的 `user_id` 和 `session_id` 会唯一对应一条记录，存储用户与 AI 的对话。
2. **WebSocket 支持**：当用户与服务器通过 WebSocket 连接时，聊天记录会在 MySQL 中更新，每个新的消息都会被附加到用户的对话记录中。
3. **上下文更新**：每次收到用户的消息，系统会结合现有的对话历史进行推理，并将最新的对话记录更新回数据库。
4. **WandB 日志**：通过 `wandb.log()` 将用户输入和系统输出进行日志记录，便于监控。

### 7. 后续优化

- **定期清理旧记录**：可以考虑为用户对话历史添加过期时间，例如每隔一段时间清理不再活跃用户的历史记录，或者根据业务需求定期清理历史。
- **性能优化**：当对话历史变得很长时，可以考虑引入上下文长度限制策略，避免超过模型的最大输入长度。
- **高可用性部署**：如果需要部署到生产环境，考虑将 FastAPI 服务与 Docker 容器、Kubernetes 等技术结合，确保高可用性和水平扩展。

通过这种方式，你可以为每个用户维护一个长期对话上下文，并将这些数据存储在 MySQL 中，从而提供持续的、个性化的对话服务。


当对话历史变得很长时，超过模型的最大输入长度（例如，对于 GPT-2、ChatGLM 或其他大语言模型，通常有 512、1024 或 2048 token 的限制）可能会导致推理失败或性能下降。因此，我们可以引入上下文长度限制策略，并定期清理旧记录，确保模型能够处理合理长度的对话输入。

### 1. 上下文长度限制策略

为了确保每次推理时，输入的对话历史不会超过模型的最大输入长度，我们需要在每次更新对话历史时进行控制。下面介绍两种常见的策略：

- **截断历史**：在对话历史超过最大长度时，截断掉较旧的部分，只保留最新的对话记录。
- **精简历史**：对历史进行筛选，删除无关的部分，只保留重要的对话信息。

### 2. 实现上下文长度控制

假设我们使用 ChatGLM 或类似的模型，最大输入长度为 2048 tokens。我们可以使用 `tokenizer.encode` 或 `tokenizer.batch_encode_plus` 获取输入文本的 token 数量，并根据最大长度进行调整。

#### 修改 `chat_with_model` 函数实现上下文长度控制

```python
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

# 加载微调后的模型和tokenizer
model = AutoModelForCausalLM.from_pretrained("./chatglm3-finetuned")
tokenizer = AutoTokenizer.from_pretrained("./chatglm3-finetuned")

MAX_INPUT_LENGTH = 2048  # 假设最大输入长度为2048 tokens

# 推理函数，添加上下文长度控制
def chat_with_model(query: str, conversation_history: str):
    # 合并历史和当前用户输入
    full_query = conversation_history + "\nUser: " + query + "\nAI:"

    # 编码文本并检查长度
    input_ids = tokenizer.encode(full_query, return_tensors="pt").to("cuda")
    
    # 如果输入的token数超过最大限制，截断旧的部分
    if input_ids.shape[1] > MAX_INPUT_LENGTH:
        # 计算需要截断的长度
        truncated_input_ids = input_ids[:, -MAX_INPUT_LENGTH:]
        # 解码并生成回复
        output = model.generate(truncated_input_ids, max_length=512)
    else:
        # 如果没有超出最大长度，直接生成
        output = model.generate(input_ids, max_length=512)

    response = tokenizer.decode(output[0], skip_special_tokens=True)
    return response
```

### 3. 定期清理旧记录

为了避免数据库中过于庞大的对话历史数据占用过多存储空间，我们可以定期清理不再活跃的用户对话记录。可以通过设置过期时间（如每 30 天清理一次旧的对话记录）或基于用户活跃度进行清理。

#### 添加清理历史的功能

我们可以在数据库中增加一个 `timestamp` 字段，并根据时间戳来定期清理过期的记录。

```python
from sqlalchemy import func

# 定期清理过期记录
def clean_old_conversations(db: Session, expiration_days: int = 30):
    # 获取当前时间减去过期天数
    expiration_time = func.now() - func.interval(f"{expiration_days} day")
    
    # 删除过期的记录
    db.query(UserContext).filter(UserContext.timestamp < expiration_time).delete()
    db.commit()
```

#### 定时任务

你可以使用如 `APScheduler` 或 `Celery` 等工具来定期清理过期的用户对话记录。

##### 使用 APScheduler 定期清理任务

首先，安装 `APScheduler`：

```bash
pip install apscheduler
```

然后，在 FastAPI 服务中设置定时清理任务：

```python
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime

# 定时任务：每天午夜清理过期记录
def scheduled_clean():
    with SessionLocal() as db:
        clean_old_conversations(db, expiration_days=30)

# 启动调度器
scheduler = BackgroundScheduler()
scheduler.add_job(scheduled_clean, 'interval', days=1, next_run_time=datetime.now())
scheduler.start()

# 启动 FastAPI 应用时，启动调度器
@app.on_event("startup")
async def startup():
    scheduler.start()
```

### 4. 更新上下文管理策略

结合上述上下文控制和定期清理记录，我们可以确保每次生成对话时输入的上下文不会过长，同时也保持数据库中记录的合理性。

#### 更新对话历史管理

我们更新用户对话历史时，会对历史内容进行检查和更新，保证不超过最大长度限制。

```python
# 更新用户上下文
def update_user_context(db: Session, user_id: str, session_id: str, new_conversation: str):
    context = db.query(UserContext).filter(UserContext.user_id == user_id, UserContext.session_id == session_id).first()
    
    if context:
        # 检查历史对话的长度，进行必要的截断
        conversation_history = context.conversation + "\n" + new_conversation
        # 截断超出最大长度的部分
        input_ids = tokenizer.encode(conversation_history, return_tensors="pt").to("cuda")
        if input_ids.shape[1] > MAX_INPUT_LENGTH:
            truncated_conversation = tokenizer.decode(input_ids[:, -MAX_INPUT_LENGTH:], skip_special_tokens=True)
        else:
            truncated_conversation = conversation_history
        context.conversation = truncated_conversation
        db.commit()
```

### 5. 总结

通过上述策略和实现：

- 我们可以在每次推理时动态控制输入的上下文长度，避免超过模型的最大输入限制。
- 我们定期清理过期的对话历史，以减少存储压力。
- 使用定时任务（如 `APScheduler`）定期执行清理任务，确保数据库中保持合理大小的对话记录。

这些措施能有效帮助你在长时间运行对话服务时，确保服务的高效性和稳定性，避免出现 `OOM` 或性能下降等问题。



在生产环境中，确保服务的高可用性和可扩展性至关重要。结合 Docker 容器和 Kubernetes 可以帮助实现这些目标。以下是如何将 FastAPI 服务与 Docker 和 Kubernetes 技术结合，以确保高可用性和水平扩展的基本步骤。

### 1. Docker 化 FastAPI 服务

#### 步骤 1：创建 Dockerfile

首先，创建一个 `Dockerfile`，定义如何构建 FastAPI 服务的镜像。假设你已经有一个 FastAPI 项目并且需要将其部署为容器。

```Dockerfile
# 使用官方 Python 镜像作为基础镜像
FROM python:3.9-slim

# 设置工作目录
WORKDIR /app

# 复制依赖项清单文件到容器中
COPY requirements.txt .

# 安装 FastAPI 和相关依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制整个项目到容器中
COPY . /app

# 设置 FastAPI 运行时命令
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

在 `requirements.txt` 中添加你所需要的依赖项，例如：

```txt
fastapi
uvicorn
redis
sqlalchemy
```

#### 步骤 2：构建 Docker 镜像

在项目根目录下执行以下命令，构建 Docker 镜像：

```bash
docker build -t my-fastapi-app .
```

#### 步骤 3：运行 Docker 容器

构建完成后，你可以运行容器：

```bash
docker run -d -p 8000:8000 my-fastapi-app
```

这将在本地的 `8000` 端口启动 FastAPI 服务。

### 2. 将 FastAPI 服务部署到 Kubernetes

Kubernetes 是一种开源平台，自动化了应用程序的部署、扩展和管理。下面介绍如何使用 Kubernetes 部署和管理你的 FastAPI 服务。

#### 步骤 1：创建 Kubernetes 部署配置文件

首先，创建一个名为 `deployment.yaml` 的 Kubernetes 配置文件，描述如何部署 FastAPI 服务。

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: fastapi-deployment
spec:
  replicas: 3  # 部署3个副本以实现高可用性
  selector:
    matchLabels:
      app: fastapi
  template:
    metadata:
      labels:
        app: fastapi
    spec:
      containers:
        - name: fastapi
          image: my-fastapi-app:latest  # 这里使用之前构建的镜像
          ports:
            - containerPort: 8000
---
apiVersion: v1
kind: Service
metadata:
  name: fastapi-service
spec:
  selector:
    app: fastapi
  ports:
    - protocol: TCP
      port: 80
      targetPort: 8000
  type: LoadBalancer  # 这里使用 LoadBalancer 类型，支持自动分配外部 IP
```

- **replicas**：指定要运行的副本数（这里是3），可以根据实际负载进行调整。
- **selector**：匹配标记为 `app: fastapi` 的所有容器。
- **Service**：定义一个 Kubernetes Service，用于暴露 FastAPI 服务，方便外部访问。

#### 步骤 2：应用 Kubernetes 配置

使用 `kubectl` 命令将上述配置应用到 Kubernetes 集群中。

```bash
kubectl apply -f deployment.yaml
```

#### 步骤 3：检查部署状态

你可以通过以下命令检查部署状态：

```bash
kubectl get deployments
kubectl get pods
kubectl get svc
```

确保 `fastapi-deployment` 部署成功，并且至少有一个 `Pod` 正在运行。

#### 步骤 4：访问服务

如果你使用的是 `LoadBalancer` 类型的服务，你可以使用以下命令获取外部 IP 地址：

```bash
kubectl get svc fastapi-service
```

如果使用的是集群内部负载均衡器，你可以使用集群内部的 DNS 名称来访问服务。

### 3. 高可用性和水平扩展

Kubernetes 能够自动扩展和负载均衡流量，以确保高可用性。

#### 步骤 1：水平自动扩展 (Horizontal Pod Autoscaler)

Kubernetes 支持根据 CPU 或内存的使用情况自动扩展应用程序的副本数。你可以创建一个自动扩展器（HPA），它根据负载情况自动增加或减少 `Pod` 数量。

首先，确保你已启用 `metrics-server`，它是 Kubernetes 提供的用于资源使用指标的服务。然后，创建一个 HPA 配置：

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: fastapi-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: fastapi-deployment
  minReplicas: 3
  maxReplicas: 10
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 80
```

这个配置文件设置了：

- `minReplicas`：最小副本数。
- `maxReplicas`：最大副本数。
- `averageUtilization`：CPU 使用率达到 80% 时，自动扩展副本数。

然后，应用 HPA 配置：

```bash
kubectl apply -f hpa.yaml
```

#### 步骤 2：负载均衡

Kubernetes 中的 `Service` 对象会自动为多个副本提供负载均衡。如果你使用了 `LoadBalancer` 类型的服务，它将会通过外部负载均衡器（如云提供商的负载均衡器）分发流量。

### 4. 持续集成与持续交付（CI/CD）

为了实现高效的开发和生产环境发布，你可以使用 CI/CD 工具（如 GitLab CI、GitHub Actions、Jenkins 等）来实现持续集成和持续交付。这包括：

- 自动构建 Docker 镜像并推送到容器镜像仓库（如 Docker Hub 或 GitHub Packages）。
- 自动部署更新到 Kubernetes 集群。
- 自动化测试和验证。

以下是一个简单的 GitHub Actions 示例配置：

```yaml
name: CI/CD for FastAPI app

on:
  push:
    branches:
      - main

jobs:
  build_and_deploy:
    runs-on: ubuntu-latest
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v2

    - name: Set up Docker Buildx
      uses: docker/setup-buildx-action@v1

    - name: Build and push Docker image
      uses: docker/build-push-action@v2
      with:
        context: .
        push: true
        tags: my-fastapi-app:latest

    - name: Deploy to Kubernetes
      run: |
        kubectl apply -f deployment.yaml
```

### 5. 总结

通过结合 Docker 和 Kubernetes，可以确保 FastAPI 服务具有高可用性、水平扩展能力，并且能够自动处理负载变化。上述流程包括：

- **Docker**：将 FastAPI 服务容器化，方便部署。
- **Kubernetes**：通过部署、服务、负载均衡和自动扩展实现高可用性。
- **水平扩展**：使用 Kubernetes Horizontal Pod Autoscaler (HPA) 动态扩展副本数。
- **CI/CD**：自动化构建、测试和部署流程，确保快速更新。

这种部署方式使得你的 FastAPI 应用具备了高可用性、可扩展性以及灵活的管理能力，能够适应生产环境中的大规模负载。
















