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
    return {"plan": plan.get("plan_trip")}


def recommend_hotel(state: UserState):
    return {"hotels": HotelRecommenderChain.invoke({
        "keywords": state.keywords,
        "persona": state.persona,
        "context": state.retrieved
    }).get("recommend_hotel")}


def recommend_flight(state: UserState):
    return {"flights": FlightRecommenderChain.
    invoke({"keywords": state.keywords, "context": state.retrieved}).get("recommend_flight")
            }


def generate_map(state: UserState):
    return {"map": MapGeneratorChain.invoke({
        "keywords": state.keywords,
        "persona": state.persona,
        "context": state.retrieved
    }).get("generate_map")}


# 对关键词进行丰富为主题内容扩展
def extract_filltopic(state: UserState):
    filkKeyWords = ExtractFillMainTitleTopic.invoke({
        "keywords": state.keywords,
    })
    return {"keywords": filkKeyWords}


def review_and_summary(state: UserState):
    # 这里需要将结果和数据保存到向量数据库中
    # 如果没有向量库命中，则保存
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
graph.add_node("extract_filltopic", extract_filltopic)
graph.add_node("vector_search", search_chrom_db)
# 把中断子图注册为一个节点名，比如 interrupt_handler
graph.add_node("interrupt_handler", interrupt_subgraph)
# 添加每一步中断检查节点 + 主任务节点
steps = [
    ("plan_trip", plan_trip),
    ("recommend_hotel", recommend_hotel),
    ("recommend_flight", recommend_flight),
    ("generate_map", generate_map),
    ("review_and_summary", review_and_summary)
]

for step_name, step_fn in steps:
    check_node = f"check_{step_name}"
    graph.add_node(check_node, check_interrupt)
    graph.add_node(step_name, step_fn)

    # 条件跳转：中断 or 继续下一步
    graph.add_conditional_edges(
        check_node,
        check_interrupt_route,
        path_map={
            "interrupt": "interrupt_handler",
            "continue": step_name
        }
    )







# 固定顺序连接逻辑
graph.add_edge("extract_keywords", "extract_filltopic")
graph.add_edge("extract_filltopic", "vector_search")
graph.add_edge("vector_search", "check_plan_trip")
graph.add_edge("plan_trip", "check_recommend_hotel")
graph.add_edge("recommend_hotel", "check_recommend_flight")
graph.add_edge("recommend_flight", "check_generate_map")
graph.add_edge("generate_map", "check_review_and_summary")
graph.add_edge("review_and_summary", END)


# ✅ 让子图输出自动回到 plan_trip
graph.add_edge("interrupt_handler", "plan_trip")

travel_graph = graph.compile()
