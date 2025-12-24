import asyncio
from typing import TypedDict, Annotated
import operator
from langgraph.graph import StateGraph, END, START


# 1. 定义状态和节点
class State(TypedDict):
    value: int
    history: Annotated[list, operator.add]


def add_one(state: State):
    new_val = state["value"] + 1
    return {"value": new_val, "history": [f"Added 1 to get {new_val}"]}


def double(state: State):
    new_val = state["value"] * 2
    return {"value": new_val, "history": [f"Doubled to get {new_val}"]}


# 2. 构建图
builder = StateGraph(State)
builder.add_node("add", add_one)
builder.add_node("double", double)
builder.add_edge(START, "add")
builder.add_edge("add", "double")
builder.add_edge("double", END)

app = builder.compile()


# 3. 使用 astream_events 监控执行
async def monitor_workflow():
    print("开始监控工作流执行事件...\n")

    # 准备初始状态
    input_state = {"value": 5, "history": []}

    # 关键：使用 astream_events 迭代事件
    async for event in app.astream_events(input_state, version="v1"):
        # 提取事件的核心信息
        event_type = event.get("event")
        node_name = event.get("name", "N/A")  # 节点名（如果适用）
        step = event.get("step")  # 执行步骤编号

        # 根据不同事件类型处理
        if event_type in ["on_chain_start", "on_chain_end"]:
            # 链事件（整个工作流或子链）
            data = event.get("data", {})
            print(f"[步骤 {step}] {event_type}: {node_name}")
            if event_type == "on_chain_end" and "output" in data:
                # 输出最终状态
                print(f"    输出状态: {data['output']}")

        elif event_type in ["on_graph_start", "on_graph_end"]:
            # 图级别事件
            print(f"[步骤 {step}] {event_type}")

        elif event_type in ["on_node_start", "on_node_end"]:
            # 节点级别事件（最常用）
            data = event.get("data", {})
            print(f"[步骤 {step}] {event_type}: 节点 '{node_name}'")
            if event_type == "on_node_start" and "input" in data:
                print(f"    输入: {data['input']}")
            if event_type == "on_node_end" and "output" in data:
                print(f"    输出更新: {data['output']}")

    print("\n工作流执行监控结束。")


# 运行
asyncio.run(monitor_workflow())
