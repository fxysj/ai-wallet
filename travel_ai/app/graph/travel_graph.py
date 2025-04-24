from langgraph.graph import StateGraph, END

from travel_ai.app.chains.extractFillMainTitleTopic import ExtractFillMainTitleTopic
from travel_ai.app.chains.extract_keywords import ExtractKeywordChain
from travel_ai.app.chains.finsih_check import ReviewSummaryChain
from travel_ai.app.chains.travel_planner import TravelPlannerChain
from travel_ai.app.chains.hotel_recommender import HotelRecommenderChain
from travel_ai.app.chains.flight_recommender import FlightRecommenderChain
from travel_ai.app.chains.map_generator import MapGeneratorChain
from travel_ai.app.graph.interrupt_handler_graph import interrupt_subgraph
from travel_ai.app.graph.vector_search import search_vector, save_vector
from travel_ai.app.state.user_state import UserState, check_interrupt, check_interrupt_route


def extract_keywords(state: UserState):
    keywords = ExtractKeywordChain.invoke({"user_input": state.user_input})
    return {"keywords": keywords}


def plan_trip(state: UserState):
    plan = TravelPlannerChain.invoke({"keywords": state.keywords,
                                      "persona": state.persona,
                                      "context": state.retrieved
                                      })
    return {"plan": plan}


def recommend_hotel(state: UserState):
    return {"hotels": HotelRecommenderChain.invoke({
        "keywords": state.keywords,
        "persona": state.persona,
        "context": state.retrieved
    })}


def recommend_flight(state: UserState):
    return {"flights": FlightRecommenderChain.invoke({"keywords": state.keywords, "context": state.retrieved})}


def generate_map(state: UserState):
    return {"map": MapGeneratorChain.invoke({
        "keywords": state.keywords,
        "persona": state.persona,
        "context": state.retrieved
    })}


# 对关键词进行丰富为主题内容扩展
def extract_filltopic(state: UserState):
    filkKeyWords = ExtractFillMainTitleTopic.invoke({
        "keywords": state.keywords,
    })
    return {"keywords": filkKeyWords}


def review_and_summary(state: UserState):
    # 这里需要将结果和数据保存到向量数据库中
    # 如果没有向量库命中，则保存
    if not state.retrieved:
        save_vector(state)
    return {
        "cute_summary": ReviewSummaryChain.invoke({
            "keywords": state.keywords,
            "persona": state.persona,
            "plan": state.plan,
            "hotels": state.hotels,
            "flights": state.flights,
            "map": state.map
        })
    }
def search_chrom_db(state:UserState):
    res = search_vector(state)
    print("search_Res:")
    print(res)
    return res

# 构建 LangGraph 流程图
graph = StateGraph(UserState)
graph.set_entry_point("extract_keywords")

# 流程如下 对用户关键词+用户的上下文信息+用户的情感信息
# 进行采集出用户的旅游目的确定
# 进行用户关键词补充更加完善
# user_id:topic信息从Chrom去查询 如果没有则下面的所有步骤则需要根据自己的理解生成
# 最后一步需要对上面的所有的信息进行汇总 进行总结生成出一个合理的信息
# 内容过滤 内容检测 内容修正
graph.add_node("extract_keywords", extract_keywords)
graph.add_node("extractFillMainTitleTopic", extract_filltopic)
graph.add_node("plan_trip", plan_trip)
graph.add_node("recommend_hotel", recommend_hotel)
graph.add_node("recommend_flight", recommend_flight)
graph.add_node("generate_map", generate_map)
graph.add_node("vector_search", search_chrom_db)
graph.add_node("review_and_summary", review_and_summary)
graph.add_node("check_interrupt", check_interrupt)
# 把中断子图注册为一个节点名，比如 interrupt_handler
graph.add_node("interrupt_handler", interrupt_subgraph)





graph.add_edge("extract_keywords", "extractFillMainTitleTopic")
graph.add_edge("extractFillMainTitleTopic", "vector_search")
graph.add_edge("vector_search", "check_interrupt")
graph.add_edge("plan_trip", "recommend_hotel")
graph.add_edge("recommend_hotel", "recommend_flight")
graph.add_edge("recommend_flight", "generate_map")
graph.add_edge("generate_map", "review_and_summary")
graph.add_edge("review_and_summary", END)


graph.add_conditional_edges(
    "check_interrupt",
    check_interrupt_route,
    path_map={
        "interrupt": "interrupt_handler",  # ✅ 是注册过的节点名
        "continue": "plan_trip",           # ✅ 也是主图的节点名
    }
)
# ✅ 让子图输出自动回到 plan_trip
graph.add_edge("interrupt_handler", "plan_trip")

graph.set_entry_point("extract_keywords")

travel_graph = graph.compile()
