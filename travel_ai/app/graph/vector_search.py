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
    search = user_id + ":" + user_input
    result = vectorstore.similarity_search(search, k=1)
    if result:
        return {"retrieved": result[0].page_content}
    else:
        return {"retrieved": None}


# 统一文本拼接 + 分割后存入向量库
def save_vector(state: UserState):
    user_id = state.user_id
    user_input = state.user_input

    # 拼接完整文档内容
    content = f"""
用户 ID: {user_id}
用户输入: {user_input}
关键词: {state.keywords}
用户性格: {state.persona}

🧭 推荐行程:
{state.plan}

🏨 推荐酒店:
{state.hotels}

✈️ 推荐航班:
{state.flights}

📍 打卡地图:
{state.map}

🌈 可爱旅游攻略汇总:
{state.cute_summary}
"""

    # 文本分割器（最多3000字符）
    splitter = CharacterTextSplitter(chunk_size=3000, chunk_overlap=100)
    docs = splitter.create_documents([content])

    # 添加到 Chroma
    vectorstore.add_documents(documents=docs)

   # ✅ 无需 persist()，Chroma 自动持久化
