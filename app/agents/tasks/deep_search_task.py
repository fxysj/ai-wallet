#深度搜索分析
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate

from app.agents.lib.llm.llm import LLMFactory
from app.agents.proptemts.research_prompt import ROOTDATA_SEARCH_TEMPLATE
from app.agents.schemas import AgentState
from app.agents.form.form import *
async def research_task(state: AgentState) -> AgentState:
    #这里是深度搜索的功能
    print("research_task")
    print("DEBUG - attached_data 类型:", type(state.attached_data))
    print("DEBUG - attached_data 内容:", state.attached_data)
    data = state.attached_data
    form = data.get("form")
    ResearchForm(
        query=form.get("query"),
        depth=form.get("depth"),
        mode=form.get("mode"),
        selectedProject=form.get("selectedProject"),
    )
    prompt = PromptTemplate(
        template=ROOTDATA_SEARCH_TEMPLATE,
        input_variables=["selectedProjectId", "query"],
    )
    llm = LLMFactory.getDefaultOPENAI()
    # 使用新版输出解析器
    chain = prompt | llm | JsonOutputParser()

    # 调用链处理用户最新输入
    chain_response = chain.invoke({
        "selectedProjectId": form.get("selectedProject").get("id"),
        "query": form.query,
    })
    print(chain_response)

    return state.copy(update={"task_result": "research_task 处理完成", "is_signed": True})