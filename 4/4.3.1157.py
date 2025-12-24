# %% 人工介入编辑节点示例
from typing import TypedDict, Annotated, Literal
from langgraph.graph import StateGraph
from langgraph.types import Interrupt, Command
from langgraph.checkpoint.memory import MemorySaver
import operator
from rich import print as rprint


# ================================================# 步骤1：定义状态类型
# ================================================
class CalculationState(TypedDict):
    """
    计算图的状态定义

    Attributes:
        value: 当前计算值
        history: 历史计算记录（使用operator.add进行状态合并）
        user_feedback: 用户反馈信息
    """

    value: int
    history: Annotated[list, operator.add]
    user_feedback: str


# ================================================# 步骤2：定义计算节点
# ================================================
def add_one_node(state: CalculationState) -> CalculationState:
    """加1节点：将当前值加1"""
    new_value = state["value"] + 1
    return {
        "value": new_value,
        "history": [new_value],  # 新增历史记录
        "user_feedback": state["user_feedback"],
    }


def multiply_by_two_node(state: CalculationState) -> CalculationState:
    """乘2节点：将当前值乘以2"""
    new_value = state["value"] * 2
    return {
        "value": new_value,
        "history": [new_value],  # 新增历史记录
        "user_feedback": state["user_feedback"],
    }


def subtract_three_node(state: CalculationState) -> CalculationState:
    """减3节点：将当前值减3"""
    new_value = state["value"] - 3
    return {
        "value": new_value,
        "history": [new_value],  # 新增历史记录
        "user_feedback": state["user_feedback"],
    }


# ================================================# 步骤3：定义人工编辑节点
# ================================================
def human_editing_node(
    state: CalculationState,
) -> Command[Literal["subtract_three_node"]]:
    """
    人工编辑节点：中断执行，允许用户查看和修改当前值

    Args:
        state: 当前图状态

    Returns:
        Command: 包含中断指令的Command对象
    """
    # 创建中断请求，包含当前状态信息
    interrupt_request = Interrupt(
        {
            "task": "人工编辑当前计算值",
            "current_value": state["value"],
            "calculation_history": state["history"],
            "instruction": "请输入新的值，或按Enter保持当前值",
            "next_step": "将执行减3操作",
        }
    )

    # 返回中断请求
    return {"user_feedback": "等待人工编辑..."}


# ================================================# 步骤4：构建计算图
# ================================================
def build_calculation_graph():
    """
    构建包含人工编辑节点的计算图

    Returns:
        StateGraph: 构建好的计算图
    """
    graph = StateGraph(CalculationState)

    # 添加所有节点
    graph.add_node("add_one", add_one_node)
    graph.add_node("multiply_by_two", multiply_by_two_node)
    graph.add_node("human_edit", human_editing_node)
    graph.add_node("subtract_three", subtract_three_node)

    # 设置边关系
    graph.set_entry_point("add_one")
    graph.add_edge("add_one", "multiply_by_two")
    graph.add_edge("multiply_by_two", "human_edit")  # 执行到这里会中断，等待人工编辑
    graph.add_edge("human_edit", "subtract_three")  # 人工编辑完成后继续执行
    graph.add_edge("subtract_three", "__end__")  # 最后一个节点

    return graph


# ================================================# 步骤5：执行图并处理人工编辑
# ================================================
def run_with_human_intervention():
    """
    执行图并演示人工编辑流程
    """
    # 构建图并使用MemorySaver保存状态
    graph = build_calculation_graph()
    checkpointer = MemorySaver()
    agent = graph.compile(checkpointer=checkpointer)

    # 配置（用于保存状态）
    config = {"configurable": {"thread_id": "human_intervention_example"}}

    # 1. 初始执行：从值5开始
    rprint("\n=== 开始执行计算图 ===")
    rprint(f"初始值: 5")

    try:
        # 执行会在human_editing_node处中断
        result = agent.invoke(
            {"value": 5, "history": [5], "user_feedback": ""}, config=config
        )
        rprint("执行完成:", result)
    except Exception as e:
        # 查看当前状态
        state_snapshot = agent.get_state(config)

        if state_snapshot.interrupts:
            # 2. 处理中断：显示中断信息并获取用户输入
            rprint("\n=== 人工编辑阶段 ===")
            interrupt_info = state_snapshot.interrupts[0].value

            rprint(f"中断原因: {interrupt_info['task']}")
            rprint(f"当前值: {interrupt_info['current_value']}")
            rprint(f"计算历史: {interrupt_info['calculation_history']}")
            rprint(f"说明: {interrupt_info['instruction']}")
            rprint(f"下一步: {interrupt_info['next_step']}")

            # 3. 获取用户输入
            user_input = input("请输入新的值: ")
            rprint(f"用户输入: {user_input}")

            # 4. 更新状态并继续执行
            if user_input.strip():
                try:
                    # 用户输入了新值
                    new_value = int(user_input.strip())
                    rprint(f"更新值为: {new_value}")

                    # 更新状态
                    updated_config = agent.update_state(
                        config,
                        {
                            "value": new_value,
                            "history": state_snapshot.values["history"] + [new_value],
                            "user_feedback": f"人工修改值为{new_value}",
                        },
                    )
                except ValueError:
                    # 用户输入无效，保持当前值
                    rprint(f"输入无效，保持当前值: {state_snapshot.values['value']}")
                    updated_config = config
            else:
                # 用户保持当前值
                rprint(f"保持当前值: {state_snapshot.values['value']}")
                updated_config = config

            # 5. 继续执行图
            rprint("\n=== 继续执行计算图 ===")
            final_result = agent.invoke(None, updated_config)
            rprint("最终结果:", final_result)
        else:
            # 其他错误
            rprint(f"执行错误: {e}")


# ================================================# 执行示例
# ================================================
if __name__ == "__main__":
    run_with_human_intervention()
