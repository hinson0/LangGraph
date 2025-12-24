from typing import Any, TypedDict
from langgraph.graph import StateGraph, MessagesState, START, END


# define a state constructor
class State(MessagesState):
    aggregate: str
    llm_response: str


builder = StateGraph(State)


class ReturnNodeValue:
    def __init__(self, node_secret: str) -> None:
        self._value = node_secret

    def __call__(self, state: State) -> Any:
        print(f"Adding {self._value} to {state['aggregate']}")
        return {"aggregate": [self._value]}


builder.add_node("a", ReturnNodeValue("i am a"))
builder.add_node("b", ReturnNodeValue("i am b"))
builder.add_node("c", ReturnNodeValue("i am c"))
builder.add_node("d", ReturnNodeValue("i am d"))

builder.add_edge(START, "a")
builder.add_edge("a", "b")
builder.add_edge("a", "c")
builder.add_edge("b", "d")
builder.add_edge("c", "d")
builder.add_edge("d", END)

graph = builder.compile()


# %% 3-19 递归限制是对并行分支流程的限制

import operator
from typing import Annotated, TypedDict, Any
from langgraph.graph import StateGraph, START, END
from langgraph.errors import GraphRecursionError


class State(TypedDict):
    aggregate: Annotated[list, operator.add]


def a_node(state):
    return {"aggregate": ["a"]}


def b_node(state):
    return {"aggregate": ["b"]}


def c_node(state):
    return {"aggregate": ["c"]}


def d_node(state):
    return {"aggregate": ["d"]}


builder = StateGraph(State)
builder.add_node(a_node)
builder.add_node(b_node)
builder.add_node(c_node)
builder.add_node(d_node)

builder.add_edge(START, "a_node")
builder.add_edge("a_node", "b_node")
builder.add_edge("a_node", "c_node")
builder.add_edge("b_node", "d_node")
builder.add_edge("c_node", "d_node")
builder.add_edge("d_node", END)
graph = builder.compile()

try:
    graph.invoke({"aggregate": []}, {"recursion_limit": 2})
except GraphRecursionError as e:
    print(e)


# %%
from langgraph.graph import StateGraph, END
from langgraph.types import TypedGraph


# 1. 定义状态结构：存储步骤计数和触发循环的标记
class MyState(State):
    step_count: int  # 记录工作流执行的步骤数
    loop: bool = True  # 控制是否触发循环


# 2. 定义节点函数
def node_a(state: MyState) -> MyState:
    """节点A：计数+1，返回状态"""
    state.step_count += 1
    print(f"执行节点A，当前步骤数：{state.step_count}")
    return state


def node_b(state: MyState) -> MyState:
    """节点B：计数+1，返回状态"""
    state.step_count += 1
    print(f"执行节点B，当前步骤数：{state.step_count}")
    return state


# 3. 定义分支逻辑：控制是否循环（节点A→节点B→节点A...）
def should_loop(state: MyState) -> str:
    """返回下一个节点的名称：循环则去node_a，否则结束"""
    if state.loop and state.step_count < 10:  # 理论上会无限循环（step_count会一直增加）
        return "node_a"
    else:
        return END


# 4. 创建工作流图
graph_builder = StateGraph(MyState)
# 添加节点
graph_builder.add_node("node_a", node_a)
graph_builder.add_node("node_b", node_b)
# 设置起始节点
graph_builder.set_entry_point("node_a")
# 添加边：node_a → node_b → 分支判断 → node_a/END
graph_builder.add_edge("node_a", "node_b")
graph_builder.add_conditional_edges("node_b", should_loop)

# 5. 编译工作流：设置默认的递归限制（步骤数上限）
# recursion_limit=5 表示工作流最多执行5个步骤，超过则抛出异常
app = graph_builder.compile(recursion_limit=5)

# 6. 执行工作流（可以在这里覆盖recursion_limit，比如recursion_limit=8）
try:
    input_state = MyState(step_count=0)
    # 调用时如果设置recursion_limit，会覆盖编译时的默认值
    # result = app.invoke(input_state, recursion_limit=8)
    result = app.invoke(input_state)
except Exception as e:
    print(f"\n触发限制异常：{type(e).__name__}: {e}")

# %%
