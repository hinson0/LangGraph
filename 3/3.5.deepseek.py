import json
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from langgraph.graph import StateGraph, MessagesState, START, END
from langchain_core.tools import tool
from pydantic import BaseModel, Field
from typing import Literal, List

# ========== 1. 定义状态和工具 ==========
print("=" * 50)
print("构建带错误降级的ReAct智能体（修复递归问题）")
print("=" * 50)


class HaikuRequest(BaseModel):
    topic: List[str] = Field(max_length=3, min_length=0)


@tool
def master_haiku_generator_tool(request: HaikuRequest):
    """生成一个俳句，基于多个给定的主题"""
    print(f"[工具调用] 生成关于 {request.topic} 的俳句...")

    topics = ", ".join(request.topic)

    # 情景1: 主题包含"失败"关键词，模拟工具异常
    if any(keyword in topics.lower() for keyword in ["失败", "error", "bad"]):
        print(f"[工具调用] 模拟工具异常: 主题包含敏感词")
        raise ValueError(f"无法为包含敏感词的主题生成俳句: {topics}")

    # 情景2: 正常情况返回俳句
    haiku_dict = {
        "春天": "樱花飘落时\n微风轻拂过湖面\n春日暖阳照",
        "冬天,雪": "白雪覆山川\n寒风中松树挺立\n冬日静悄悄",
        "月亮,夜晚": "银盘挂夜空\n月影倒映在湖心\n静夜思故乡",
    }

    key = ", ".join(sorted(request.topic))
    result = haiku_dict.get(key, f"关于{topics}的原创俳句...")
    print(f"[工具调用] 成功生成俳句")
    return result


# ========== 2. 模拟LLM节点函数 ==========
def call_model_node(state: MessagesState):
    """模拟主模型：决定是否调用工具"""
    user_input = state["messages"][-1].content
    print(f"[主模型] 分析用户输入: '{user_input}'")

    if "俳句" in user_input or "haiku" in user_input.lower():
        topics = []
        for word in ["春天", "冬天", "雪", "月亮", "失败", "error"]:
            if word in user_input:
                topics.append(word)

        if not topics:
            topics = ["春天"]

        tool_message = AIMessage(
            content="",
            tool_calls=[
                {
                    "name": "master_haiku_generator_tool",
                    "args": {"request": {"topic": topics}},
                    "id": f"call_{len(state['messages'])}",
                    "type": "tool_call",
                }
            ],
        )
        print(f"[主模型] 决定调用工具，主题: {topics}")
        return {"messages": [tool_message]}
    else:
        response = "您好！我可以帮您生成俳句。请告诉我您想要的主题，比如'写一个关于春天的俳句'。"
        print(f"[主模型] 直接回复引导信息")
        return {"messages": [AIMessage(content=response)]}


def call_fallback_model_node(state: MessagesState):
    """模拟降级模型：使用更强大的模型重试"""
    print(f"[降级模型] 使用增强模型处理...")

    # 改进的响应：使用更安全的主题
    tool_message = AIMessage(
        content="",
        tool_calls=[
            {
                "name": "master_haiku_generator_tool",
                "args": {"request": {"topic": ["春天"]}},
                "id": f"fallback_{len(state['messages'])}",
                "type": "tool_call",
            }
        ],
    )
    print(f"[降级模型] 已调整主题为安全选项")
    return {"messages": [tool_message]}


# ========== 3. 工具执行节点 ==========
def call_tool_node(state: MessagesState):
    """执行工具调用"""
    tools_by_name = {"master_haiku_generator_tool": master_haiku_generator_tool}
    messages = state["messages"]
    last_message = messages[-1]
    output_messages = []

    print(f"[工具节点] 执行工具调用...")

    for tool_call in last_message.tool_calls:
        try:
            args = tool_call["args"].copy()
            if "request" in args:
                args["request"] = HaikuRequest(**args["request"])

            tool_result = tools_by_name[tool_call["name"]].invoke(args)

            output_messages.append(
                ToolMessage(
                    content=json.dumps(tool_result, ensure_ascii=False),
                    name=tool_call["name"],
                    tool_call_id=tool_call["id"],
                )
            )
            print(f"[工具节点] 工具执行成功")

        except Exception as e:
            print(f"[工具节点] 工具执行失败: {e}")
            output_messages.append(
                ToolMessage(
                    content=str(e),
                    name=tool_call["name"],
                    tool_call_id=tool_call["id"],
                    additional_kwargs={"error": True},
                )
            )

    return {"messages": output_messages}


# ========== 4. 错误处理节点 ==========
def remove_failed_tool_call_attempt_node(state: MessagesState):
    """移除失败的工具调用尝试"""
    print(f"[清理节点] 清理失败记录...")
    return {"messages": []}  # 返回空消息列表，实际上会清除状态


# ========== 5. 修复后的路由函数 ==========
def should_continue_node(state: MessagesState) -> Literal["call_tool_node", END]:
    """主路由：判断是否需要调用工具"""
    last_message = state["messages"][-1]
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        print(f"[主路由] 检测到工具调用，前往工具节点")
        return "call_tool_node"
    else:
        print(f"[主路由] 无工具调用，结束流程")
        return END


def should_fallback_node(
    state: MessagesState,
) -> Literal["call_model_node", "remove_failed_tool_call_attempt_node", END]:
    """修复：工具执行后的路由逻辑"""
    messages = state["messages"]
    last_message = messages[-1]

    # 情况1: 如果最后一条消息是ToolMessage且包含错误，触发降级
    if isinstance(last_message, ToolMessage) and last_message.additional_kwargs.get(
        "error"
    ):
        print(f"[错误路由] 检测到工具错误，触发降级流程")
        return "remove_failed_tool_call_attempt_node"

    # 情况2: 如果最后一条消息是ToolMessage且没有错误，直接结束
    elif isinstance(last_message, ToolMessage):
        print(f"[错误路由] 工具执行成功，结束流程")
        return END  # 关键修复：成功执行后结束，而不是返回主模型

    # 情况3: 其他情况返回主模型（实际上不会走到这里）
    else:
        print(f"[错误路由] 其他情况，返回主模型")
        return "call_model_node"


# ========== 6. 构建工作流图 ==========
print("\n[系统] 开始构建工作流图...")

builder = StateGraph(MessagesState)

# 添加所有节点
builder.add_node("call_model_node", call_model_node)
builder.add_node("call_tool_node", call_tool_node)
builder.add_node(
    "remove_failed_tool_call_attempt_node", remove_failed_tool_call_attempt_node
)
builder.add_node("call_fallback_model_node", call_fallback_model_node)

# 配置修复后的工作流
builder.set_entry_point("call_model_node")
builder.add_conditional_edges("call_model_node", should_continue_node)
builder.add_conditional_edges(
    "call_tool_node", should_fallback_node
)  # 关键：连接工具节点到修复后的路由
builder.add_edge("remove_failed_tool_call_attempt_node", "call_fallback_model_node")
builder.add_edge("call_fallback_model_node", "call_tool_node")  # 降级后重新执行工具

# 编译图
graph = builder.compile()
print("[系统] 工作流图构建完成！")

# ========== 7. 测试案例 ==========
test_cases = [
    "帮我写一个关于春天的俳句",
    "生成一个包含失败关键词的俳句",  # 会触发错误降级
    "你好，今天天气怎么样？",  # 不会调用工具
    "写一个关于冬天和雪的俳句",
]

print(f"\n{'=' * 60}")
print("开始测试智能体（已修复递归问题）")
print("=" * 60)

for i, question in enumerate(test_cases, 1):
    print(f"\n{'=' * 40}")
    print(f"测试 {i}: '{question}'")
    print("=" * 40)

    # 初始化状态
    initial_state = {"messages": [HumanMessage(content=question)]}

    try:
        # 执行工作流
        final_state = graph.invoke(initial_state)

        # 提取并显示最终回复
        final_messages = final_state["messages"]
        for msg in reversed(final_messages):
            if hasattr(msg, "content") and msg.content:
                print(f"\n[最终回复] {msg.content}")
                break

    except Exception as e:
        print(f"[执行错误] {e}")

print(f"\n{'=' * 60}")
print("所有测试完成！")
print("=" * 60)
