# %% 3-28 使用@tool装饰器定义工具函数

from langchain_core.tools import tool


@tool
def get_weather(location: str):  # type: ignore
    """获取天气"""
    if location.lower() in ["sf", "cn"]:
        return "It's 16 degrees and foggy."
    else:
        return "It's 32 degrees and sunny."


@tool
def get_coolest_cities():  # type: ignore
    """获取最冷的城市名"""
    return "NYC, SF"


# %% 3-29 手动调用ToolNode


from langchain_core.messages import AIMessage  # noqa: E402
from langgraph.prebuilt import ToolNode  # noqa: E402
# from langgraph.checkpoint import Me


tool_node = ToolNode([get_weather, get_coolest_cities])

# checkpointer = MemorySaver()
config = {"configurable": {"thread_id": "test_1"}}  # 关键：提供运行时配置

message_with_single_tool_call = AIMessage(
    content="",
    tool_calls=[
        {
            "name": "get_weather",
            "args": {"location": "sf"},
            "id": "tool_call_id",
            "type": "tool_call",
        }
    ],
)

tool_node.invoke(
    {
        "messages": [message_with_single_tool_call],
    }
)

# %%3-30 手动调用ToolNode，并行工具调用

message_with_multiple_tool_calls = AIMessage(
    content="",
    tool_calls=[
        {
            "name": "get_weather",
            "args": {"location": "sf"},
            "id": "tool_call_id",
            "type": "tool_call",
        },
        {
            "name": "get_coolest_cities",
            "args": {"location": "sf"},
            "id": "tool_call_id",
            "type": "tool_call",
        },
    ],
)

tool_node.invoke({"messags": [message_with_multiple_tool_calls]})

# %% 3-28 使用@tool装饰器定义工具函数

from langchain_core.tools import tool  # noqa: E402


@tool
def get_weather(location: str):  # type: ignore
    """获取天气"""
    if location.lower() in ["sf", "cn"]:
        return "It's 16 degrees and foggy."
    else:
        return "It's 32 degrees and sunny."


@tool
def get_coolest_cities():  # type: ignore
    """获取最冷的城市名"""
    return "NYC, SF"


from langchain_core.messages import AIMessage  # noqa: E402
from langgraph.prebuilt import ToolNode  # noqa: E402

# 1. 创建ToolNode，传入工具列表
tool_node = ToolNode([get_weather, get_coolest_cities])

# 3. 构造包含工具调用的消息
message_with_single_tool_call = AIMessage(
    content="",
    tool_calls=[
        {
            "name": "get_weather",
            "id": "tool_call_id2",
            "type": "tool_call",
        }
    ],
)

config = {"configurable": {"thread_id": "test_1"}}

# 调用ToolNode，并确保传入正确的config参数
tool_node_output = tool_node.invoke(
    {"messages": [message_with_single_tool_call]},  # 状态字典
)

# %%3-31 在langgraph图中使用ToolNode构建ReAct智能体
from langgraph.graph import StateGraph, START, END, MessagesState  # noqa: E402
from langgraph.prebuilt import ToolNode  # noqa: E402
from langchain_openai import ChatOpenAI  # noqa: E402
from langchain_core.tools import tool  # noqa: E402


@tool
def get_weather(location: str):
    """获取天气"""
    if location.lower() in ["sf", "cn"]:
        return "It's 16 degrees and foggy."
    else:
        return "It's 32 degrees and sunny."


@tool
def get_coolest_cities():
    """获取最冷的城市名"""
    return "NYC, SF"


tools = [get_weather, get_coolest_cities]
tool_node = ToolNode(tools)

model_with_tools = ChatOpenAI(
    model="Qwen/Qwen2.5-7B-Instruct", temperature=0
).bind_tools(tools)


def should_continue(state: MessagesState):
    last_message = state["messages"][-1]
    if last_message.tool_calls:
        return "tools"
    return END


def call_mode(state: MessagesState):
    response = model_with_tools.invoke(state["messages"])
    return {"messages": [response]}


workflow = StateGraph(MessagesState)
workflow.add_node("agent", call_mode)
workflow.add_node("tools", tool_node)

workflow.add_edge(START, "agent")
workflow.add_conditional_edges("agent", should_continue, ["tools", END])
workflow.add_edge("tools", "agent")

app = workflow.compile()


# %% 3-32 自定义工具节点，处理出现错误时（模型降级+错误消息处理）
import json  # noqa: E402
from langchain_core.messages import AIMessage, ToolMessage  # noqa: E402
from langgraph.graph import MessagesState, StateGraph, START, END  # noqa: E402
from langchain_core.tools import tool  # noqa: E402
from langchain_openai import ChatOpenAI  # noqa: E402
from langchain_core.output_parsers import StrOutputParser  # noqa: E402
from pydantic import BaseModel, Field  # noqa: E402
from typing import Literal  # noqa: E402
from langchain_core.messages.modifier import RemoveMessage  # noqa: E402


class HaikuRequest(BaseModel):
    topic: list[str] = Field(max_length=3, min_length=0)


@tool
def master_haiku_generator_tool(request: HaikuRequest):
    """生成一个海库，基于多个给定的主题"""
    model = ChatOpenAI(model="Qwen/Qwen2.5-7B-Instruct", temperature=0)
    chain = model | StrOutputParser()
    topics = ", ".join(request.topic)
    haiku = chain.invoke(f"write a haiku about {topics}")
    return haiku


model = ChatOpenAI(model="Qwen/Qwen2-1.5B-Instruct", temperature=0)
model_with_tools = model.bind_tools([master_haiku_generator_tool])

better_model = ChatOpenAI(model="Qwen/Qwen2.5-7B-Instruct", temperature=0)
better_model_with_tools = better_model.bind_tools([master_haiku_generator_tool])


def call_model_node(state: MessagesState):
    return {"messages": [model_with_tools.invoke(state["messages"])]}


def should_continue_node(state: MessagesState):
    return "call_tool_node" if state["messages"][-1].tool_calls else END


def call_tool_node(state: MessagesState):
    tools_by_name = {master_haiku_generator_tool.name: master_haiku_generator_tool}
    messages = state["messages"]
    last_message = messages[-1]
    output_messages = []
    for tool_call in last_message.tool_calls:
        try:
            tool_result = tools_by_name(tool_call["name"]).invoke(tool_call["args"])
            output_messages.append(
                ToolMessage(
                    content=json.dumps(tool_result),
                    name=tool_call["name"],
                    tool_call_id=tool_call["id"],
                )
            )
        except Exception as e:
            output_messages.append(
                ToolMessage(
                    content=str(e),
                    name=tool_call["name"],
                    tool_call_id=tool_call["id"],
                    additional_kwargs={"error": e},
                )
            )
    return {"messages": output_messages}


def should_fallback_node(
    state: MessagesState,
) -> Literal["call_model_node", "remove_failed_tool_call_attempt_node"]:
    messages = state["messages"]
    failed_tool_messages = [
        msg
        for msg in messages
        if isinstance(msg, ToolMessage) and msg.additional_kwargs.get("error")
    ]
    if failed_tool_messages:
        return "remove_failed_tool_call_attempt_node"
    return "call_model_node"


def remove_failed_tool_call_attempt_node(state: MessagesState):
    last_ai_message_index = next(
        i
        for i, msg in reversed(list(enumerate(state["messages"])))
        if isinstance(msg, AIMessage)
    )
    messages_to_remove = state["messages"][last_ai_message_index:]

    return {"messages": [RemoveMessage(id=m.id) for m in messages_to_remove]}


def call_fallback_model_node(state: MessagesState):
    return {"messages": [better_model_with_tools.invoke(state["messages"])]}


# 创建图
builder = StateGraph(MessagesState)
builder.add_node(call_model_node)
builder.add_node(call_tool_node)
builder.add_node(remove_failed_tool_call_attempt_node)
builder.add_node(call_fallback_model_node)

builder.set_entry_point("call_model_node")
builder.add_conditional_edges("call_model_node", should_continue_node)
builder.add_conditional_edges("call_tool_node", should_fallback_node)
builder.add_edge("remove_failed_tool_call_attempt_node", "call_fallback_model_node")
builder.add_edge("call_fallback_model_node", "call_tool_node")

graph = builder.compile()

# %% 3-33 工具函数返回Command对象，更新图状态
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

# %% 3-34 使用Annotated和Injected注解传递运行时参数
from typing import Annotated, Any

from langchain_core.tools import tool, InjectedToolCallId
from langchain_core.runnables.config import RunnableConfig
from langchain_core.messages import ToolMessage
from langchain.agents import AgentState
from langchain_openai import ChatOpenAI


from langgraph.types import Command
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode, InjectedState

USER_INFO = [
    dict(user_id=1, name="bob dylan", location="new york"),
    dict(user_id=2, name="yangzhibing", location="jiangxi fuzhou"),
]

USER_ID_TO_USER_INFO = {info["user_id"]: info for info in USER_INFO}


class State(AgentState):
    user_info: dict[str, Any]
    user_id: int


@tool
def lookup_user_info_tool(
    tool_call_id: Annotated[str, InjectedToolCallId],
    user_id: Annotated[int, InjectedState("user_id")],
):
    """查询用户信息的工具，更好辅助他们获取问题信息"""
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
    {"messages": [("human", "今天江西南丰的天气?")], "user_id": 1},  # type: ignore
):
    print(chunk)
