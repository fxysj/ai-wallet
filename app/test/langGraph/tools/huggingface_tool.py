# tools/huggingface_tool.py
from transformers import pipeline

# 使用 transformers 提供的情感分析 pipeline
#sentiment_pipeline = pipeline("sentiment-analysis")

# 推荐：指定模型名称和版本
sentiment_pipeline = pipeline(
    "sentiment-analysis",
    model="distilbert/distilbert-base-uncased-finetuned-sst-2-english",
    revision="714eb0f"  # 可选，表示固定某个 commit 版本
)

def analyze_sentiment_batch(comments: list[str]) -> dict:
    # 推荐：指定模型名称和版本
    results = sentiment_pipeline(comments)

    # 统计情感分布
    total = len(results)
    pos_count = sum(1 for r in results if r['label'] == 'POSITIVE')
    neg_count = sum(1 for r in results if r['label'] == 'NEGATIVE')

    return {
        "total": total,
        "positive": pos_count,
        "negative": neg_count,
        "positive_ratio": pos_count / total if total else 0,
        "raw_results": results
    }
