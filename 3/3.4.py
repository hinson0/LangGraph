# %%3-26 将已编译的子图作为节点的存在，添加到父图中
from typing import TypedDict
from langgraph.graph import StateGraph, MessagesState, START, END

# 查询天气的子图
subgraph = ...


# 定义父图
class ParentState(TypedDict):  # type: ignore
    messages: list


def node_1(state: MessagesState):
    return dict(messages=[""])


builder = StateGraph(ParentState)
builder.add_node(node_1)
builder.add_node("weather_graph", subgraph)  # type: ignore

builder.add_edge(START, "node_1")
builder.add_edge("node_1", "weather_graph")
builder.add_edge("weather_graph", END)


graph = builder.compile()
graph.invoke(...)  # type: ignore

# %% 3-27 使用节点函数适配”子图“和”父图“

child_graph = ...


class ParentState(TypedDict):
    my_key: str


def call_child_graph_node(state: ParentState) -> ParentState:
    child_graph_input = {"my_child_key": state["my_key"]}
    child_graph_output = child_graph.invoke(child_graph_input)  # type: ignore
    return {"my_key": child_graph_output["my_child_key"]}


parentBuilder = StateGraph(ParentState)

parentBuilder.add_node("child", call_child_graph_node)

parentBuilder.add_edge("parent_1", "child")

parentGraph = parentBuilder.compile()
