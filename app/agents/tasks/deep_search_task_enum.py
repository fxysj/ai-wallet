class EnumValueFormatter:
    def __init__(self):
        self._handlers = {}

    def on(self, value, *, title, description):
        """
        注册一个枚举值对应的 title 和 description。
        """
        self._handlers[str(value).strip()] = {
            "title": title,
            "description": description
        }
        return self

    def format(self, input_value):
        """
        根据传入值返回对应的格式化信息，未匹配则返回空字符串。
        """
        key = str(input_value).strip()
        if key in self._handlers:
            return {
                "title": self._handlers[key]["title"],
                "description": self._handlers[key]["description"],
                "value": key
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

    def on(self, value, *, title, description) -> 'EnumValueRegistry':
        """
        为当前字段注册一个枚举值对应的格式化信息。
        """
        if self._current_field:
            self._registry[self._current_field].on(value, title=title, description=description)
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

    # 注册字段 is_open_source 和 status
    registry \
        .register("is_open_source") \
            .on("0", title="未开源", description="该合约未开源，有潜在风险。") \
            .on(1, title="已开源", description="该合约已开源，可查看源码。") \
    .on("",title="111",description="ss")\
        .register("status") \
            .on("0", title="无效", description="该状态无效") \
            .on("1", title="有效", description="该状态有效")

    # 测试
    print(registry.format("is_open_source", 1))         # ✅ 命中
    print(registry.format("status", "0"))               # ✅ 命中
    print(registry.format("is_open_source", ""))        # ❌ 未命中值 -> 返回 ""
    print(registry.format("is_open_source", "2"))       # ❌ 未命中值 -> 返回 ""
    print(registry.format("unknown_field", 1))          # ❌ 未注册字段 -> 返回 ""
