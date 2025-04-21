from app.test.langGraph.tools.huggingface_tool import analyze_sentiment_batch
from app.test.langGraph.tools.translate_tool import detect_and_translate_to_english
from app.test.langGraph.tools.versioning import save_user_version, compare_versions

if __name__ == "__main__":
    comments = ["这款产品真不错，我很喜欢", "物流很慢，不满意"]
    translated = [detect_and_translate_to_english(c) for c in comments]
    print("🌍 Translated:", translated)

    analysis = analyze_sentiment_batch(translated)
    print("📊 Sentiment:", analysis)

    save_user_version("u001", translated)
    result = compare_versions("u001", ["This is a great product!", "Not good service"])
    print("📁 Version Compare:", result)