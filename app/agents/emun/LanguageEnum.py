from enum import Enum

class LanguageEnum(Enum):
    EN = "英语"
    ZH_HANS = "简体"
    ZH_HANT = "繁体"

    @classmethod
    def from_code(cls, code: str):
        if not code:
            return None
        mapping = {
            "en": cls.EN,
            "zh-Hans": cls.ZH_HANS,
            "zh-Hant": cls.ZH_HANT,
        }
        return mapping.get(code.strip())


from fastapi import Request
async def get_lang_from_headers(request: Request) -> str:
    lang_code = request.headers.get("Lang")
    lang_enum = LanguageEnum.from_code(lang_code)
    if lang_enum:
        return lang_enum.value
    return "英语"
if __name__ == '__main__':
    print(LanguageEnum.EN.value)  # 输出: 英语
    print(LanguageEnum.ZH_HANS.name)  # 输出: ZH_HANS
