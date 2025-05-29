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

if __name__ == '__main__':
    print(transform_investors([]))
    # 输出: []
