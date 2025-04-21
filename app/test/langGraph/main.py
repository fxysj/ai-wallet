from langgraph.graph import END, StateGraph
from langchain.chat_models import ChatOpenAI
from langchain.schema import SystemMessage
from langchain.tools import tool
from tools.huggingface_tool import analyze_sentiment_batch
from tools.translate_tool import detect_and_translate_to_english
from tools.versioning import save_user_version, compare_versions

# 📁 State structure
class AgentState(dict):
    pass

# 🔧 Tools
@tool
def sentiment_analysis_tool(comments: list[str]) -> dict:
    return analyze_sentiment_batch(comments)

@tool
def translate_and_unify_language(comments: list[str]) -> list[str]:
    return [detect_and_translate_to_english(text) for text in comments]

@tool
def save_data_version(user_id: str, comments: list[str]) -> str:
    return save_user_version(user_id, comments)

@tool
def compare_with_previous_version(user_id: str, new_comments: list[str]) -> dict:
    return compare_versions(user_id, new_comments)

# 📈 LangChain LLM
llm = ChatOpenAI(temperature=0, model="gpt-4")

# 🔍 Node: Sense user input

def sense_input(state: AgentState) -> AgentState:
    return {**state, "comments": state.get("comments", []), "user_id": state.get("user_id")}

# 🔧 Node: Language normalization

def normalize_language(state: AgentState) -> AgentState:
    translated = translate_and_unify_language(state["comments"])
    return {**state, "normalized_comments": translated}

# 🧩 Node: Save version

def save_version(state: AgentState) -> AgentState:
    ver_id = save_data_version(state["user_id"], state["normalized_comments"])
    return {**state, "version_id": ver_id}

# 🧰 Node: Sentiment analysis

def run_sentiment_analysis(state: AgentState) -> AgentState:
    result = sentiment_analysis_tool(state["normalized_comments"])
    return {**state, "analysis_result": result}

# 🌐 Node: Compare versions

def compare_versions_node(state: AgentState) -> AgentState:
    compare_result = compare_with_previous_version(state["user_id"], state["normalized_comments"])
    return {**state, "compare_result": compare_result}

# ⚖️ Node: Evaluate target match

def evaluate_result(state: AgentState) -> str:
    ratio = state["analysis_result"].get("positive_ratio", 0)
    return "output_success" if ratio >= 0.9 else "suggest_improve"

# 📊 Node: Output success

def output_success(state: AgentState) -> AgentState:
    return {**state, "final_result": "分析成功，情绪正面率达标 ✅"}

# 💭 Node: Suggest improvement

def suggest_improve(state: AgentState) -> AgentState:
    improve_system_prompt = """
    # 目标
    分析评论情绪后，正面反馈比例不足 90%。请提供有针对性的优化建议，帮助用户提升评论的正面率。

    # 分析结果
    {result}

    # 要求
    - 提供三条明确建议
    - 每条建议简明扼要
    - 使用积极语言表达

    # 输出格式
    1. ...
    2. ...
    3. ...
    """.format(result=state["analysis_result"])

    msg = SystemMessage(content=improve_system_prompt)
    improvement = llm([msg]).content
    return {**state, "final_result": improvement}

# 🌐 Build Graph
builder = StateGraph(AgentState)

builder.add_node("sense_input", sense_input)
builder.add_node("normalize_language", normalize_language)
builder.add_node("save_version", save_version)
builder.add_node("analyze_sentiment", run_sentiment_analysis)
builder.add_node("compare_versions", compare_versions_node)
builder.add_node("output_success", output_success)
builder.add_node("suggest_improve", suggest_improve)

builder.add_conditional_edges(
    "evaluate_result", evaluate_result,
    {
        "output_success": "output_success",
        "suggest_improve": "suggest_improve"
    }
)

builder.set_entry_point("sense_input")
builder.add_edge("sense_input", "normalize_language")
builder.add_edge("normalize_language", "save_version")
builder.add_edge("save_version", "analyze_sentiment")
builder.add_edge("analyze_sentiment", "compare_versions")
builder.add_edge("compare_versions", "evaluate_result")
builder.add_edge("output_success", END)
builder.add_edge("suggest_improve", END)

graph = builder.compile()

# 👍 API function for FastAPI

def run_sentiment_loop(comments: list[str], user_id: str) -> dict:
    result = graph.invoke({"comments": comments, "user_id": user_id})
    return result
