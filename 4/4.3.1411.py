# %%
from langgraph.types import interrupt, Command
from typing import TypedDict, Annotated
from langgraph.graph import StateGraph
from langgraph.checkpoint.memory import MemorySaver
import operator


class MyState(TypedDict):  # type: ignore
    value: int
    history: Annotated[list, operator.add]


def add_one_node(state: MyState):
    return {"value": state["value"] + 1, "history": [state["value"] + 1]}


def add_two_node(state: MyState):
    return {"value": state["value"] + 2, "history": [state["value"] + 2]}


def double_node(state: MyState):
    return {"value": state["value"] * 2, "history": [state["value"] * 2]}


def human_editing_node(state: MyState):
    approval_request = interrupt(
        {"desc": "审阅下当前的值", "current_value": state.get("value")}
    )
    new_value = approval_request.get("new_value")
    return Command(
        update={"value": new_value + state["value"]}, goto=double_node.__name__
    )


graph = StateGraph(MyState)
graph.add_node(add_one_node)
graph.add_node(add_two_node)
graph.add_node(double_node)
graph.add_node(human_editing_node)

graph.set_entry_point(add_one_node.__name__)
graph.add_edge(add_one_node.__name__, add_two_node.__name__)
graph.add_edge(add_two_node.__name__, human_editing_node.__name__)
graph.set_finish_point(double_node.__name__)

agent = graph.compile(checkpointer=MemorySaver())
config = {"configurable": {"thread_id": "thread_id_1"}}

agent.invoke({"value": 1}, config=config)  # type: ignore


# %% 在这里得到用户输入的10，然后恢复图执行
agent.invoke(Command(resume={"new_value": 10}), config)  # type: ignore


# %% ??? 上一次编辑的位置 @todo


# %% 正确使用存档点来编译图
agent = graph.compile(checkpointer=MemoryError())  # type: ignore
"""
没有使用checkpointer，interrupt()是无法工作的
"""

# %% 必须使用同一个thread_config，才能正确的恢复


def user_location_node(state): ...


thread_config = {}

agent.invoke(Command(resume=user_location_node), config=thread_config)

# %%
