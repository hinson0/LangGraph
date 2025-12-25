from langgraph.types import Command
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from langchain.messages import HumanMessage
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


# 假设工作流在human_feedback任务中中断
agent = create_agent(
    model=ChatOpenAI(model="Qwen/Qwen3-8B"),
    tools=[get_weather_tool],
    interrupt_before=["tools"],
    checkpointer=MemorySaver(),
)

for chunk in agent.stream(
    {"messages": [HumanMessage(content="how is the weather in sf?")]},
    config=config,  # type: ignore
    stream_mode="values",
):
    print(chunk)
