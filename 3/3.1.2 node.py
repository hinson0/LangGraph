# %% 3-10
def process_data(input_data):
    raise NotImplementedError


def my_node(state):
    # read state from state
    input_data = state["messages"]
    # process input_data
    output_data = process_data(input_data)

    # return new state
    return {"some_key": output_data, "another_key": new_value}


# %% 3-11
from ast import match_case
from pyexpat.errors import messages
from typing import TypedDict
from langgraph.graph import StateGraph, START, END, MessagesState
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from sqlalchemy import literal
from tenacity import retry


# define a state constructor
class ChatState(MessagesState):
    user_input: str
    llm_response: str


# define a LLM node
def llm_node(state):
    prompt = ChatPromptTemplate.from_messages([("human", "{question}")])
    model = ChatOpenAI(model="Qwen/Qwen2.5-7B-Instruct")
    chain = prompt | model
    response = chain.invoke({"question": state["user_question"]}).content
    return {"llm_response": response}


# define a graph
builder = StateGraph(ChatState)
builder.add_node("llm_node", llm_node)
builder.add_edge(START, "llm_node")
builder.add_edge("llm_node", END)
graph = builder.compile()

# invoke this graph
result = graph.invoke({"user_question": "hello LangGraph"})
print(result)


# %% 3-12 Node Retry
import operator
import sqlite3

from typing import Annotated, Sequence
from typing_extensions import TypedDict


from langchain_openai import ChatOpenAI
from langchain_community.utilities import SQLDatabase
from langchain_core.messages import AIMessage, BaseMessage

from langgraph.graph import StateGraph, START, END
from langgraph.types import RetryPolicy

# 定义数据库和模型
db = SQLDatabase.from_uri("sqlite:///:memory:")
model = ChatOpenAI(model="Qwen/Qwen2.5-7B-Instruct")


# 定义图的状态和逻辑节点
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]


def query_database(state):
    query_result = db.run("SELECT * FROM Artist LIMIT 10;")
    return {"messages": [AIMessage(content=query_result)]}


def call_model(state):
    response = model.invoke(state["messages"])
    return {"messages": [response]}


# 定义图
builder = StateGraph(AgentState)

# query_database节点
builder.add_node(
    "query_database",
    query_database,
    retry_policy=RetryPolicy(retry_on=sqlite3.OperationalError),
)

# model节点
builder.add_node("model", call_model, retry_policy=RetryPolicy(max_attempts=5))

# query_url节点
builder.add_node(
    "query_url", lambda state: {"messages": ["get something from the url"]}
)

# 构建图
builder.add_edge(START, "model")
builder.add_edge("model", "query_database")
builder.add_edge("query_database", END)

graph = builder.compile()

# %% 我的想法


builder.add_edge(START, "model")
builder.add_conditional_edges(
    "model",
    lambda state: "query_database"
    if state["selected_tool"] == "数据库"
    else "query_url",
)
builder.add_edge("query_database", END)


# %% 3-13 意图识别和技能路由流程


def intent_recognition_node(state):
    return NotImplemented


def route_to_skill(state):
    user_intent = state["user_intent"]
    if user_intent == "查询天气":
        return "weather_query_node"
    elif user_intent == "预定机票":
        return "flight_booking_node"
    elif user_intent == "投诉建议":
        return "complaint_suggestion_node"
    else:
        return END


builder.add_conditional_edges("intent_recognition_node", route_to_skill)


# %% 3-14  工具选择和结果处理流程
def route_after_tool_selection(state):
    tool_name = state["selected_tool"]
    match tool_name:
        case "搜索引擎":
            return "search_tool_node"
        case "计算器":
            return "calculator_tool_node"
        case _:
            return END


def route_after_tool_execution(state):
    tool_status = state["tool_status"]
    if tool_status == "成功":
        return "tool_result_processing_node"
    else:
        return "tool_error_handling_node"


builder.add_conditional_edges("tool_selection_node", route_after_tool_selection)
builder.add_conditional_edges("tool_execution_node", route_after_tool_execution)

# %% 3-15 使用命令的节点函数
from langgraph.types import Command
from typing import Literal


def decide_next_node(state):
    return NotImplemented


def my_node(state) -> Command[Literal["node_B", "node_C"]]:
    next_node_name = decide_next_node(state)
    result_data = ...
    return Command(update={"processed_data": result_data}, goto=next_node_name)
