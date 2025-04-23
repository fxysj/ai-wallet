# 导入 PyTorch 库
import torch

# 导入 HuggingFace 的 BERT 模型、分词器、Trainer 和训练参数定义工具
from transformers import BertForSequenceClassification, BertTokenizer, Trainer, TrainingArguments

# 导入 HuggingFace datasets 库，用于加载标准数据集
from datasets import load_dataset

def main():
    # 加载预训练的 BERT 模型用于文本分类任务（GLUE 任务中 MRPC 是二分类）
    model = BertForSequenceClassification.from_pretrained("bert-base-uncased", num_labels=2)

    # 加载对应的 BERT 分词器（与模型结构匹配）
    tokenizer = BertTokenizer.from_pretrained("bert-base-uncased")

    # 加载 GLUE 数据集中的 MRPC 子任务（句子对是否语义相同）
    dataset = load_dataset("glue", "mrpc")

    # 定义分词函数，将句子对编码为模型输入格式
    def tokenize_fn(examples):
        return tokenizer(
            examples["sentence1"],                # 第一句
            examples["sentence2"],                # 第二句
            truncation=True,                      # 超出 max_length 就截断
            padding="max_length",                 # 不足的就 padding 补齐
            max_length=128                        # 最大长度 128 个 token
        )

    # 应用分词函数到整个数据集（batched=True 表示一次处理多个样本）
    tokenized = dataset.map(tokenize_fn, batched=True)

    # 设置数据格式为 PyTorch tensor，提取输入和标签列用于训练
    tokenized.set_format(type="torch", columns=["input_ids", "attention_mask", "label"])

    # 定义训练参数
    training_args = TrainingArguments(
        output_dir="./output",                       # 模型和日志的输出路径
        per_device_train_batch_size=8,               # 每张 GPU 的训练 batch size
        per_device_eval_batch_size=8,                # 每张 GPU 的验证 batch size
        evaluation_strategy="epoch",                 # 每个 epoch 评估一次
        num_train_epochs=3,                          # 总共训练 3 个 epoch
        save_strategy="epoch",                       # 每个 epoch 保存一次模型
        logging_dir="./logs",                        # 日志保存目录
        deepspeed="./ds_config.json",                # 指定 DeepSpeed 配置文件路径
        fp16=True                                    # 开启混合精度训练（节省显存 + 加速）
    )

    # 使用 Trainer 封装训练流程（Trainer 是 HuggingFace 的训练框架）
    trainer = Trainer(
        model=model,                                 # 传入模型
        args=training_args,                          # 传入训练参数
        train_dataset=tokenized["train"],            # 指定训练集
        eval_dataset=tokenized["validation"]         # 指定验证集
    )

    # 开始训练
    trainer.train()

# 如果是主进程运行这个文件，则执行 main 函数
if __name__ == "__main__":
    main()
