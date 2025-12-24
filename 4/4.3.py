# %% 4-21 使用interrupt_before设置静态断点
from typing import TypedDict, Annotated
from langgraph.graph import StateGraph
from langgraph.checkpoint.memory import MemorySaver
import operator


class MyState(TypedDict):  # type: ignore
    value: int
    history: Annotated[list, operator.add]


def add_one_node(state: MyState):
    return {"value": state["value"] + 1, "history": [state["value"] + 1]}


def add_two_node(state: MyState):
    return {"value": state["value"] + 2, "history": [state["value"] + 2]}


def double_node(state: MyState):
    return {"value": state["value"] * 2, "history": [state["value"] * 2]}


def triple_node(state: MyState):
    return {"value": state["value"] * 3, "history": [state["value"] * 3]}


graph = StateGraph(MyState)
graph.add_node(add_one_node)
graph.add_node(add_two_node)
graph.add_node(double_node)
graph.add_node(triple_node)
graph.set_entry_point(add_one_node.__name__)
graph.add_edge(add_one_node.__name__, add_two_node.__name__)
graph.add_edge(add_two_node.__name__, double_node.__name__)
graph.add_edge(double_node.__name__, triple_node.__name__)
graph.set_finish_point(triple_node.__name__)

# Set static breakpoint before specific nodes
# interrupt_before: pause execution before these nodes run
config = {"configurable": {"thread_id": "test_1"}}
agent = graph.compile(checkpointer=MemorySaver(), interrupt_before=["double_node"])
agent.get_state(config)  # type: ignore

# %%
# First execution: provide initial state
for chunk in agent.stream(
    {"value": 1, "history": []},
    config={"configurable": {"thread_id": "test_1"}},
    stream_mode="values",
):
    print(chunk)

# After hitting the breakpoint, resume with None
# for chunk in agent.stream(
#     None, config={"configurable": {"thread_id": "test_1"}}, stream_mode="values"
# ):
#     print(chunk)


# Example usage:
# config = {"configurable": {"thread_id": "test_1"}}
# result = agent.invoke({"value": 1, "history": []}, config)
# # Execution will pause before double_node
# # Check state: state = agent.get_state(config)
# # Resume: agent.invoke(None, config)  # Pass None to continue

# %% 使用interrupt()函数的”人工审批节点“以及基于人工输入（批准/拒绝）的路由逻辑

from typing import Literal, TypedDict
from langgraph.graph import StateGraph
from langgraph.types import interrupt, Command
from langgraph.checkpoint.memory import MemorySaver


class MyState(TypedDict):
    topic: str
    proposed_action_details: str


def propose_action_node(state: MyState) -> MyState:
    return {**state, "proposed_action_details": f"基于主题{state['topic']}的操作提议"}


def human_approval_node(
    state: MyState,
) -> Command[Literal["execute_action_node", "revise_action_node"]]:
    approval_request = interrupt(
        {
            "question": "Approve the execution of the following action?",
            "action_details": state["proposed_action_details"],
        }
    )

    if approval_request["user_response"] == "approve":
        return Command(goto="execute_action_node")
    else:
        return Command(goto="revise_action_node")


def execute_action_node(state: MyState) -> MyState:
    return {
        **state,
        "proposed_action_details": f"已执行操作:{state['proposed_action_details']}",
    }


def revise_action_node(state: MyState) -> MyState:
    return {
        **state,
        "proposed_action_details": f"修改后的操作:{state['proposed_action_details']}(已调整)",
    }


# 构建图
graph = StateGraph(MyState)
graph.add_node(propose_action_node)
graph.add_node(human_approval_node)
graph.add_node(execute_action_node)
graph.add_node(revise_action_node)
graph.set_entry_point(propose_action_node.__name__)
graph.add_edge(propose_action_node.__name__, human_approval_node.__name__)
graph.add_edge(revise_action_node.__name__, human_approval_node.__name__)
agent = graph.compile(checkpointer=MemorySaver())

# 执行图
config = {"configurable": {"thread_id": "approval_thread"}}
agent.invoke({"topic": "重要决策"}, config=config)
agent.get_state(config)
# StateSnapshot(
#     values={'topic': '重要决策', 'proposed_action_details': '基于主题重要决策的操作提议'},
#     next=('human_approval_node',),
#     config={
#         'configurable': {
#             'thread_id': 'approval_thread',
#             'checkpoint_ns': '',
#             'checkpoint_id': '1f0ded1a-8399-6568-8001-2eaeda9c2b96'
#         }
#     },
#     metadata={'source': 'loop', 'step': 1, 'parents': {}},
#     created_at='2025-12-22T01:00:50.036256+00:00',
#     parent_config={
#         'configurable': {
#             'thread_id': 'approval_thread',
#             'checkpoint_ns': '',
#             'checkpoint_id': '1f0ded1a-8398-68d4-8000-7e46db229364'
#         }
#     },
#     tasks=(
#         PregelTask(
#             id='a49d4bb9-d1bd-93ed-3844-214d5893f93f',
#             name='human_approval_node',
#             path=('__pregel_pull', 'human_approval_node'),
#             error=None,
#             interrupts=(
#                 Interrupt(
#                     value={
#                         'question': 'Approve the execution of the following action?',
#                         'action_details': '基于主题重要决策的操作提议'
#                     },
#                     id='15a6eff132506720fadc3c311c280256'
#                 ),
#             ),
#             state=None,
#             result=None
#         ),
#     ),
#     interrupts=(
#         Interrupt(
#             value={
#                 'question': 'Approve the execution of the following action?',
#                 'action_details': '基于主题重要决策的操作提议'
#             },
#             id='15a6eff132506720fadc3c311c280256'
#         ),
#     )
# )

# %% 恢复图执行，决绝提议
agent.invoke(Command(resume={"user_response": "deny"}), config)
agent.get_state(config)
# StateSnapshot(
#     values={
#         'topic': '重要决策',
#         'proposed_action_details': '修改后的操作:基于主题重要决策的操作提议(已调整)'
#     },
#     next=('human_approval_node',),
#     config={
#         'configurable': {
#             'thread_id': 'approval_thread',
#             'checkpoint_ns': '',
#             'checkpoint_id': '1f0ded2e-08f9-69ca-8003-1c09f9797350'
#         }
#     },
#     metadata={'source': 'loop', 'step': 3, 'parents': {}},
#     created_at='2025-12-22T01:09:34.049113+00:00',
#     parent_config={
#         'configurable': {
#             'thread_id': 'approval_thread',
#             'checkpoint_ns': '',
#             'checkpoint_id': '1f0ded2e-08f8-682c-8002-d2bb5d6a1e9b'
#         }
#     },
#     tasks=(
#         PregelTask(
#             id='06a97ba3-bd5d-531d-3539-57d447cc3a05',
#             name='human_approval_node',
#             path=('__pregel_pull', 'human_approval_node'),
#             error=None,
#             interrupts=(
#                 Interrupt(
#                     value={
#                         'question': 'Approve the execution of the following action?',
#                         'action_details': '修改后的操作:基于主题重要决策的操作提议(已调整)'
#                     },
#                     id='897f4867e90f5e9af8e4f29986925088'
#                 ),
#             ),
#             state=None,
#             result=None
#         ),
#     ),
#     interrupts=(
#         Interrupt(
#             value={
#                 'question': 'Approve the execution of the following action?',
#                 'action_details': '修改后的操作:基于主题重要决策的操作提议(已调整)'
#             },
#             id='897f4867e90f5e9af8e4f29986925088'
#         ),
#     )

# %% 恢复图执行，批准提议
agent.invoke(Command(resume={"user_response": "approve"}), config)
agent.get_state(config)
# StateSnapshot(
#     values={
#         'topic': '重要决策',
#         'proposed_action_details': '已执行操作:修改后的操作:基于主题重要决策的操作提议(已调整)'
#     },
#     next=(),
#     config={
#         'configurable': {
#             'thread_id': 'approval_thread',
#             'checkpoint_ns': '',
#             'checkpoint_id': '1f0ded33-72b1-6dae-8005-6679bcc9a288'
#         }
#     },
#     metadata={'source': 'loop', 'step': 5, 'parents': {}},
#     created_at='2025-12-22T01:11:59.352350+00:00',
#     parent_config={
#         'configurable': {
#             'thread_id': 'approval_thread',
#             'checkpoint_ns': '',
#             'checkpoint_id': '1f0ded33-72af-6ee6-8004-aff50b9d8fb8'
#         }
#     },
#     tasks=(),
#     interrupts=()
# )


# %% 使用interrupt()函数的 "人工编辑节点"以及使用人工编辑的值更新图状态

from langgraph.types import Interrupt, Command
from typing import TypedDict, Annotated
from langgraph.graph import StateGraph
from langgraph.checkpoint.memory import MemorySaver
import operator


class MyState(TypedDict):  # type: ignore
    value: int
    history: Annotated[list, operator.add]


def add_one_node(state: MyState):
    return {"value": state["value"] + 1, "history": [state["value"] + 1]}


def add_two_node(state: MyState):
    return {"value": state["value"] + 2, "history": [state["value"] + 2]}


def double_node(state: MyState):
    return {"value": state["value"] * 2, "history": [state["value"] * 2]}


def triple_node(state: MyState):
    return {"value": state["value"] * 3, "history": [state["value"] * 3]}


def human_editing_node(state: MyState):
    generated_chat = Interrupt(
        {"task": "审阅下当前的值", "current_value": state.get("value")}
    )
    return {"generated_chat": generated_chat}


graph = StateGraph(MyState)
graph.add_node(add_one_node)
graph.add_node(add_two_node)
graph.add_node(double_node)
graph.add_node(triple_node)
graph.add_node(human_editing_node)

graph.set_entry_point(add_one_node.__name__)
graph.add_edge(add_one_node.__name__, add_two_node.__name__)
graph.add_edge(add_two_node.__name__, human_editing_node.__name__)
graph.add_edge(add_two_node.__name__, double_node.__name__)
graph.add_edge(double_node.__name__, triple_node.__name__)
graph.set_finish_point(triple_node.__name__)

agent = graph.invoke(Command())


# %% 使用interrupt()函数的"人工编辑节点"完整示例
from langgraph.types import Interrupt, Command, interrupt
from typing import TypedDict, Annotated, Literal
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
def human_editing_node(state: CalculationState) -> Command[Literal["double"]]:
    """
    人工编辑节点：中断执行，允许用户查看和修改当前值

    Args:
        state: 当前图状态

    Returns:
        包含中断指令的Command对象
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

    # 返回中断请求
    return {"user_feedback": "等待人工编辑..."}


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

    # 执行会在human_editing_node处中断
    try:
        result = agent.invoke(
            {"value": 1, "history": [], "user_feedback": ""}, config=config
        )
        rprint("执行完成:", result)
    except Exception as e:
        # 查看当前状态
        state_snapshot = agent.get_state(config)

        if state_snapshot.interrupts:
            # 2. 处理中断：显示中断信息并获取用户输入.
            rprint("\n=== 人工编辑阶段 ===")
            interrupt_info = state_snapshot.interrupts[0].value
            rprint(f"中断原因: {interrupt_info['task']}")
            rprint(f"当前值: {interrupt_info['current_value']}")
            rprint(f"计算历史: {interrupt_info['calculation_history']}")
            rprint(f"说明: {interrupt_info['instruction']}")

            # 3. 获取用户输入（实际交互）
            user_input = input("请输入新的值：")
            rprint(f"用户输入: {user_input}")

            # 4. 更新状态并继续执行
            if user_input.strip():
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

                # 5. 继续执行图
                rprint("\n=== 继续执行计算图 ===")
                final_result = agent.invoke(None, updated_config)
                rprint("最终结果:", final_result)
            else:
                # 用户保持当前值
                rprint("保持当前值，继续执行")
                final_result = agent.invoke(None, config)
                rprint("最终结果:", final_result)
        else:
            # 其他错误
            rprint(f"执行错误: {e}")


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

    # 编译图时设置中断点
    return graph


# ================================================
# 步骤6：执行示例
# ================================================
if __name__ == "__main__":
    run_with_human_editing()


# %%
from langgraph.types import Interrupt, Command, interrupt
from typing import TypedDict, Annotated, Literal
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
def human_editing_node(state: CalculationState) -> Command[Literal["double"]]:
    """
    人工编辑节点：中断执行，允许用户查看和修改当前值

    Args:
        state: 当前图状态

    Returns:
        包含中断指令的Command对象
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

    # 返回中断请求
    return {"user_feedback": "等待人工编辑..."}


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

    # 执行会在human_editing_node处中断
    try:
        result = agent.invoke(
            {"value": 1, "history": [], "user_feedback": ""}, config=config
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

            # 3. 获取用户输入（实际交互）
            user_input = input("请输入新的值：")
            rprint(f"用户输入: {user_input}")

            # 4. 更新状态并继续执行
            if user_input.strip():
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

                # 5. 继续执行图
                rprint("\n=== 继续执行计算图 ===")
                final_result = agent.invoke(None, updated_config)
                rprint("最终结果:", final_result)
            else:
                # 用户保持当前值
                rprint("保持当前值，继续执行")
                final_result = agent.invoke(None, config)
                rprint("最终结果:", final_result)
        else:
            # 其他错误
            rprint(f"执行错误: {e}")


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

    # 编译图时设置中断点
    return graph


# %% 完整的人工介入编辑节点示例 - 使用 interrupt() 函数
from langgraph.types import interrupt, Command
from typing import TypedDict, Annotated
from langgraph.graph import StateGraph
from langgraph.checkpoint.memory import MemorySaver
import operator


class DocumentState(TypedDict):
    """Document processing state"""

    content: str  # Document content
    edited_content: str  # Edited content
    history: Annotated[list, operator.add]  # Edit history


def generate_content_node(state: DocumentState) -> DocumentState:
    """Generate initial content node"""
    initial_content = f"这是自动生成的文档内容，当前状态: {state.get('content', '')}"
    return {
        "content": initial_content,
        "edited_content": initial_content,
        "history": [f"生成内容: {initial_content}"],
    }


def human_edit_node(state: DocumentState) -> Command:
    """
    Human editing node: interrupt execution and allow user to edit content

    Use interrupt() function to create an interrupt, waiting for user input
    """
    # Create interrupt, pass current content to user
    user_response = interrupt(
        {
            "message": "请编辑以下内容",
            "current_content": state["content"],
            "instruction": "输入新的内容，或输入 'skip' 跳过编辑",
        }
    )

    # Decide next step based on user response
    if (
        user_response.get("edited_content")
        and user_response["edited_content"] != "skip"
    ):
        # User provided new content, update state and continue
        return Command(
            update={
                "edited_content": user_response["edited_content"],
                "history": [f"人工编辑: {user_response['edited_content']}"],
            }
        )
    else:
        # User skipped editing, keep original content
        return Command(
            update={
                "edited_content": state["content"],
                "history": ["跳过编辑，保持原内容"],
            }
        )


def review_node(state: DocumentState) -> DocumentState:
    """Review node: process edited content"""
    review_message = f"审查完成: {state['edited_content']}"
    return {**state, "history": [review_message]}


def build_document_graph():
    """Build document processing graph"""
    graph = StateGraph(DocumentState)

    # Add nodes
    graph.add_node("generate", generate_content_node)
    graph.add_node("human_edit", human_edit_node)
    graph.add_node("review", review_node)

    # Set edge relationships
    graph.set_entry_point("generate")
    graph.add_edge("generate", "human_edit")
    graph.add_edge("human_edit", "review")
    graph.add_edge("review", "__end__")

    return graph


# Execution example
def run_document_editing_example():
    """Run document editing example"""
    graph = build_document_graph()
    checkpointer = MemorySaver()
    agent = graph.compile(checkpointer=checkpointer)

    config = {"configurable": {"thread_id": "doc_editing_1"}}

    print("\n=== 开始执行文档处理图 ===")

    # Initial execution, will interrupt at human_edit node
    try:
        result = agent.invoke(
            {"content": "", "edited_content": "", "history": []}, config=config
        )
        print("执行完成:", result)
    except Exception:
        # Get current state
        state_snapshot = agent.get_state(config)

        if state_snapshot.interrupts:
            print("\n=== 人工编辑阶段 ===")
            interrupt_info = state_snapshot.interrupts[0].value
            print(f"消息: {interrupt_info['message']}")
            print(f"当前内容: {interrupt_info['current_content']}")
            print(f"说明: {interrupt_info['instruction']}")

            # Get user input
            user_input = input("\n请输入编辑后的内容（或输入 'skip' 跳过）: ")

            # Resume execution with user-edited content
            final_result = agent.invoke(
                Command(resume={"edited_content": user_input}), config=config
            )

            print("\n=== 最终结果 ===")
            print(f"编辑后的内容: {final_result['edited_content']}")
            print(f"编辑历史: {final_result['history']}")


# If running this file directly, execute example
if __name__ == "__main__":
    run_document_editing_example()


# %%
