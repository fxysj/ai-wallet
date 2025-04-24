from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langgraph.graph import StateGraph

from travel_ai.app.state.user_state import UserState
from travel_ai.app.config import llm
interrupt_graph = StateGraph(UserState)

# 示例处理：用 OpenAI 问答链回答临时问题
def handle_interrupt(state: UserState):

    prompt = PromptTemplate.from_template("你是一个旅游小助手，请回答以下问题：{question}")
    qa_chain = prompt | llm |StrOutputParser()

    answer =  qa_chain.invoke({"question": state.interrupt_input})
    print("回答的问题:"+answer)
    return {"interrupt_answer": answer, "interrupt_input": None}  # 清空中断信息，继续主图

interrupt_graph.add_node("handle", handle_interrupt)
interrupt_graph.set_entry_point("handle")
interrupt_graph.set_finish_point("handle")

# ✅ 这一步是关键：compile 得到子图 Runnable
interrupt_subgraph = interrupt_graph.compile()
