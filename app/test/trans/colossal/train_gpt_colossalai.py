import os
import torch
from torch.utils.data import DataLoader
from transformers import GPT2LMHeadModel, AutoTokenizer
from datasets import load_dataset

import colossalai
from colossalai.nn.optimizer import HybridAdam
from colossalai.nn.lr_scheduler import CosineAnnealingLR
from colossalai.nn.parallel import ZeroDDP
from colossalai.nn.loss import CrossEntropyLoss
from colossalai.trainer import Trainer
from colossalai.utils import get_dataloader

from colossalai.logging import get_dist_logger
from colossalai.core import global_context as gpc
from colossalai.initialize import launch

# 初始化分布式训练环境，使用默认配置即可
launch(config={}, rank=0, world_size=1, host='localhost', port=29500, backend='nccl')

# 获取分布式日志器
logger = get_dist_logger()

# 加载中文 GPT2 模型和分词器
tokenizer = AutoTokenizer.from_pretrained("IDEA-CCNL/Wenzhong-GPT2-110M")
model = GPT2LMHeadModel.from_pretrained("IDEA-CCNL/Wenzhong-GPT2-110M")

# 使用 ZeroDDP 包装模型，减少内存冗余
model = ZeroDDP(model)

# 加载中文数据集（这里以 THUCNews 为例）
dataset = load_dataset("thucnews", split="train[:1%]")

# 数据预处理函数，将新闻文本编码为 GPT 输入格式
def tokenize_function(example):
    inputs = tokenizer(example["text"], truncation=True, padding="max_length", max_length=128)
    inputs["labels"] = inputs["input_ids"].copy()
    return inputs

# 预处理并构建 PyTorch DataLoader
tokenized_dataset = dataset.map(tokenize_function, batched=True)
tokenized_dataset.set_format(type='torch', columns=['input_ids', 'attention_mask', 'labels'])

train_dataloader = DataLoader(tokenized_dataset, batch_size=8, shuffle=True)

# 定义优化器
optimizer = HybridAdam(model.parameters(), lr=5e-5)

# 定义学习率调度器
lr_scheduler = CosineAnnealingLR(optimizer=optimizer, total_steps=1000)

# 定义损失函数
criterion = CrossEntropyLoss()

# 构建 Trainer
trainer = Trainer(
    model=model,
    optimizer=optimizer,
    criterion=criterion,
    train_dataloader=train_dataloader,
    test_dataloader=None,
    lr_scheduler=lr_scheduler
)

# 启动训练
trainer.fit(epochs=3)
