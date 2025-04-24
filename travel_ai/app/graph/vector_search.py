from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import CharacterTextSplitter
from travel_ai.app.state.user_state import UserState
import os

# 初始化 Chroma 向量库（持久化路径为 ./chroma_db）
CHROMA_DB_PATH = "./chroma_db"
embedding_model = OpenAIEmbeddings()
vectorstore = Chroma(persist_directory=CHROMA_DB_PATH, embedding_function=embedding_model)


def search_vector(state: UserState):
    user_id = state.user_id
    user_input = state.user_input
    search_query = user_id + ":" + user_input

    # 使用返回分数的搜索方法
    results = vectorstore.similarity_search_with_score(search_query, k=3)

    if results:
        # results 是 (Document, score) 的元组列表
        sorted_results = sorted(results, key=lambda x: x[1], reverse=False)  # 分数越低越相似
        top_result = sorted_results[0][0].page_content
        return {"retrieved": top_result}
    else:
        return {"retrieved": None}


# 统一文本拼接 + 分割后存入向量库
def save_vector(state: UserState):
    user_id = state.user_id
    user_input = state.user_input

    # 构建带标签的长文档内容
    content = f"""
👤 用户 ID: {user_id}
💬 用户输入: {user_input}
🔑 抽取关键词: {state.keywords}
🧠 用户性格画像: {state.persona}

🧭 旅游推荐行程:
{state.plan}

🏨 酒店推荐:
{state.hotels}

✈️ 航班推荐:
{state.flights}

📍 打卡地图信息:
{state.map}

🌈 高情商可爱旅游攻略汇总:
{state.cute_summary}
""".strip()

    # 文本分割器配置：每段最大 1000 字符，无重叠
    splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)

    # 将长文本分割为多个文档块，每块作为独立的向量输入
    documents = splitter.create_documents([content], metadatas=[{"user_id": user_id}])

    # 添加分割后的文档块到向量数据库
    vectorstore.add_documents(documents=documents)

   # ✅ 无需 persist()，Chroma 自动持久化
