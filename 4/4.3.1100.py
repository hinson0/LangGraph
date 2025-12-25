# %% 使用interrupt()函数的"人工编辑节点"完整示例
from langgraph.types import Interrupt, Command
from typing import TypedDict, Annotated
from langgraph.graph import StateGraph
from langgraph.checkpoint.memory import MemorySaver
import operator
from rich import print as rprint


# ================================================
# 步骤1：定义状态类型
# ================================================
class CalculationState(TypedDict):
    """计算图的状态定义"""

    value: int  # 当前计算值
    history: Annotated[list, operator.add]  # 历史计算记录
    user_feedback: str  # 用户反馈信息


# ================================================
# 步骤2：定义计算节点
# ================================================
def add_one_node(state: CalculationState) -> CalculationState:
    """加1节点"""
    new_value = state["value"] + 1
    return {"value": new_value, "history": [new_value]}


def add_two_node(state: CalculationState) -> CalculationState:
    """加2节点"""
    new_value = state["value"] + 2
    return {"value": new_value, "history": [new_value]}


def double_node(state: CalculationState) -> CalculationState:
    """乘2节点"""
    new_value = state["value"] * 2
    return {"value": new_value, "history": [new_value]}


# ================================================
# 步骤3：定义人工编辑节点
# ================================================
def human_editing_node(state: CalculationState) -> CalculationState:
    """
    人工编辑节点：中断执行，允许用户查看和修改当前值

    Args:
        state: 当前图状态

    Returns:
        更新后的状态，包含用户输入的值
    """
    # 创建中断请求，包含当前状态信息
    interrupt_request = Interrupt(
        {
            "task": "人工编辑当前值",
            "current_value": state["value"],
            "calculation_history": state["history"],
            "instruction": "请输入新的值，或按Enter保持当前值",
        }
    )

    # 返回中断请求，图执行将在此中断
    return {"user_feedback": "等待人工编辑...", "generated_chat": interrupt_request}


# ================================================
# 步骤4：构建计算图
# ================================================
def build_calculation_graph():
    """构建包含人工编辑节点的计算图"""
    graph = StateGraph(CalculationState)

    # 添加节点
    graph.add_node("add_one", add_one_node)
    graph.add_node("add_two", add_two_node)
    graph.add_node("double", double_node)
    graph.add_node("human_edit", human_editing_node)

    # 设置边关系
    graph.set_entry_point("add_one")
    graph.add_edge("add_one", "add_two")
    graph.add_edge("add_two", "human_edit")  # 执行到这里会中断，等待人工编辑
    graph.add_edge("human_edit", "double")  # 人工编辑完成后继续执行
    graph.add_edge("double", "__end__")  # 最后一个节点

    return graph


# ================================================
# 步骤5：执行图并处理人工编辑
# ================================================
def run_with_human_editing():
    """执行图并演示人工编辑流程"""
    # 构建图并使用MemorySaver保存状态
    graph = build_calculation_graph()
    checkpointer = MemorySaver()
    agent = graph.compile(checkpointer=checkpointer)

    # 配置（用于保存状态）
    config = {"configurable": {"thread_id": "human_editing_example"}}

    # 1. 初始执行：从值1开始
    rprint("\n=== 开始执行计算图 ===")
    try:
        # 执行会在human_editing_node处中断
        result = agent.invoke(
            {"value": 1, "history": [], "user_feedback": ""}, config=config
        )
        rprint("执行完成:", result)
    except Interrupt as e:
        # 2. 处理中断：获取当前状态
        rprint("\n=== 人工编辑阶段 ===")
        rprint(f"中断原因: {e.task}")
        rprint(f"当前值: {e.current_value}")
        rprint(f"计算历史: {e.calculation_history}")

        # 3. 模拟人工输入（实际应用中这里会是用户界面）
        # 这里我们直接设置新值，实际应用中可以替换为input()或其他用户输入方式
        user_input = "10"  # 模拟用户输入新值
        rprint(f"用户输入: {user_input}")

        # 4. 使用update_state更新状态
        if user_input.strip():
            # 用户输入了新值
            new_value = int(user_input.strip())
            rprint(f"更新值为: {new_value}")

            # 获取当前状态快照
            state_snapshot = agent.get_state(config)

            # 更新状态
            updated_config = agent.update_state(
                config,
                {"value": new_value, "user_feedback": f"人工修改值为{new_value}"},
            )

            # 5. 继续执行图
            rprint("\n=== 继续执行计算图 ===")
            final_result = agent.invoke(None, updated_config)
            rprint("最终结果:", final_result)
        else:
            # 用户保持当前值
            rprint("保持当前值，继续执行")
            final_result = agent.invoke(None, config)
            rprint("最终结果:", final_result)


# ================================================
# 步骤6：执行示例
# ================================================
if __name__ == "__main__":
    run_with_human_editing()
# {'value': 8, 'history': [2, 4, 8], 'user_feedback': '等待人工编辑...'}
