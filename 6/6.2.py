# %% 6-12 在Functional API工作流中使用LangChain LLM集成

from langchain_openai import ChatOpenAI
from langgraph.func import task, entrypoint
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.runnables.config import RunnableConfig


@task
def generate_response(user_query: str) -> str:
    llm = ChatOpenAI(model="Qwen/Qwen3-8B", temperature=0)
    response = llm.invoke(user_query)
    return response.content  # type: ignore


@entrypoint(checkpointer=MemorySaver())
def chatbot_workflow(query: str) -> str:
    agent_response = generate_response(query)
    return agent_response.result()


config: RunnableConfig = {"configurable": {"thread_id": "chatbot_1"}}
response = chatbot_workflow.invoke("你好，你好吗？", config=config)
response
# 你好！我很好，谢谢关心！😊 你呢？今天过得怎么样？有什么我可以帮你的吗？'

# %% 6-6 @entrypoint定义
from langgraph.func import task, entrypoint
from langgraph.checkpoint.memory import MemorySaver
from langgraph.store.memory import InMemoryStore
from langgraph.store.base import BaseStore
from langgraph.types import StreamWriter
from langchain_core.runnables import RunnableConfig
from typing import Any


@entrypoint(checkpointer=MemorySaver(), store=InMemoryStore())
def my_workflow(
    user_input: dict,
    *,
    previous: Any = None,
    store: BaseStore,
    writer: StreamWriter,
    config: RunnableConfig,
) -> str:
    api_key_from_config = config.get("configurable", {}).get("api_version")
    writer(
        f"工作流{config.get('metadata', {}).get('thread_id')}，以API版本\
            启动：{api_key_from_config}"
    )

    # 使用注入参数的工作流逻辑
    return f"工作流处理的输入:{user_input}"


# 示例调用
result = my_workflow.invoke(
    {"messages": "hello"}, config={"configurable": {"thread_id": "complex_workflow_1"}}
)
result
# "工作流处理的输入:{'messages': 'hello'}"
# %% 6-7 @task定义

from langgraph.func import task, entrypoint
from langgraph.types import RetryPolicy
from langgraph.checkpoint.memory import MemorySaver


@task(name="task_a", retry_policy=RetryPolicy(max_attempts=2, retry_on=TimeoutError))
def fetch_api_data(url: str) -> dict:
    import time, random

    time.sleep(random.random())
    if random.random() < 0.3:
        rp(1)
        raise TimeoutError("API请求超时")
    return {"status": "success", "data": f"来自{url}的数据"}


@entrypoint(checkpointer=MemorySaver())
def data_processing_workflow(url: str) -> dict:
    api_result = fetch_api_data(url)
    return {"workflow_result": "数据已处理", "api_result": api_result.result()}


result = data_processing_workflow.invoke(
    "https://api.example.com/data",
    config={"configurable": {"thread_id": "thread_id_1"}},
)
result
# 第一种结果
# {'workflow_result': '数据已处理',
#  'api_result': {'status': 'success',
#   'data': '来自https://api.example.com/data的数据'}}


# 第二种结果
# TimeoutError: API请求超时
# During task with name 'data_processing_workflow' and id '87fe9549-f0ec-6182-13d2-27cf5184f4df'


# %% 6-8 包含控制流和任务调用的工作流逻辑

from langgraph.func import task, entrypoint
from langgraph.checkpoint.memory import MemorySaver
from rich import print as rp


@task
def is_even(number: int) -> bool:
    return number % 2 == 0


@task
def multiply_by_2(number: int) -> int:
    return number * 2


@entrypoint(checkpointer=MemorySaver())
def workflow(number: int) -> int:
    if is_even(number).result():
        return multiply_by_2(number).result()
    else:
        return number


config = {"configurable": {"thread_id": "thread_id_1"}}
workflow.invoke(2, config=config)  # type: ignore
workflow.invoke(5, config=config)  # type: ignore

# %% 6-9 使用invoke同步执行工作流
config = {"configurable": {"thread_id": "thread_id_0942"}}
my_workflow.invoke("hello world", config=config)  # type: ignore

# %% 6-10 使用stream流 执行工作流
config = {"configurable": {"thread_id": "thread_id_0944"}}
for chunk in my_workflow.stream(
    ["streaming input1", "streaming input2"], config=config, stream_mode="updates"
):
    print(chunk)

# %% 6-11 使用Command对象恢复工作流
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

agent.get_state(config)

# StateSnapshot(
#     values={
#         'messages': [
#             HumanMessage(
#                 content='how is the weather in sf?',
#                 additional_kwargs={},
#                 response_metadata={},
#                 id='9a4e1000-3c1c-4d31-b3c7-b86f96f8cab1'
#             ),
#             AIMessage(
#                 content='',
#                 additional_kwargs={'refusal': None},
#                 response_metadata={
#                     'token_usage': {
#                         'completion_tokens': 27,
#                         'prompt_tokens': 176,
#                         'total_tokens': 203,
#                         'completion_tokens_details': {
#                             'accepted_prediction_tokens': None,
#                             'audio_tokens': None,
#                             'reasoning_tokens': 0,
#                             'rejected_prediction_tokens': None
#                         },
#                         'prompt_tokens_details': None
#                     },
#                     'model_provider': 'openai',
#                     'model_name': 'Qwen/Qwen3-8B',
#                     'system_fingerprint': '',
#                     'id': '019b54635bdbc917222cfb236b802ab9',
#                     'finish_reason': 'tool_calls',
#                     'logprobs': None
#                 },
#                 id='lc_run--019b5463-5b03-7091-9807-a3db9cf6f8eb-0',
#                 tool_calls=[
#                     {
#                         'name': 'get_weather_tool',
#                         'args': {'city': 'sf', 'arg2': 'temperature'},
#                         'id': '019b54635f72a9f3780245194d1f8632',
#                         'type': 'tool_call'
#                     }
#                 ],
#                 usage_metadata={
#                     'input_tokens': 176,
#                     'output_tokens': 27,
#                     'total_tokens': 203,
#                     'input_token_details': {},
#                     'output_token_details': {'reasoning': 0}
#                 }
#             )
#         ]
#     },
#     next=('tools',),
#     config={
#         'configurable': {
#             'thread_id': 'workflow_6',
#             'checkpoint_ns': '',
#             'checkpoint_id': '1f0e1627-d440-6dfa-8001-8e619622aff9'
#         }
#     },
#     metadata={'source': 'loop', 'step': 1, 'parents': {}},
#     created_at='2025-12-25T07:22:37.314180+00:00',
#     parent_config={
#         'configurable': {
#             'thread_id': 'workflow_6',
#             'checkpoint_ns': '',
#             'checkpoint_id': '1f0e1627-c933-6c3c-8000-7910c7de5222'
#         }
#     },
#     tasks=(
#         PregelTask(
#             id='43f72415-707f-8cc3-98ba-ef1808efd0b6',
#             name='tools',
#             path=('__pregel_push', 0, False),
#             error=None,
#             interrupts=(),
#             state=None,
#             result=None
#         ),
#     ),
#     interrupts=()
# )

resume_command = Command(resume="nyc")
for chunk in agent.stream(                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       , config=config):  # type: ignore
    print(chunk)




