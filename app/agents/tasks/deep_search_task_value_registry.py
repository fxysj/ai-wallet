class EnumValueFormatter:
    def __init__(self):
        self._handlers = {}

    def on(self, value, *, title, description, riskLevel=None, risked=None):
        """
        注册一个枚举值对应的 title、description、riskLevel 和 risked。
        """
        self._handlers[str(value).strip()] = {
            "title": title,
            "description": description,
            "riskLevel": riskLevel,
            "risked": risked
        }
        return self

    def format(self, input_value):
        """
        根据传入值返回对应的格式化信息，未匹配则返回空字符串。
        """
        key = str(input_value).strip()
        if key in self._handlers:
            handler = self._handlers[key]
            return {
                "title": handler["title"],
                "description": handler["description"],
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
        """
        注册字段并设为当前操作对象，支持链式调用。
        """
        if field_name not in self._registry:
            self._registry[field_name] = EnumValueFormatter()
        self._current_field = field_name
        return self

    def on(self, value, *, title, description, riskLevel=None, risked=None) -> 'EnumValueRegistry':
        """
        为当前字段注册一个枚举值对应的格式化信息。
        """
        if self._current_field:
            self._registry[self._current_field].on(
                value,
                title=title,
                description=description,
                riskLevel=riskLevel,
                risked=risked
            )
        return self

    def format(self, field_name: str, value):
        """
        对指定字段和值进行格式化，字段未注册或值未匹配返回空字符串。
        """
        formatter = self._registry.get(field_name)
        if formatter:
            return formatter.format(value)
        else:
            return ""


if __name__ == '__main__':
    registry = EnumValueRegistry()

    # 注册字段 gas_abuse
    registry.register("gas_abuse") \
        .on("1",
            title="This Token Is A Gas Abuser",
            description="Gas abuse activity has been found.",
            riskLevel="high",
            risked=True) \
        .on("0",
            title="This Token Is Not A Gas Abuser",
            description="No gas abuse activity has been found.",
            riskLevel="low",
            risked=False)

    print(registry.format("gas_abuse", "0"))

    registry = EnumValueRegistry()

    # 注册字段 is_open_source 和 status
    registry.register("gas_abuse") \
        .on("1", title="This Token Is A Gas Abuser", description="Gas abuse activity has been found.",riskLevel="") \
        .on("0", title="This Token Is Not A Gas Abuser", description="No gas abuse activity has been found.",riskLevel="")
    print(registry.format("gas_abuse", "0"))

