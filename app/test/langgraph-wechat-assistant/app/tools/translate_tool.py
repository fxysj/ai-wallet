# tools/translate_tool.py 语言归一化（翻译）
from deep_translator import GoogleTranslator
from langdetect import detect

def detect_and_translate_to_english(text: str) -> str:
    try:
        lang = detect(text)
        if lang != "en":
            return GoogleTranslator(source=lang, target="en").translate(text)
        return text
    except Exception as e:
        return f"Translation Error: {e}"
