# %%
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent

model = ChatOpenAI(model="Qwen/Qwen3-8B", temperature=0)


# 获取天气tool
def get_weather_tool(city: str, arg2):
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


# 初始化agent
agent = create_agent(model=model, tools=[get_weather_tool])
response = agent.invoke({"messages": [("user", "How's the weather in sf?")]})
print(response["messages"][-1].content)
# 'The weather in San Francisco is always sunny! 🌞'

response["messages"][-1]
# AIMessage(
#     content='The weather in San Francisco is always sunny! 🌞',
#     additional_kwargs={'refusal': None},
#     response_metadata={
#         'token_usage': {
#             'completion_tokens': 12,
#             'prompt_tokens': 251,
#             'total_tokens': 263,
#             'completion_tokens_details': {
#                 'accepted_prediction_tokens': None,
#                 'audio_tokens': None,
#                 'reasoning_tokens': 0,
#                 'rejected_prediction_tokens': None
#             },
#             'prompt_tokens_details': None
#         },
#         'model_provider': 'openai',
#         'model_name': 'Qwen/Qwen3-8B',
#         'system_fingerprint': '',
#         'id': '019b4e395e4c406dadfd92877d8eecaa',
#         'finish_reason': 'stop',
#         'logprobs': None
#     },
#     id='lc_run--019b4e39-5de7-72c0-a241-1af51ef6f004-0',
#     usage_metadata={
#         'input_tokens': 251,
#         'output_tokens': 12,
#         'total_tokens': 263,
#         'input_token_details': {},
#         'output_token_details': {'reasoning': 0}
#     }
# )
response["messages"][-2]
# ToolMessage(
#     content="It's always sunny in San Francisco",
#     name='get_weather_tool',
#     id='33af562e-0aa4-49ce-9297-f3f1b66c0a38',
#     tool_call_id='019b4e395dec59c5512f435a1c03eed8'
# )

response["messages"][-3]

# AIMessage(
#     content='',
#     additional_kwargs={'refusal': None},
#     response_metadata={
#         'token_usage': {
#             'completion_tokens': 36,
#             'prompt_tokens': 194,
#             'total_tokens': 230,
#             'completion_tokens_details': {
#                 'accepted_prediction_tokens': None,
#                 'audio_tokens': None,
#                 'reasoning_tokens': 0,
#                 'rejected_prediction_tokens': None
#             },
#             'prompt_tokens_details': None
#         },
#         'model_provider': 'openai',
#         'model_name': 'Qwen/Qwen3-8B',
#         'system_fingerprint': '',
#         'id': '019b4e395645b6f85d4672124c88dbcc',
#         'finish_reason': 'tool_calls',
#         'logprobs': None
#     },
#     id='lc_run--019b4e39-556d-7822-b5bb-fcad0e223360-0',
#     tool_calls=[
#         {
#             'name': 'get_weather_tool',
#             'args': {'city': 'sf', 'arg2': '', 'arg3': '', 'arg4': ''},
#             'id': '019b4e395dec59c5512f435a1c03eed8',
#             'type': 'tool_call'
#         }
#     ],
#     usage_metadata={
#         'input_tokens': 194,
#         'output_tokens': 36,
#         'total_tokens': 230,
#         'input_token_details': {},
#         'output_token_details': {'reasoning': 0}
#     }
# )
# %% prompt 提示词
# 使用prompt参数设置自定义系统提示以进行中文回复
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent


model = ChatOpenAI(model="Qwen/Qwen3-8B", temperature=0)


# 获取天气tool
def get_weather_tool(city: str, arg2):
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


# 初始化agent
# agent = create_agent(model=model, tools=[get_weather_tool], system_prompt="用中文回复")
agent = create_agent(
    model=model, tools=[get_weather_tool], system_prompt="respond in Chinese"
)
response = agent.invoke({"messages": [("user", "How's the weather in sf?")]})
print(response["messages"][-1].content)
# 旧金山（sf）的天气是晴朗的。

response["messages"]
# [
#     HumanMessage(
#         content="How's the weather in sf?",
#         additional_kwargs={},
#         response_metadata={},
#         id='46d43887-2d72-4aa2-b00c-c5762a942cfd'
#     ),
#     AIMessage(
#         content='',
#         additional_kwargs={'refusal': None},
#         response_metadata={
#             'token_usage': {
#                 'completion_tokens': 27,
#                 'prompt_tokens': 180,
#                 'total_tokens': 207,
#                 'completion_tokens_details': {
#                     'accepted_prediction_tokens': None,
#                     'audio_tokens': None,
#                     'reasoning_tokens': 0,
#                     'rejected_prediction_tokens': None
#                 },
#                 'prompt_tokens_details': None
#             },
#             'model_provider': 'openai',
#             'model_name': 'Qwen/Qwen3-8B',
#             'system_fingerprint': '',
#             'id': '019b4e4bdb744b5afbb1dbde5e097da2',
#             'finish_reason': 'tool_calls',
#             'logprobs': None
#         },
#         id='lc_run--019b4e4b-da8c-7c50-bade-05cf689d0c68-0',
#         tool_calls=[
#             {
#                 'name': 'get_weather_tool',
#                 'args': {'city': 'sf', 'arg2': 'weather'},
#                 'id': '019b4e4bdf9b989a1933732da0220a2a',
#                 'type': 'tool_call'
#             }
#         ],
#         usage_metadata={
#             'input_tokens': 180,
#             'output_tokens': 27,
#             'total_tokens': 207,
#             'input_token_details': {},
#             'output_token_details': {'reasoning': 0}
#         }
#     ),
#     ToolMessage(
#         content='sunny',
#         name='get_weather_tool',
#         id='5cf0c073-498a-4263-8152-0c229d436c48',
#         tool_call_id='019b4e4bdf9b989a1933732da0220a2a'
#     ),
#     AIMessage(
#         content='旧金山（SF）的天气是晴朗的。',
#         additional_kwargs={'refusal': None},
#         response_metadata={
#             'token_usage': {
#                 'completion_tokens': 12,
#                 'prompt_tokens': 223,
#                 'total_tokens': 235,
#                 'completion_tokens_details': {
#                     'accepted_prediction_tokens': None,
#                     'audio_tokens': None,
#                     'reasoning_tokens': 0,
#                     'rejected_prediction_tokens': None
#                 },
#                 'prompt_tokens_details': None
#             },
#             'model_provider': 'openai',
#             'model_name': 'Qwen/Qwen3-8B',
#             'system_fingerprint': '',
#             'id': '019b4e4be00f35c928fa81802bc0f3a3',
#             'finish_reason': 'stop',
#             'logprobs': None
#         },
#         id='lc_run--019b4e4b-df8f-74b1-94f8-1426ef3f852e-0',
#         usage_metadata={
#             'input_tokens': 223,
#             'output_tokens': 12,
#             'total_tokens': 235,
#             'input_token_details': {},
#             'output_token_details': {'reasoning': 0}
#         }
#     )
# ]


# %% 添加对话记忆。使用checkpointer参数向智能体添加内存聊天记忆功能

from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver

# 创建具有记忆功能的ReAct智能体
agent = create_agent(
    model=ChatOpenAI(model="Qwen/Qwen3-8B", temperature=0),
    tools=[get_weather_tool],
    checkpointer=InMemorySaver(),
)

# 首次交互
config = {"configurable": {"thread_id": "user_thread_1"}}
inputs1 = {"messages": [("user", "How is the weather in sf?")]}
response1 = agent.invoke(input=inputs1, config=config)
response1["messages"][-1]
# AIMessage(
#     content='The weather in San Francisco is sunny.',
#     additional_kwargs={'refusal': None},
#     response_metadata={
#         'token_usage': {
#             'completion_tokens': 8,
#             'prompt_tokens': 219,
#             'total_tokens': 227,
#             'completion_tokens_details': {
#                 'accepted_prediction_tokens': None,
#                 'audio_tokens': None,
#                 'reasoning_tokens': 0,
#                 'rejected_prediction_tokens': None
#             },
#             'prompt_tokens_details': None
#         },
#         'model_provider': 'openai',
#         'model_name': 'Qwen/Qwen3-8B',
#         'system_fingerprint': '',
#         'id': '019b4e843c855cb406e0e2c33908e3d6',
#         'finish_reason': 'stop',
#         'logprobs': None
#     },
#     id='lc_run--019b4e84-3bf8-75b3-a4d3-75c3d3f14bc9-0',
#     usage_metadata={
#         'input_tokens': 219,
#         'output_tokens': 8,
#         'total_tokens': 227,
#         'input_token_details': {},
#         'output_token_details': {'reasoning': 0}
#     }
# )

# %% 第2次交互
inputs2 = {"messages": [("user", "How is chicago?")]}
response2 = agent.invoke(input=inputs2, config=config)
response2["messages"][-1]
# AIMessage(
#     content="I'm unable to retrieve the weather information for Chicago. Please check the city name or try again later.",
#     additional_kwargs={'refusal': None},
#     response_metadata={
#         'token_usage': {
#             'completion_tokens': 21,
#             'prompt_tokens': 292,
#             'total_tokens': 313,
#             'completion_tokens_details': {
#                 'accepted_prediction_tokens': None,
#                 'audio_tokens': None,
#                 'reasoning_tokens': 0,
#                 'rejected_prediction_tokens': None
#             },
#             'prompt_tokens_details': None
#         },
#         'model_provider': 'openai',
#         'model_name': 'Qwen/Qwen3-8B',
#         'system_fingerprint': '',
#         'id': '019b4e85bc8c0f3475f3acc38e83d0a0',
#         'finish_reason': 'stop',
#         'logprobs': None
#     },
#     id='lc_run--019b4e85-bbf5-78d3-b2c3-d227911a807e-0',
#     usage_metadata={
#         'input_tokens': 292,
#         'output_tokens': 21,
#         'total_tokens': 313,
#         'input_token_details': {},
#         'output_token_details': {'reasoning': 0}
#     }
# )

# %% 第3次交互
inputs3 = {"messages": [("user", "How is nyc?")]}
response3 = agent.invoke(input=inputs3, config=config)
response3["messages"][-1]
# AIMessage(
#     content='The weather in New York City is cloudy.',
#     additional_kwargs={'refusal': None},
#     response_metadata={
#         'token_usage': {
#             'completion_tokens': 9,
#             'prompt_tokens': 372,
#             'total_tokens': 381,
#             'completion_tokens_details': {
#                 'accepted_prediction_tokens': None,
#                 'audio_tokens': None,
#                 'reasoning_tokens': 0,
#                 'rejected_prediction_tokens': None
#             },
#             'prompt_tokens_details': None
#         },
#         'model_provider': 'openai',
#         'model_name': 'Qwen/Qwen3-8B',
#         'system_fingerprint': '',
#         'id': '019b4e86e8883f040a9c39d67a4f419c',
#         'finish_reason': 'stop',
#         'logprobs': None
#     },
#     id='lc_run--019b4e86-e7fd-7713-b9d9-d705f9958103-0',
#     usage_metadata={
#         'input_tokens': 372,
#         'output_tokens': 9,
#         'total_tokens': 381,
#         'input_token_details': {},
#         'output_token_details': {'reasoning': 0}
#     }
# )

# %% 测试
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver

# 创建具有记忆功能的ReAct智能体
agent = create_agent(
    model=ChatOpenAI(model="Qwen/Qwen3-8B", temperature=0),
    tools=[get_weather_tool],
    checkpointer=InMemorySaver(),
)

# 首次交互
config = {"configurable": {"thread_id": "user_thread_1"}}
inputs1 = {"messages": [("user", "How is the weather in nyc?")]}
response1 = agent.invoke(input=inputs1, config=config)
response1["messages"][-1]
# AIMessage(
#     content='The weather in NYC is cloudy.',
#     additional_kwargs={'refusal': None},
#     response_metadata={
#         'token_usage': {
#             'completion_tokens': 7,
#             'prompt_tokens': 221,
#             'total_tokens': 228,
#             'completion_tokens_details': {
#                 'accepted_prediction_tokens': None,
#                 'audio_tokens': None,
#                 'reasoning_tokens': 0,
#                 'rejected_prediction_tokens': None
#             },
#             'prompt_tokens_details': None
#         },
#         'model_provider': 'openai',
#         'model_name': 'Qwen/Qwen3-8B',
#         'system_fingerprint': '',
#         'id': '019b4e893bd830834625a8e6034a35c1',
#         'finish_reason': 'stop',
#         'logprobs': None
#     },
#     id='lc_run--019b4e89-3b36-7f70-9b4e-d52d3a80e6a3-0',
#     usage_metadata={
#         'input_tokens': 221,
#         'output_tokens': 7,
#         'total_tokens': 228,
#         'input_token_details': {},
#         'output_token_details': {'reasoning': 0}
#     }
# )
"""
可以看到，checkpointer应该是起了作用。因为total_tokens增加了很多(上面的例子)。而这个例子仅仅
只有228个。
"""

# %% 使用interrupt_before和checkpointer来启用人机环路

from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
