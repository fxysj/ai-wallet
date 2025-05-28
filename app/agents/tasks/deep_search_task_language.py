from app.agents.emun.LanguageEnum import LanguageEnum


class EnumValueFormatter:
    def __init__(self):
        self._handlers = {}

    def on(self, value, *, titles, descriptions, riskLevel=None, risked=None):
        """
        注册一个枚举值对应的多语言 title、description、riskLevel 和 risked。
        titles/descriptions 是字典，如 {'en': 'xxx', 'zh-CN': 'xxx', 'zh-TW': 'xxx'}
        """
        self._handlers[str(value).strip()] = {
            "titles": titles,
            "descriptions": descriptions,
            "riskLevel": riskLevel,
            "risked": risked
        }
        return self

    def format(self, input_value, language='en'):
        """
        根据传入值和语言返回对应的格式化信息，未匹配则返回空字符串。
        """
        key = str(input_value).strip()
        if key in self._handlers:
            handler = self._handlers[key]
            title = handler["titles"].get(language, handler["titles"].get("en", ""))
            description = handler["descriptions"].get(language, handler["descriptions"].get("en", ""))
            return {
                "title": title,
                "description": description,
                "value": key,
                "riskLevel": handler.get("riskLevel"),
                "risked": handler.get("risked")
            }
        else:
            return ""


class EnumValueRegistry:
    def __init__(self):
        self._registry = {}
        self._current_field = None

    def register(self, field_name: str) -> 'EnumValueRegistry':
        if field_name not in self._registry:
            self._registry[field_name] = EnumValueFormatter()
        self._current_field = field_name
        return self

    def on(self, value, *, titles, descriptions, riskLevel=None, risked=None) -> 'EnumValueRegistry':
        if self._current_field:
            self._registry[self._current_field].on(
                value,
                titles=titles,
                descriptions=descriptions,
                riskLevel=riskLevel,
                risked=risked
            )
        return self

    def format(self, field_name: str, value, language='en'):
        formatter = self._registry.get(field_name)
        if formatter:
            return formatter.format(value, language)
        else:
            return ""

if __name__ == '__main__':
    if __name__ == '__main__':
        registry = EnumValueRegistry()

        registry.register("is_open_source") \
            .on("1",
                titles={
                     LanguageEnum.EN.value: "Contract source code verified",
                    LanguageEnum.ZH_HANT.value: "合约已开源",
                    LanguageEnum.ZH_HANS.value: "合約已開源"
                },
                descriptions={
                    LanguageEnum.EN.value: "This token contract is open source. You can check the contract code for details. Unsourced token contracts are likely to have malicious functions to defraud their users of their assets.",
                    LanguageEnum.ZH_HANT.value: "此代币合约已开源，可查询合约代码详情。未开源的代币合约更可能存在恶意机制，骗取用户资产。",
                    LanguageEnum.ZH_HANS.value: "此代幣合約已開源，可查詢合約代碼詳情。未開源的代幣合約更可能存在惡意機制，騙用戶資產。"
                },
                riskLevel="medium",
                risked=False) \
            .on("0",
                titles={
                    "en": "Contract source code can't verified",
                    "zh-CN": "合约未开源",
                    "zh-TW": "合約未開源"
                },
                descriptions={
                    "en": "This token contract is not open source. Unsourced token contracts are likely to have malicious functions to defraud their users of their assets.",
                    "zh-CN": "此代币合约未开源。未开源的代币合约更可能存在恶意机制，骗取用户资产。",
                    "zh-TW": "此代幣合約未開源。未開源的代幣合約更可能存在惡意機制，騙用戶資產。"
                },
                riskLevel="high",
                risked=True)

        print(registry.format("is_open_source", "1", language=LanguageEnum.ZH_HANS.value))


