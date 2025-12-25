# %%
from langgraph.types import Command
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.runnables.config import RunnableConfig

config: RunnableConfig = {"configurable": {"thread_id": "workflow_6"}}


def get_weather_tool(city):
    """use this tool to get the weather information for a city"""
    weather = ""
    match city.lower():
        case "nyc":
            weather = "cloudy"
        case "sf":
            weather = "sunny"
        case _:
            weather = "Unable to get the weather information for this city"
    return weather


# 创建带有中断的智能体
agent = create_agent(
    model=ChatOpenAI(model="Qwen/Qwen3-8B"),
    tools=[get_weather_tool],
    interrupt_before=["tools"],  # 在工具调用前中断
    checkpointer=MemorySaver(),
)

# 启动流程并处理中断
for chunk in agent.stream(
    {"messages": [HumanMessage(content="how is the weather in sf?")]},
    config=config,
    stream_mode="values",
):
    print("当前状态:", chunk)

# 检查当前状态 - 这会显示在何处中断
current_state = agent.get_state(config)
print("中断状态:", current_state)

# 在中断后添加人工输入
human_response = "返回nyc作为工具的参数,并返回工具的结果"  # 这是人工输入的数据
new_message = HumanMessage(content=human_response)

# 更新状态并继续执行
for chunk in agent.stream(
    {"messages": [new_message]},  # 添加人工输入
    config=config,
    stream_mode="values",
):
    print("继续执行状态:", chunk)

chunk["messages"]

# print(agent.get_state(config))

# 或者，可以使用 update_state 方法来更新状态
# agent.update_state(config, {"messages": current_state.values["messages"] + [new_message]})
