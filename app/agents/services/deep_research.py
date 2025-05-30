def transform_investors(investors):
    if not investors:  # 空列表直接返回
        return investors

    type_mapping = {
        1: "Project",
        2: "VC",
        3: "People"
    }
    for investor in investors:
        if investor.get("type") in type_mapping:
            investor["type"] = type_mapping[investor["type"]]
    return investors



from typing import Union, List, Dict, Any

def replace_empty_fields(data: Union[Dict, List[Dict]]) -> Union[Dict, List[Dict]]:
    def is_empty(value: Any) -> bool:
        return value is None or (isinstance(value, str) and value.strip() == "")

    def process(item: Any) -> Any:
        if isinstance(item, dict):
            return {k: process(v) if isinstance(v, (dict, list)) else ('--' if is_empty(v) else v)
                    for k, v in item.items()}
        elif isinstance(item, list):
            return [process(elem) for elem in item]
        else:
            return item

    if not data or data == {} or data == []:
        return data

    return process(data)



if __name__ == '__main__':
    print(transform_investors([]))
    # 输出: []
    # 1. 单个嵌套字典
    input1 = {
        "name": "Alice",
        "age": "",
        "email": None,
        "profile": {
            "address": " ",
            "zipcode": "12345",
            "contact": {
                "phone": "",
                "wechat": None
            }
        },
        "score": 0.00,
        "active": False
    }
    print(replace_empty_fields(input1))

    # 2. 嵌套字典数组
    input2 = [
        {
            "name": "",
            "info": {
                "email": "  ",
                "details": {
                    "bio": None
                }
            }
        },
        {
            "name": "Bob",
            "info": {
                "email": "bob@example.com",
                "details": {
                    "bio": "Engineer"
                }
            }
        }
    ]
    print(replace_empty_fields(input2))

    # 3. 空对象
    print(replace_empty_fields({"name":"ss","info":{"sex":0,"ss":""}}))  # {}
    print(replace_empty_fields([]))  # []



