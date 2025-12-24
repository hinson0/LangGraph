# %% 3-35 获取Mermaid语法描述

from typing import Annotated, Any
import os
import nest_asyncio

# 解决异步事件循环嵌套问题
nest_asyncio.apply()

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


# 添加节点
graph.add_node(agent_node)
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

# %% 3-37 使用系统Chrome浏览器渲染PNG图片

from IPython.display import Image, display
from langchain_core.runnables.graph import MermaidDrawMethod

try:
    # 配置环境变量，让Pyppeteer使用系统已安装的Chrome
    os.environ["PYPPETEER_CHROMIUM_REVISION"] = "1181205"  # 使用已下载的版本
    os.environ["CHROME_EXECUTABLE_PATH"] = (
        "/Applications/Google Chrome.app"  # 系统Chrome路径
    )

    # 使用Pyppeteer渲染，使用系统Chrome
    png_bytes = agent.get_graph().draw_mermaid_png(
        draw_method=MermaidDrawMethod.PYPPETEER
    )
    display(Image(png_bytes))
except Exception as e:
    print(f"Pyppeteer渲染失败: {e}")
