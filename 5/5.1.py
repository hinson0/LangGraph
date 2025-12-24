from typing import TypedDict, Any
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage


class AgentState(TypedDict):
    messages: list[BaseMessage]
    intermediate_results: dict[str, Any]


# %% 5-2 在LangGraph中通过中间结果管理短期记忆
def add_user_messages(
    state: AgentState, user_message: str
) -> dict[str, list[BaseMessage]]:
    new_message = HumanMessage(content=user_message)
    return {"messages": state["messages"] + [new_message]}


def add_ai_message(state: AgentState, ai_response: str) -> dict[str, list[BaseMessage]]:
    new_message = AIMessage(content=ai_response)
    return {"messages": state["messages"] + [new_message]}


# %% 在LangGraph中通过截断管理短期记忆
from langchain_core.messages import trim_messages
from langchain_openai import ChatOpenAI


type ReturnedMessages = dict[str, list[BaseMessage]]


def truncate_history(state: AgentState, max_messages: int) -> ReturnedMessages:
    return {"messages": state["messages"][-max_messages:]}


def trim_message_history_by_token(
    state: AgentState, max_tokens: int
) -> ReturnedMessages:
    msgs = trim_messages(
        state["messages"],
        strategy="last",
        token_counter=ChatOpenAI(model="gpt-4o"),
        max_tokens=max_tokens,
        start_on="human",
        end_on=("human", "tool"),
        include_system=True,
    )

    return {"messages": msgs}


# %% 在LangGraph中有选择性的保留和管理短期记忆

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import chain
from langchain_openai import ChatOpenAI


def summarize_history(state: AgentState, llm) -> ReturnedMessages:
    conversation = ...
    prompt = ChatPromptTemplate.from_template(
        f"总结以下对话仅供参考:\n {conversation} "
    )
    conversation_str = "\n".join(f"{m.role}: {m.content}" for m in state["messages"])  # type: ignore
    summarization_chain = prompt | llm | StrOutputParser()
    summary = summarization_chain.invoke({"conversation": conversation_str})

    # 将历史记录替换为摘要和最新的用户信息
    summary_msg = AIMessage(content=summary)
    last_human_msg = (
        [m for m in state["messages"] if m.type == "human"][-1]
        if any(m.type == "human" for m in state["messages"])
        else None
    )

    new_msgs = [summary_msg]
    if last_human_msg:
        new_msgs.append(last_human_msg)  # type: ignore

    return {"messages": new_msgs}  # type: ignore


"""
管理短期记忆的几种方式：
    * 截取
    * 摘要
    * 关键信息片段
"""

# %%
