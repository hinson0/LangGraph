#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LangGraph 3.5 完整可运行测试用例
演示内容：自定义工具节点 + 错误处理 + 模型降级机制
"""

# 导入必要的库
import json
import os
from dotenv import load_dotenv
from langchain_core.tools import tool
from langchain_core.messages import AIMessage, ToolMessage, HumanMessage
from langgraph.graph import MessagesState, StateGraph, START, END
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from pydantic import BaseModel, Field
from typing import Literal
from langchain_core.messages.modifier import RemoveMessage


# 加载环境变量
load_dotenv()


# 1. 定义工具参数模型
class HaikuRequest(BaseModel):
    """生成诗的请求参数模型"""

    topic: list[str] = Field(
        max_length=3, min_length=1, description="诗主题列表，最多3个"
    )


# 2. 定义自定义工具
@tool
def master_haiku_generator_tool(request: HaikuRequest):
    """生成一个诗，基于多个给定的主题"""
    # 使用相同的模型配置
    model = ChatOpenAI(
        model="Qwen/Qwen2.5-7B-Instruct",
        temperature=0.3,
        base_url=os.environ.get("OPENAI_BASE_URL"),
    )
    chain = model | StrOutputParser()
    topics = ", ".join(request.topic)
    haiku = chain.invoke(
        f"write a haiku about {topics}. Make sure it follows the 5-7-5 syllable pattern. Respond in Chinese."
    )
    return haiku


# 3. 配置模型
# 基础模型（使用可用的模型）
model = ChatOpenAI(
    model="Qwen/Qwen2.5-7B-Instruct",  # 替换为可用的模型
    temperature=0.7,  # 提高温度，增加生成内容的可能性
    base_url=os.environ.get("OPENAI_BASE_URL"),
)
model_with_tools = model.bind_tools([master_haiku_generator_tool])

# 降级模型（使用同一个可用模型，或替换为其他可用模型）
better_model = ChatOpenAI(
    model="Qwen/Qwen2.5-7B-Instruct",  # 保持一致或使用其他可用模型
    temperature=0.7,  # 提高温度，增加生成内容的可能性
    base_url=os.environ.get("OPENAI_BASE_URL"),
)
better_model_with_tools = better_model.bind_tools([master_haiku_generator_tool])


# 4. 定义工作流节点
def call_model_node(state: MessagesState):
    """调用基础模型节点"""
    print("\n📤 调用基础模型...")
    print(f"   输入消息数量: {len(state['messages'])}")
    print(f"   最后一条消息类型: {type(state['messages'][-1]).__name__}")
    print(f"   最后一条消息内容: {state['messages'][-1].content[:100]}...")

    response = model_with_tools.invoke(state["messages"])

    print(f"   模型响应类型: {type(response).__name__}")
    print(
        f"   模型响应内容: {response.content[:100]}..."
        if response.content
        else "   模型响应内容: (空)"
    )
    if hasattr(response, "tool_calls") and response.tool_calls:
        print(f"   工具调用数量: {len(response.tool_calls)}")
        print(f"   工具调用名称: {response.tool_calls[0]['name']}")
        print(f"   工具调用参数: {response.tool_calls[0]['args']}")

    return {"messages": [response]}


def should_continue_node(state: MessagesState):
    """决策节点：是否需要调用工具"""
    last_message = state["messages"][-1]
    print(f"\n🔍 检查是否需要调用工具...")
    print(f"   最后一条消息类型: {type(last_message).__name__}")

    if last_message.tool_calls:
        print(f"🔧 检测到工具调用: {last_message.tool_calls[0]['name']}")
        return "call_tool_node"

    print("✅ 对话完成，返回最终结果")
    return END


def call_tool_node(state: MessagesState):
    """调用工具节点（带错误处理）"""
    tools_by_name = {master_haiku_generator_tool.name: master_haiku_generator_tool}
    messages = state["messages"]
    last_message = messages[-1]
    output_messages = []

    print("\n⚙️ 执行工具调用...")
    print(f"   工具调用数量: {len(last_message.tool_calls)}")

    for tool_call in last_message.tool_calls:
        try:
            print(f"\n   执行工具: {tool_call['name']}")
            print(f"   参数: {tool_call['args']}")

            # 执行工具调用
            tool_result = tools_by_name[tool_call["name"]].invoke(tool_call["args"])
            print(f"   工具执行成功!")
            print(f"   工具结果: {tool_result[:100]}...")

            # 添加成功的工具消息
            output_messages.append(
                ToolMessage(
                    content=json.dumps(tool_result),
                    name=tool_call["name"],
                    tool_call_id=tool_call["id"],
                )
            )
        except Exception as e:
            print(f"   工具执行失败: {str(e)}")

            # 添加包含错误信息的工具消息
            output_messages.append(
                ToolMessage(
                    content=str(e),
                    name=tool_call["name"],
                    tool_call_id=tool_call["id"],
                    additional_kwargs={"error": str(e)},
                )
            )

    return {"messages": output_messages}


def should_fallback_node(
    state: MessagesState,
) -> Literal["call_model_node", "remove_failed_tool_call_attempt_node"]:
    """决策节点：是否需要降级到更好的模型"""
    messages = state["messages"]
    failed_tool_messages = [
        msg
        for msg in messages
        if isinstance(msg, ToolMessage) and msg.additional_kwargs.get("error")
    ]

    print("\n🔄 检查工具调用结果...")
    print(f"   失败的工具调用数量: {len(failed_tool_messages)}")

    if failed_tool_messages:
        print("🔄 检测到工具调用失败，准备降级到更好的模型")
        return "remove_failed_tool_call_attempt_node"

    print("🔄 工具调用成功，回到模型生成最终回复")
    return "call_model_node"


def remove_failed_tool_call_attempt_node(state: MessagesState):
    """移除失败的工具调用尝试"""
    print("\n🗑️ 移除失败的工具调用历史...")

    last_ai_message_index = next(
        i
        for i, msg in reversed(list(enumerate(state["messages"])))
        if isinstance(msg, AIMessage)
    )
    messages_to_remove = state["messages"][last_ai_message_index:]

    print(f"   要移除的消息数量: {len(messages_to_remove)}")
    for msg in messages_to_remove:
        print(f"   移除消息: {type(msg).__name__}")

    return {"messages": [RemoveMessage(id=m.id) for m in messages_to_remove]}


def call_fallback_model_node(state: MessagesState):
    """调用降级模型节点"""
    print("\n📤 调用降级模型...")
    print(f"   输入消息数量: {len(state['messages'])}")

    response = better_model_with_tools.invoke(state["messages"])

    print(f"   模型响应类型: {type(response).__name__}")
    print(
        f"   模型响应内容: {response.content[:100]}..."
        if response.content
        else "   模型响应内容: (空)"
    )
    if hasattr(response, "tool_calls") and response.tool_calls:
        print(f"   工具调用数量: {len(response.tool_calls)}")

    return {"messages": [response]}


# 5. 构建工作流图
def build_workflow():
    """构建完整的工作流图"""
    print("🏗️ 构建工作流图...")

    builder = StateGraph(MessagesState)

    # 添加节点
    builder.add_node("call_model_node", call_model_node)
    builder.add_node("call_tool_node", call_tool_node)
    builder.add_node(
        "remove_failed_tool_call_attempt_node", remove_failed_tool_call_attempt_node
    )
    builder.add_node("call_fallback_model_node", call_fallback_model_node)

    # 添加边
    builder.set_entry_point("call_model_node")
    builder.add_conditional_edges("call_model_node", should_continue_node)
    builder.add_conditional_edges("call_tool_node", should_fallback_node)
    builder.add_edge("remove_failed_tool_call_attempt_node", "call_fallback_model_node")
    builder.add_edge("call_fallback_model_node", "call_tool_node")

    # 编译工作流
    return builder.compile()


# 6. 测试函数
def test_haiku_generation():
    """测试诗生成功能"""
    print("\n" + "=" * 60)
    print("🧪 测试：生成诗")
    print("=" * 60)

    # 构建工作流
    graph = build_workflow()

    # 定义测试输入 - 更明确地请求诗
    test_input = {
        "messages": [HumanMessage(content="请生成一首关于春天、樱花和希望的诗")]
    }

    try:
        # 运行工作流
        print("\n🚀 开始运行工作流...")
        result = graph.invoke(test_input)

        # 打印结果
        print("\n" + "=" * 60)
        print("🎉 工作流运行完成！")
        print("=" * 60)

        # 打印所有消息
        print("\n📝 所有消息历史:")
        print("-" * 40)
        for i, msg in enumerate(result["messages"]):
            print(f"消息 {i + 1}: {type(msg).__name__}")
            if hasattr(msg, "content") and msg.content:
                print(f"内容: {msg.content}")
            if hasattr(msg, "tool_calls") and msg.tool_calls:
                print(f"工具调用: {msg.tool_calls}")
            print("-" * 40)

        # 输出最终回复
        final_message = result["messages"][-1]
        print(f"\n💬 最终回复:\n{final_message.content}")

        # 如果最终回复为空，检查是否有工具结果
        if not final_message.content:
            print("\n⚠️ 注意：最终回复为空！")
            print("检查工具结果是否正确生成...")
            # 查找工具消息
            tool_messages = [
                msg for msg in result["messages"] if isinstance(msg, ToolMessage)
            ]
            if tool_messages:
                print(f"\n找到 {len(tool_messages)} 条工具消息:")
                for msg in tool_messages:
                    print(f"工具消息内容: {msg.content}")

    except Exception as e:
        print(f"\n❌ 测试失败: {type(e).__name__}: {e}")
        import traceback

        traceback.print_exc()


# 7. 主函数
if __name__ == "__main__":
    # 运行测试
    test_haiku_generation()
