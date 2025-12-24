# %%3-20 map阶段的分割节点
from langgraph.types import Send
from typing import TypedDict, List


class OverallState(TypedDict):
    large_input_data: str
    subjects: List[str]


def split_large_data(input_data, num_sub_stasks):
    return []


def split_input_data_node(state: OverallState):
    input_data = state["large_input_data"]
    sub_datasets = split_large_data(input_data, num_sub_stasks=10)
    send_list = []
    for sub_dataset in sub_datasets:
        send_list.append(Send("map_node", {"sub_data": sub_dataset}))
    return send_list


# %% 3-21 map阶段的映射节点
from typing import Any  # noqa: E402


class MapState(TypedDict):
    sub_data: Any


def precess_sub_data(sub_data):
    raise NotImplementedError


def map_node(state: MapState):
    sub_data = state["sub_data"]
    intermediate_results = precess_sub_data(sub_data)
    return {"intermediate_results": intermediate_results}


# %% 3-22 reduce阶段的规约节点
from typing import Annotated  # noqa: E402
import operator  # noqa: E402


class ReduceState(TypedDict):
    intermediate_results: Annotated[list, operator.add]


def aggregate_results(intermediate_results):
    raise NotImplementedError


def reduce_node(state: ReduceState):
    intermediate_results = state["intermediate_results"]
    final_results = aggregate_results(intermediate_results)
    return dict(final_results=final_results)


# %% 3-23 分割节点 -> 映射节点的连接代码

from langgraph.graph import StateGraph, MessagesState, START, END  # noqa: E402


class State(MessagesState):
    aggregate: str
    llm_response: str


builder = StateGraph(State)

builder.add_edge(START, "split_input_data_node")
builder.add_conditional_edges("split_node", split_input_data_node, ["map_node"])

# %% 3-24 映射节点到归约节点的边连接代码
builder.add_edge("map_node", "reduce_node")
builder.add_edge("reduce_node", END)


# %% 3-25 send()函数的基本用法


def generate_jokes_node(state: State):
    return dict(messages=[""])


def continue_to_jokes(state: OverallState):
    # some codes
    send_list = [
        Send("generate_jokes_node", dict(subject=s)) for s in state["subjects"]
    ]
    return send_list
