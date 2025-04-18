class EnumValueFormatter:
    def __init__(self):
        self._handlers = {}
        self._default = {
            "title": "Unknown",
            "description": "Unknown value provided.",
        }

    def on(self, value, *, title, description):
        self._handlers[str(value).strip()] = {
            "title": title,
            "description": description
        }
        return self

    def format(self, input_value):
        key = str(input_value).strip()
        if key in self._handlers:
            return {
                "title": self._handlers[key]["title"],
                "description": self._handlers[key]["description"],
                "value": key
            }
        else:
            return {
                "title": self._default["title"],
                "description": self._default["description"],
                "value": key
            }

    def set_default(self, *, title, description):
        self._default = {
            "title": title,
            "description": description
        }
        return self


class EnumValueRegistry:
    def __init__(self):
        self._registry = {}
        self._current_field = None

    def register(self, field_name: str) -> 'EnumValueRegistry':
        if field_name not in self._registry:
            self._registry[field_name] = EnumValueFormatter()
        self._current_field = field_name
        return self

    def on(self, value, *, title, description):
        if self._current_field:
            self._registry[self._current_field].on(value, title=title, description=description)
        return self

    def set_default(self, *, title, description):
        if self._current_field:
            self._registry[self._current_field].set_default(title=title, description=description)
        return self

    def format(self, field_name: str, value):
        formatter = self._registry.get(field_name)
        if formatter:
            return formatter.format(value)
        else:
            return {
                "title": "Unregistered field",
                "description": f"Field '{field_name}' is not registered.",
                "value": str(value)
            }
if __name__ == '__main__':
    registry = EnumValueRegistry()

    registry \
        .register("is_open_source") \
        .on("0", title="未开源", description="该合约未开源，有潜在风险。") \
        .on(1, title="已开源", description="该合约已开源，可查看源码。") \
        .set_default(title="未知开源状态", description="未知的开源标识。") \
        .register("status") \
        .on("0", title="无效", description="该状态无效") \
        .on("1", title="有效", description="该状态有效")

    print(registry.format("is_open_source", 1))
    print(registry.format("status", "0"))
    print(registry.format("unknown_field", 1))  # 未注册字段