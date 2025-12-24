# %%
from langgraph.graph import START, END, StateGraph
from typing import TypedDict, Annotated
import asyncio
import operator


class MyState(TypedDict):
    value: int
    history: Annotated[list, operator.add]
    number: int


def add_num_node(state: MyState) -> MyState:
    return {
        "value": state.get("value") + state.get("number"),
        "history": [state.get("value") + state.get("number")],  # type: ignore
    }


def double_node(state: MyState) -> MyState:
    return {
        "value": state.get("value") * 2,
        "history": [state.get("value") * 2],  # type: ignore
    }


def should_continue_route(state: MyState) -> str:
    if state.get("value") < 100:
        return add_num_node.__name__
    return END


# build a graph
graph = StateGraph(MyState)
graph.add_node(add_num_node)
graph.add_node(double_node)
graph.add_edge(START, add_num_node.__name__)
graph.add_edge(add_num_node.__name__, double_node.__name__)
graph.add_conditional_edges(double_node.__name__, should_continue_route)
agent = graph.compile()


async def main():
    input = {"value": 1, "history": [], "number": 10}
    async for event in agent.astream_events(input, version="v1"):
        print(f"{event['event']}-{event['name']}-{event['data']}")


asyncio.run(main())

# on_chain_start-LangGraph-{'input': {'value': 1, 'history': [], 'number': 10}}
# on_chain_start-add_num_node-{'input': {'value': 1, 'history': [], 'number': 10}}
# on_chain_stream-add_num_node-{'chunk': {'value': 11, 'history': [11]}}
# on_chain_end-add_num_node-{'input': {'value': 1, 'history': [], 'number': 10}, 'output': {'value': 11, 'history': [11]}}
# on_chain_stream-LangGraph-{'chunk': {'add_num_node': {'value': 11, 'history': [11]}}}
# on_chain_start-double_node-{'input': {'value': 11, 'history': [11], 'number': 10}}
# on_chain_stream-double_node-{'chunk': {'value': 22, 'history': [22]}}
# on_chain_end-double_node-{'input': {'value': 11, 'history': [11], 'number': 10}, 'output': {'value': 22, 'history': [22]}}
# on_chain_stream-LangGraph-{'chunk': {'double_node': {'value': 22, 'history': [22]}}}
# on_chain_end-LangGraph-{'output': {'double_node': {'value': 22, 'history': [22]}}}

# %%
from langgraph.graph import START, END, StateGraph
from typing import TypedDict, Annotated
import asyncio
import operator


class MyState(TypedDict):
    value: int
    history: Annotated[list, operator.add]
    number: int


def add_num_node(state: MyState) -> MyState:
    return {
        "value": state.get("value") + state.get("number"),
        "history": [state.get("value") + state.get("number")],  # type: ignore
    }


def double_node(state: MyState) -> MyState:
    return {
        "value": state.get("value") * 2,
        "history": [state.get("value") * 2],  # type: ignore
    }


def should_continue_route(state: MyState) -> str:
    if state.get("value") < 100:
        return add_num_node.__name__
    return END


# build a graph
graph = StateGraph(MyState)
graph.add_node(add_num_node)
graph.add_node(double_node)
graph.add_edge(START, add_num_node.__name__)
graph.add_edge(add_num_node.__name__, double_node.__name__)
graph.add_conditional_edges(double_node.__name__, should_continue_route)
agent = graph.compile()


async def main():
    input = {"value": 1, "history": [], "number": 10}
    async for event in agent.astream_events(input, version="v1"):
        print(f"{event['event']}-{event['name']}-{event['data']}")


asyncio.run(main())

# build a graph
graph = StateGraph(MyState)
graph.add_node(add_num_node)
graph.add_node(double_node)
graph.add_edge(START, add_num_node.__name__)
graph.add_edge(add_num_node.__name__, double_node.__name__)
graph.add_conditional_edges(double_node.__name__, should_continue_route)
agent = graph.compile()


# on_chain_start-LangGraph-{'input': {'value': 1, 'history': [], 'number': 10}}
# on_chain_start-add_num_node-{'input': {'value': 1, 'history': [], 'number': 10}}
# on_chain_stream-add_num_node-{'chunk': {'value': 11, 'history': [11]}}
# on_chain_end-add_num_node-{'input': {'value': 1, 'history': [], 'number': 10}, 'output': {'value': 11, 'history': [11]}}
# on_chain_stream-LangGraph-{'chunk': {'add_num_node': {'value': 11, 'history': [11]}}}
# on_chain_start-double_node-{'input': {'value': 11, 'history': [11], 'number': 10}}
# on_chain_start-should_continue_route-{'input': {'value': 22, 'history': [11, 22], 'number': 10}}
# on_chain_end-should_continue_route-{'input': {'value': 22, 'history': [11, 22], 'number': 10}, 'output': 'add_num_node'}
# on_chain_stream-double_node-{'chunk': {'value': 22, 'history': [22]}}
# on_chain_end-double_node-{'input': {'value': 11, 'history': [11], 'number': 10}, 'output': {'value': 22, 'history': [22]}}
# on_chain_stream-LangGraph-{'chunk': {'double_node': {'value': 22, 'history': [22]}}}
# on_chain_start-add_num_node-{'input': {'value': 22, 'history': [11, 22], 'number': 10}}
# on_chain_stream-add_num_node-{'chunk': {'value': 32, 'history': [32]}}
# on_chain_end-add_num_node-{'input': {'value': 22, 'history': [11, 22], 'number': 10}, 'output': {'value': 32, 'history': [32]}}
# on_chain_stream-LangGraph-{'chunk': {'add_num_node': {'value': 32, 'history': [32]}}}
# on_chain_start-double_node-{'input': {'value': 32, 'history': [11, 22, 32], 'number': 10}}
# on_chain_start-should_continue_route-{'input': {'value': 64, 'history': [11, 22, 32, 64], 'number': 10}}
# on_chain_end-should_continue_route-{'input': {'value': 64, 'history': [11, 22, 32, 64], 'number': 10}, 'output': 'add_num_node'}
# on_chain_stream-double_node-{'chunk': {'value': 64, 'history': [64]}}
# on_chain_end-double_node-{'input': {'value': 32, 'history': [11, 22, 32], 'number': 10}, 'output': {'value': 64, 'history': [64]}}
# on_chain_stream-LangGraph-{'chunk': {'double_node': {'value': 64, 'history': [64]}}}
# on_chain_start-add_num_node-{'input': {'value': 64, 'history': [11, 22, 32, 64], 'number': 10}}
# on_chain_stream-add_num_node-{'chunk': {'value': 74, 'history': [74]}}
# on_chain_end-add_num_node-{'input': {'value': 64, 'history': [11, 22, 32, 64], 'number': 10}, 'output': {'value': 74, 'history': [74]}}
# on_chain_stream-LangGraph-{'chunk': {'add_num_node': {'value': 74, 'history': [74]}}}
# on_chain_start-double_node-{'input': {'value': 74, 'history': [11, 22, 32, 64, 74], 'number': 10}}
# on_chain_start-should_continue_route-{'input': {'value': 148, 'history': [11, 22, 32, 64, 74, 148], 'number': 10}}
# on_chain_end-should_continue_route-{'input': {'value': 148, 'history': [11, 22, 32, 64, 74, 148], 'number': 10}, 'output': '__end__'}
# on_chain_stream-double_node-{'chunk': {'value': 148, 'history': [148]}}
# on_chain_end-double_node-{'input': {'value': 74, 'history': [11, 22, 32, 64, 74], 'number': 10}, 'output': {'value': 148, 'history': [148]}}
# on_chain_stream-LangGraph-{'chunk': {'double_node': {'value': 148, 'history': [148]}}}
# on_chain_end-LangGraph-{'output': {'double_node': {'value': 148, 'history': [148]}}}

# %% @todo 试试set_entry_point+set_finish_point
from langgraph.graph import START, END, StateGraph
from typing import TypedDict, Annotated
import asyncio
import operator


class MyState(TypedDict):
    value: int
    history: Annotated[list, operator.add]
    number: int


def add_num_node(state: MyState) -> MyState:
    return {
        "value": state.get("value") + state.get("number"),
        "history": [state.get("value") + state.get("number")],  # type: ignore
    }


def double_node(state: MyState) -> MyState:
    return {
        "value": state.get("value") * 2,
        "history": [state.get("value") * 2],  # type: ignore
    }


def should_continue_route(state: MyState) -> str:
    if state.get("value") < 100:
        return add_num_node.__name__
    return END


# build a graph
graph = StateGraph(MyState)
graph.add_node(add_num_node)
graph.add_node(double_node)
graph.set_entry_point(add_num_node.__name__)
graph.add_edge(add_num_node.__name__, double_node.__name__)
# graph.add_edge(double_node.__name__, END)
graph.set_finish_point(double_node.__name__)
agent = graph.compile()

input = {"value": 1, "history": [], "number": 10}
agent.invoke(input)

"""
可以发现，其实set_finish_point('a_node')在效果是等价add_edge('a_node', END)效果的，
但END得好处在于，可以被动态处理。而set_finish_point则只能固定的。
一般动态处理时，END都被用于作为条件返回的。
"""

# %%
