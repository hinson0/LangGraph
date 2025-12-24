# %% 3-35 获取Mermaid语法描述

from typing import Annotated, Any

from langchain_core.tools import tool, InjectedToolCallId
from langchain_core.runnables.config import RunnableConfig
from langchain_core.messages import ToolMessage
from langchain.agents import AgentState
from langchain_openai import ChatOpenAI


from langgraph.types import Command
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode

USER_INFO = [
    dict(user_id=1, name="bob dylan", location="new york"),
    dict(user_id=2, name="yangzhibing", location="jiangxi fuzhou"),
]

USER_ID_TO_USER_INFO = {info["user_id"]: info for info in USER_INFO}


class State(AgentState):
    user_info: dict[str, Any]


@tool
def lookup_user_info_tool(
    tool_call_id: Annotated[str, InjectedToolCallId], config: RunnableConfig
):
    """查询用户信息的工具，更好辅助他们获取问题信息"""
    user_id = config.get("configurable", {}).get("user_id")
    if user_id is None:
        raise ValueError("please privode user id")
    if user_id not in USER_ID_TO_USER_INFO:
        raise ValueError(f"user {user_id} not found")
    user_info = USER_ID_TO_USER_INFO[user_id]
    return Command(
        update={
            "user_info": user_info,
            "messages": [
                ToolMessage(
                    "successfully looked up user information", tool_call_id=tool_call_id
                ),
            ],
        },
    )


# 初始化图
graph = StateGraph(State)


# 定义节点
def agent_node(state: State):
    if user_info := state.get("user_info"):
        system_messages = f"you are asssiting {user_info['name']} \
                            who lives in {user_info['location']}"
    else:
        system_messages = "you are a helpful assistant."

    model = ChatOpenAI(model="Qwen/Qwen2.5-7B-Instruct", temperature=0)
    model = model.bind_tools([lookup_user_info_tool])
    response = model.invoke(
        [{"role": "system", "content": system_messages}] + state["messages"]
    )
    return {"messages": [response]}


def should_use_tools_router(state: State):
    last_message = state["messages"][-1]
    return "tools_node" if getattr(last_message, "tool_calls") else END


# def tools_node(state):
#     return ToolNode([lookup_user_info_tool])

# 添加节点
graph.add_node(agent_node)
# graph.add_node(tools_node)
graph.add_node("tools_node", ToolNode([lookup_user_info_tool]))


# 定义边
graph.set_entry_point("agent_node")
graph.add_edge("tools_node", "agent_node")
graph.add_conditional_edges("agent_node", should_use_tools_router)


# 编译
agent = graph.compile()

# 调用
for chunk in agent.stream(
    {"messages": [("human", "今天江西南丰的天气?")]},  # type: ignore
    {"configurable": {"user_id": 1}},
):
    print(chunk)

mermaid_syntax = agent.get_graph().draw_mermaid()
# print(mermaid_syntax)

# %% 3-37 使用系统Chrome浏览器渲染PNG图片

from IPython.display import Image, display
from langchain_core.runnables.graph import MermaidDrawMethod
import os

try:
    # 配置Pyppeteer使用系统Chrome（无需下载新的Chromium）
    os.environ["CHROME_EXECUTABLE_PATH"] = (
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    )

    # 使用Pyppeteer渲染，会自动使用系统Chrome
    png_bytes = agent.get_graph().draw_mermaid_png(
        draw_method=MermaidDrawMethod.PYPPETEER
    )
    display(Image(png_bytes))
except Exception as e:
    print(f"Pyppeteer渲染失败: {e}")
    print("\nMermaid语法:")
    print(mermaid_syntax)


# %% 3.38 使用Mermaid和Pyppeteer库渲染PNG图片

import random
from typing import Annotated, Literal, TypedDict
from langgraph.graph import StateGraph, END, START
from langgraph.graph.message import add_messages


class State(TypedDict):
    messages: Annotated[list, add_messages]


class MyNode:
    def __init__(self, name: str):
        self.name = name

    def __call__(self, state: State):
        return {"messages": [("assistant", f"called node {self.name}")]}


def route(state: State) -> Literal["entry_node", END]:  # type: ignore
    if len(state["messages"]) > 10:
        return END
    return "entry_node"


def add_fractal_nodes(builder, current_node, level, max_level):
    if level > max_level:
        return
    num_nodes = random.randint(1, 3)
    for i in range(num_nodes):
        nm = ["A", "B", "C"][i]
        node_name = f"node_{current_node}_{nm}"
        builder.add_node(node_name, MyNode(node_name))
        builder.add_edge(current_node, node_name)

        # 创建多层级的随机节点
        r = random.random()
        if r > 0.2 and level + 1 < max_level:
            add_fractal_nodes(builder, node_name, level + 1, max_level)
        elif r > 0.5:
            builder.add_conditional_edges(node_name, route, node_name)
        else:
            builder.add_edge(node_name, END)


def build_fractal_graph(max_level: int):
    builder = StateGraph(State)
    entry_point = "entry_node"
    builder.add_node(entry_point, MyNode(entry_point))
    builder.add_edge(START, entry_point)
    add_fractal_nodes(builder, entry_point, 1, max_level)

    return builder.compile()


agent = build_fractal_graph(3)


from IPython.display import Image, display
from langchain_core.runnables.graph import CurveStyle, MermaidDrawMethod, NodeStyles
import nest_asyncio
import os


nest_asyncio.apply()
# 配置Pyppeteer使用系统Chrome（无需下载新的Chromium）
os.environ["CHROME_EXECUTABLE_PATH"] = (
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
)


png_bytes = agent.get_graph().draw_mermaid_png(
    draw_method=MermaidDrawMethod.PYPPETEER,
    curve_style=CurveStyle.LINEAR,
    node_colors=NodeStyles(
        first="#ffdfba",
        last="#baffc9",
        default="#fad7de",
    ),
    wrap_label_n_words=9,
    output_file_path=None,
    background_color="white",
    padding=10,
)

display(Image(png_bytes))

# %%
