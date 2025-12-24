# %% 5-12 个性化推荐
from langgraph.graph import StateGraph, START, END, MessagesState
from langgraph.store.memory import InMemoryStore
from langgraph.store.base import BaseStore
from langchain_core.runnables import RunnableConfig
from langchain_openai import ChatOpenAI
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate
import json

recommendation_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "你是一个乐于助人的推荐引擎。根据用户资料提供个性化的产品推荐。"),
        ("human", "{user_profile_summary}"),
    ]
)

recommendation_chain = (
    recommendation_prompt
    | ChatOpenAI(model="Qwen/Qwen2.5-7B-Instruct")
    | (lambda x: {"messages": [AIMessage(content=x.content)]})
)


def recommend_products_node(
    state: MessagesState, config: RunnableConfig, store: BaseStore
):
    user_id = config["configurable"]["user_id"]  # type: ignore
    namespace = ("user_profiles", user_id)
    user_profile_record = store.get(namespace, "profile")
    user_profile = user_profile_record.value if user_profile_record else {}
    user_profile_summary = format_user_profile_summary(user_profile)
    result = recommendation_chain.invoke({"user_profile_summary": user_profile_summary})
    return result


def format_user_profile_summary(user_profile: dict) -> str:
    name = user_profile.get("preferred_name", "用户")
    categories = ", ".join(user_profile.get("preferred_product_categories", ["产品"]))
    return f"用户名:{name}。他偏好的产品类型是：{categories}"


def update_user_profile_node(
    state: MessagesState, config: RunnableConfig, store: BaseStore
):
    user_id = config.get("configurable").get("user_id")  # type: ignore
    namespace = ("user_profiles", user_id)
    user_profile_record = store.get(namespace, "profile")  # type: ignore
    user_profile = user_profile_record.value if user_profile_record else {}
    preference_updates = extract_preference_updates(state)
    updated_profile = user_profile.copy()
    if "preferred_product_categories" in preference_updates:
        updated_profile["preferred_product_categories"] = list(
            set(
                updated_profile.get("preferred_product_categories", [])
                + preference_updates["preferred_product_categories"]
            )
        )
    store.put(namespace, "profile", updated_profile)  # type: ignore
    return {}


def extract_preference_updates(state: MessagesState) -> dict:
    lastest_message_content = state["messages"][-2].content
    extraction_prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "从用户消息中提取产品类别偏好。以dict形式返回，外层不要包裹'''json''',"
                "键为'preferred_product_categories,值为类别list'。如果没有表达偏好，则"
                "返回一个空字典。",
            ),
            ("human", "{user_message}"),
        ]
    )

    extraction_chain = extraction_prompt | ChatOpenAI(model="Qwen/Qwen2.5-7B-Instruct")
    preferences_json = extraction_chain.invoke(
        {"user_message": lastest_message_content}
    )
    try:
        preferences = json.loads(preferences_json.content.replace("'", '"'))  # type: ignore
        return preferences
    except json.JSONDecodeError:
        return {}


# 初始化用户profile
store = InMemoryStore()
user_id = "user_123"
store.put(
    ("user_profiles", user_id),
    "profile",
    {
        "preferred_name": "张三",
        "preferred_product_categories": ["电子产品", "书籍"],
    },
)


graph = StateGraph(MessagesState)
graph.add_node(recommend_products_node)
graph.add_node(update_user_profile_node)
graph.set_entry_point(recommend_products_node.__name__)
graph.add_edge(recommend_products_node.__name__, update_user_profile_node.__name__)
graph.set_finish_point(update_user_profile_node.__name__)
agent = graph.compile(store=store)


# %% 执行图：第一次交互
config = {"configurable": {"user_id": user_id}}
result = agent.invoke({"messages": [HumanMessage(content="你好")]}, config)  # type: ignore

print("初始推荐:")
print(result["messages"][-1].content)
print("=" * 50)

# %% 模拟用户表达新的偏好
user_message = "我最近对运动，尤其是跑步很感兴趣"
result2 = agent.invoke(
    {"messages": result["messages"] + [HumanMessage(content=user_message)]},
    config=config,  # type: ignore
)

result2

# %% 检查更新后的用户资料
updated_profile = store.get(("user_profiles", user_id), "profile").value  # type: ignore
updated_profile
# {'preferred_name': '张三', 'preferred_product_categories': ['电子产品', '书籍']}

print("更新后的用户资料")
print(json.dumps(updated_profile, ensure_ascii=False, indent=2))

print("=" * 50)
# 更新后的用户资料
# {
#   "preferred_name": "张三",
#   "preferred_product_categories": [
#     "书籍",
#     "电子产品",
#     "运动",
#     "跑步"
#   ]
# }
# ==================================================

# %% 再次获取推荐，应该包含新的偏好
result3 = agent.invoke({"messages": [HumanMessage(content="我又来了")]}, config)  # type: ignore
print("更新后资料的推荐")
print(result3["messages"][-1].content)
# 更新后资料的推荐
# 根据您的用户资料“张三”，偏好包括书籍、电子产品、运动和跑步，以下是针对这些偏好的个性化产品推荐：

# ### 书籍
# 1. **《跑步者饮食计划》** - 跑步爱好者常常希望以健康的方式维持与提升他们的运动表现，这本书从节食的理论基础、营养素介绍、运动前后的饮食建议，以及特殊场合的饮食安排时时谈到，非常适合张三查知营养信息。
# 2. **《跑步者的心理机能》** - 包括跑步对心理的积极影响、如何建立跑步的忠诚度等，这本书能帮助跑步者更好地理解透过跑步提升身心健康的重要性。
# 3. **《跑步者健身手册》** - 涵盖跑步技巧、姿势跑步、安全注意事项、跑步中的医疗知识以及如何取得未曾想过的进步，对于希望探讨和提升跑步技能的张三来说，这本书是个完美的推荐。

# ### 电子产品
# 1. **智能手表** - 如果对音乐有丰富的需求，带有音乐存储功能的智能手表可以让张三直接在手表上播放音乐，进行跑步等运动更轻松，且不必担心电量问题。
# 2. **便携式蓝牙耳机** - 即使是最出色的跑步者也偶尔需要更长的佩戴时间，或者需要额外的音量来掩盖周围的声音，好的舒适度和可靠的音质在跑步中是非常重要的，就可以满足这样的需求。
# 3. **携手机器人跑步伴侣APP** - 二合一即智能手环，能够捕捉到一步一步的数据，进行训练和恢复，为您提供个性化指南与建议。

# ### 运动相关
# 1. **运动服、运动鞋** - 挑选适合跑步和健身的高质量运动服和运动鞋不仅能让用户更舒适，还能提高运动效果。
# 2. **跑步服** - 材料透气、轻便，设计能够适应各种运动情境，保持通风防止出汗。
# 3. **跑步面罩** - 防止汗水流进眼睛，让跑步体验更加舒适。
# 4. **评议智能跑步机** - 提供多种训练模式，可以模拟真实的跑步路线，适合室内使用，也能帮助张三监测跑步数据。

# ### 跑步
# 1. **跑步GPS追踪器** - 集成的GPS可以实时追踪跑步路线，记录轨迹，帮助了解跑步路线和效率。
# 2. **定制的跑步训练计划** - 根据张三的身体状态、健身水平和目标定制详细的训练计划，使每一程跑步都朝向更近的达到目标。
# 3. **跑步社区和社交网络** - 加入到社区可以与其他跑步爱好者分享经验、心得和乐趣，可以相互激励。
# 4. **跑步服装套装** - 包括汗水吸水的运动长裤/短裤，吸汗版运动衫等，帮助跑步时保持凉爽不冷不热。

# 以上产品更适合张三的个性偏好。希望这些建议能够帮助张三找到恰到好处的产品。


# %% 多步骤的情景化任务


def extract_departure_city_from_message(content): ...
def extract_arrival_city_from_message(content): ...
def book_flight_api(departure_city, arrival_city): ...
def format_flight_confirmation(flight_details): ...


def book_flight_node(state: MessagesState, config: RunnableConfig):
    task_state = state.get("flight_booking_state", {})
    if not task_state.get("departure_city"):
        response = agent.invoke(
            state["messages"] + [HumanMessage(content="你想从哪里出发?")]  # type: ignore
        )
        return {
            "messages": response,
            "flight_booking_state": {"departure_city": "pending"},
        }

    if task_state.get("departure_city") == "pending" and not task_state.get(
        "arrival_city"
    ):
        departure_city = extract_departure_city_from_message(
            state["messages"][-1].content
        )
        if departure_city:
            response = agent.invoke(
                [HumanMessage(content=f"您要从{departure_city}飞往哪里?")]
                + state["messages"]  # pyright: ignore[reportArgumentType]
            )
            return {
                "messages": response,
                "flight_booking_state": {
                    "departure_city": departure_city,
                    "arrival_city": "pending",
                },
            }
        else:
            response = agent.invoke(
                [
                    HumanMessage(
                        content="抱歉，我没有听清您的出发城市。您可以换一种说法吗?"
                    )
                ]
                + state["messages"]  # pyright: ignore[reportArgumentType]
            )
            return {"messages": response}

    if task_state.get("arrival_city") == "pending":
        arrival_city = extract_arrival_city_from_message(state["messages"][-1].content)
        if arrival_city:
            flight_details = book_flight_api(
                departure_city=task_state["departure_city"], arrival_city=arrival_city
            )
            confirmation_message = format_flight_confirmation(flight_details)
            response = agent.invoke(
                [HumanMessage(content=confirmation_message)] + state["messages"]  # pyright: ignore[reportArgumentType]
            ) tate": {}}
        else:
            response = agent.invoke(
                [
                    HumanMessage(
                        content="抱歉，我没有听清您的出发城市。您可以换一种说法吗?"
                    )
                ]
                + state["messages"]  # pyright: ignore[reportArgumentType]
            )
            return {"messages": response}

    response = agent.invoke(
        [HumanMessage(content="让我们为您预定航班，您要从哪里起飞？")]
        + state["messages"]  # type: ignore
    )
    return {"messages": response, "flight_booking_state": {"departure_city": "pending"}}


graph = StateGraph(MessagesState)
graph.add_node(book_flight_node)
graph.set_entry_point(book_flight_node.__name__)
# graph的其余部分


# %% 构建一个TrustCall可用的数据结构
from pydantic import BaseModel, Field


class UserPersona(BaseModel):
    user_name: str = Field(description="用户的首选姓名")
    interests: list[str] = Field(description="用户兴趣列表")

