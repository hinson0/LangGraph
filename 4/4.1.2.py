import asyncio
from langgraph.graph import StateGraph, MessagesState, END
from langchain_core.messages import HumanMessage


# 定义一个简单的节点函数
async def node_1(state: MessagesState):
    """第一个节点：处理用户消息并返回响应"""
    # 获取最新的人类消息
    human_msg = state["messages"][-1].content
    # 模拟处理逻辑
    response = f"节点1已处理你的消息：{human_msg}"
    # 返回更新后的状态（MessagesState 要求用 messages 字段存储消息）
    return {"messages": [HumanMessage(content=response)]}


async def node_2(state: MessagesState):
    """第二个节点：二次处理消息"""
    last_msg = state["messages"][-1].content
    response = f"节点2再次处理：{last_msg}"
    return {"messages": [HumanMessage(content=response)]}


async def main():
    # 1. 初始化状态图（使用内置的 MessagesState，包含 messages 列表）
    graph_builder = StateGraph(MessagesState)

    # 2. 添加节点
    graph_builder.add_node("node1", node_1)
    graph_builder.add_node("node2", node_2)

    # 3. 设置入口点和边
    graph_builder.set_entry_point("node1")  # 从 node1 开始执行
    graph_builder.add_edge("node1", "node2")  # node1 执行完跳转到 node2
    graph_builder.add_edge("node2", END)  # node2 是结束点

    # 4. 编译图
    graph = graph_builder.compile()

    async for event in graph.astream_events(
        input={"messages": [HumanMessage(content="你好，LangGraph！")]},
        version="v1",  # 必须指定版本（最新文档要求 v1）
        # include_types=["start", "end", "node", "edge"],  # 要获取的事件类型（可选）
    ):
        print(4)
        # 打印事件（根据事件类型处理不同逻辑）
        print(f"事件类型：{event['event']}")
        if event["event"] == "node":
            print(f"  节点名称：{event['name']}")
            print(f"  节点输出：{event['data']['output']}\n")
        elif event["event"] == "edge":
            print(f"  边跳转：{event['data']['source']} -> {event['data']['target']}\n")


asyncio.run(main())
