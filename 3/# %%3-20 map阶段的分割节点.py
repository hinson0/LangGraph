# %%3-20 map阶段的分割节点
from langgraph.types import Send
from typing import TypedDict, Annotated, List, Dict, Any
from langgraph.graph import StateGraph, START, END
import operator


# 定义全局状态
class OverallState(TypedDict):
    large_input_data: str
    results: Annotated[List[str], operator.add]  # 用于收集结果的列表


# 定义映射节点状态
class MapNodeState(TypedDict):
    sub_data: str
    results: List[str]  # 用于传递结果


# 实现数据分割函数
def split_large_data(input_data: str, num_sub_stasks: int) -> List[str]:
    """
    将大型字符串数据分割为指定数量的子字符串

    Args:
        input_data: 要分割的大型字符串
        num_sub_stasks: 要创建的子任务数量

    Returns:
        包含分割后子字符串的列表
    """
    if not input_data:
        return []

    # 计算每个子任务的大致长度
    chunk_size = len(input_data) // num_sub_stasks

    # 创建子数据集列表
    sub_datasets = []
    for i in range(num_sub_stasks):
        start = i * chunk_size
        # 最后一个子数据集包含剩余的所有字符
        end = (i + 1) * chunk_size if i < num_sub_stasks - 1 else len(input_data)
        sub_datasets.append(input_data[start:end])

    return sub_datasets


# 定义分割节点
def split_input_data(state: OverallState) -> List[Dict[str, Any]]:
    input_data = state["large_input_data"]
    sub_datasets = split_large_data(input_data, num_sub_stasks=10)
    send_list = []
    for sub_dataset in sub_datasets:
        send_list.append(
            Send("map_node", {"sub_data": sub_dataset, "results": state["results"]})
        )
    return send_list


# 定义映射节点
def map_node(state: MapNodeState) -> Dict[str, Any]:
    sub_data = state["sub_data"]
    # 这里可以实现实际的处理逻辑，例如文本处理、数据分析等
    # 简单示例：将子字符串转换为大写并添加处理标记
    processed_result = f"PROCESSED: {sub_data.upper()}"

    # 获取现有结果并添加新结果
    current_results = state.get("results", [])
    updated_results = current_results.copy()
    updated_results.append(processed_result)

    return {"results": updated_results}


# 定义主函数
def main():
    # 创建状态图
    builder = StateGraph(OverallState)

    # 添加节点
    builder.add_node("split_node", split_input_data)
    builder.add_node("map_node", map_node)

    # 添加边
    builder.add_edge(START, "split_node")
    builder.add_edge("map_node", END)

    # 编译图
    graph = builder.compile()

    # 测试数据
    test_data = (
        "This is a large input data string that needs to be processed in parallel using LangGraph. "
        * 5
    )

    # 运行图
    result = graph.invoke({"large_input_data": test_data, "results": []})

    # 输出结果
    print("Input data length:", len(test_data))
    print("Number of processed chunks:", len(result["results"]))
    print("\nProcessed results:")
    for i, res in enumerate(result["results"]):
        print(f"Chunk {i + 1}: {res}")


if __name__ == "__main__":
    main()
