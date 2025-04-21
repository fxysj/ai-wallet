examples = [
    {
        "goal": "减脂",
        "plan": "1. 每天控制热量摄入在 1500 千卡左右。\n2. 主食选择燕麦、全麦面包，控制碳水摄入。\n3. 增加蛋白质来源，如鸡胸肉、鸡蛋、豆腐。\n4. 每周至少运动 4 次，每次 45 分钟。"
    },
    {
        "goal": "增肌",
        "plan": "1. 每日热量摄入高于消耗 300 千卡。\n2. 多吃高蛋白食物，如牛肉、鸡蛋、乳清蛋白粉。\n3. 配合阻力训练，每周 4~5 次。\n4. 睡眠保证 7~8 小时，促进恢复。"
    }
]
from langchain.prompts import PromptTemplate, FewShotPromptTemplate

# 子模板（每个示例的格式）
example_prompt = PromptTemplate(
    input_variables=["goal", "plan"],
    template="目标: {goal}\n饮食计划: {plan}"
)

# Few-shot 主模板
few_shot_prompt = FewShotPromptTemplate(
    examples=examples,
    example_prompt=example_prompt,
    prefix="你是一个专业的营养师，根据用户的目标，制定一份详细的饮食和运动计划。以下是一些示例：",
    suffix="现在请根据用户的目标制定计划：\n目标: {goal}\n饮食计划:",
    input_variables=["goal"],
    example_separator="\n\n"
)
print(few_shot_prompt.format(goal="三高控制"))

