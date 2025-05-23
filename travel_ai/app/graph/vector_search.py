from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from travel_ai.app.state.user_state import UserState
from travel_ai.app.config import llm
# 初始化 Chroma 向量库（持久化路径为 ./chroma_db）
CHROMA_DB_PATH = "./chroma_db"
embedding_model = OpenAIEmbeddings()
vectorstore = Chroma(persist_directory=CHROMA_DB_PATH, embedding_function=embedding_model,collection_name="rag_travel")


def search_vector(state: UserState):
    user_id = state.user_id
    user_input = state.user_input
    search_query = user_input

    print("search_query :"+search_query)

    # 使用返回分数的搜索方法
    results = vectorstore.similarity_search_with_score(search_query, k=1,filter={"user_id":user_id})
    print(results)
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

if __name__ == '__main__':
    # 👤 创建用户状态并填入数据
    state = UserState(
        user_id="123",
        user_input="我想去三亚旅游5天",
        keywords="三亚,旅游",
        persona="喜欢海边，喜欢晒太阳",
        plan={"day1": "到达三亚，入住酒店", "day2": "亚龙湾一日游"},
        hotels={"name": "三亚湾红树林", "rating": 4.5},
        flights={"flight_number": "CA123", "from": "北京", "to": "三亚"},
        map={"spots": ["天涯海角", "亚龙湾", "南山寺"]},
        cute_summary={"tips": "多带防晒霜哦，三亚很晒！"}
    )

    # ✅ 先保存
    save_vector(state)

    state= UserState(
        user_input="我想去三亚旅游5天",
        user_id="123"
    )
    resource= search_vector(state)
    print(resource)
