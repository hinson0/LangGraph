# %% 7-14 LangGraph中可用的人机环路交互对象结构体

from typing import TypedDict, Literal


class HumanInterruptConfig(TypedDict):
    allow_ignore: bool
    allow_respond: bool
    allow_edit: bool
    allow_accept: bool


class ActionRequest(TypedDict):
    action: str
    args: dict


class HumanInterrupt(TypedDict):
    action_request: ActionRequest
    config: HumanInterruptConfig
    description: str | None


class HumanResponse(TypedDict):
    text: Literal["accept", "ignore", "response", "edit"]
    args: str | ActionRequest | None


# %% 7-15 在LangGraph的图函数中使用HumanInterrupt
from langgraph.graph import StateGraph, START, END, MessagesState
from langgraph.types import interrupt
from langchain_core.messages import HumanMessage, ToolMessage, AIMessage


def tools_by_name():
    pass


class AgentState(MessagesState):
    pass


def agent_node(state: AgentState):
    """智能体节点，决定是否调用工具或请求人工输入"""
    last_message = state["messages"][-1]
    tool_call_name = "hypothetical_tool"
    tool_call_args = {"input_arg": "example_value"}

    request: HumanInterrupt = {
        "action_request": {"action": tool_call_name, "args": tool_call_args},
        "config": {
            "allow_accept": True,
            "allow_edit": True,
            "allow_ignore": True,
            "allow_respond": True,
        },
        "description": f"智能体建议使用参数{tool_call_args}调用参数调用工具：{tool_call_name}。你批准吗？",
    }

    response_list = interrupt([request])
    response = response_list[0] if response_list else None

    if response:
        if response["type"] == "accept":
            tool_result = tools_by_name[tool_call_name].invoke(response["args"])
            output_message = ToolMessage(
                content=str(tool_result), tool_callid=last_message.tool_calls[0].id
            )
        elif response["type"] == "edit":
            edited_args = response["args"]["args"]
            tool_result = tools_by_name[tool_call_name].invoke(edited_args)
            output_message = ToolMessage(
                content=str(tool_result), tool_call_id=last_message.tool_calls[0].id
            )
        elif response["type"] == "response":
            user_response_text = response["args"]
            output_message = AIMessage(
                content=f"用户相应：{user_response_text}。根据响应继续进行操作。"
            )
        elif response["type"] == "ignore":
            output_message = AIMessage(
                content="人工中断被忽略。继续进行操作，不进行工具调用。"
            )
        else:
            output_message = AIMessage(content="未知的人工响应类型")
    else:
        output_message = AIMessage(content="未收到人工响应，继续进行操作不进行干预")

    return {"messages": [output_message]}


# build a graph
graph = StateGraph(AgentState)
graph.add_node(agent_node)
graph.set_entry_point(agent_node.__name__)
graph.set_finish_point(agent_node.__name__)
workflow = graph.compile()

# example call for demo
messages = [HumanMessage(content="启动工作流，并可能触发中断")]
response = workflow.invoke({"messages": messages})
print(response)
