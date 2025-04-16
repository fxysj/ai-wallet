from langchain_core.prompts import PromptTemplate

from app.agents.lib.llm.llm import LLMFactory
llm = LLMFactory.getDefaultOPENAI()
with open("sal.md", "r", encoding="utf-8") as f:
    template = f.read()
    prompt_template = PromptTemplate(
        template=template,
    )
    chain = prompt_template|llm
    res = chain.invoke(input={
        "messages":[
            {"user","你好"},
            {"user","好的"},
            {"system",template}
        ]
    })
    print(res)