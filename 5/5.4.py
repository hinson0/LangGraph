# %%
"""
ReAct模式：

    reason: 推理
    act： 行动

将推理与行动动态结合起来。
所谓动态结合agent推理得到结果（依据human的提示词），付诸行动（决策）。然后反馈给human。
human拿到决策，并动态调整结果（进一步给定提示词）。
从而形成一个reason->act->human-in-the-loop->reason->act->human-in-the-loop的有效循环。
使得reason和act不断相互加强。

而传统的AI是僵化的，比如纯粹的推理，或者孤立的行动。
"""

# %% 5-17 使用记忆工具配置ReAct智能体
# from langgraph.prebuilt import create_react_agent
from langchain.agents import create_agent
from langgraph.store.memory import InMemoryStore
from langchain_core.messages import HumanMessage
from langmem import create_manage_memory_tool, create_search_memory_tool

# 创建具有记忆功能的智能体
agent = create_agent(
    "openai:Qwen/Qwen2.5-7B-Instruct",
    tools=[
        create_manage_memory_tool(namespace=("memories",)),
        create_search_memory_tool(namespace=("memories",)),
    ],
    store=InMemoryStore(),
)

# 执行agent，进行简单对话
response = agent.invoke({"messages": [HumanMessage(content="请记住我喜欢编程！")]})
response


# %% 搜索记忆以验证存储
search_result = agent.invoke(
    {"messages": [HumanMessage(content="回忆一下我喜欢什么？")]}
)
search_result
# {
#     'messages': [
#         HumanMessage(
#             content='回忆一下我喜欢什么？',
#             additional_kwargs={},
#             response_metadata={},
#             id='7f05dc4f-c6ee-491e-88aa-08a3be386a1b'
#         ),
#         AIMessage(
#             content='',
#             additional_kwargs={'refusal': None},
#             response_metadata={
#                 'token_usage': {
#                     'completion_tokens': 22,
#                     'prompt_tokens': 465,
#                     'total_tokens': 487,
#                     'completion_tokens_details': {
#                         'accepted_prediction_tokens': None,
#                         'audio_tokens': None,
#                         'reasoning_tokens': 0,
#                         'rejected_prediction_tokens': None
#                     },
#                     'prompt_tokens_details': None
#                 },
#                 'model_provider': 'openai',
#                 'model_name': 'Qwen/Qwen2.5-7B-Instruct',
#                 'system_fingerprint': '',
#                 'id': '019b4df23d546c0ee344bd3860ebe346',
#                 'finish_reason': 'tool_calls',
#                 'logprobs': None
#             },
#             id='lc_run--019b4df2-3c9d-7643-8257-9903a70e8e7a-0',
#             tool_calls=[
#                 {
#                     'name': 'search_memory',
#                     'args': {'query': '喜欢什么'},
#                     'id': '019b4df23f56a84a0a12a8391bf04501',
#                     'type': 'tool_call'
#                 }
#             ],
#             usage_metadata={
#                 'input_tokens': 465,
#                 'output_tokens': 22,
#                 'total_tokens': 487,
#                 'input_token_details': {},
#                 'output_token_details': {'reasoning': 0}
#             }
#         ),
#         ToolMessage(
#             content='[{"namespace":["memories"],"key":"8a4be9fb-46fd-4e66-8c0a-a2bbb5083e8a","value":{"content":"我喜欢编程！"},"created_at":"2025-12-24T01:19:32.752178+00:00","updated_at":"2025-12-24T01:19:32.752182+00:00","score":null}]',
#             name='search_memory',
#             id='a8195145-f523-4c85-8569-9477e585f420',
#             tool_call_id='019b4df23f56a84a0a12a8391bf04501'
#         ),
#         AIMessage(
#             content='您喜欢编程！这是一个新的记忆，我会记住这个信息。如果您有更多关于您的喜好想要分享，随时告诉我。',
#             additional_kwargs={'refusal': None},
#             response_metadata={
#                 'token_usage': {
#                     'completion_tokens': 25,
#                     'prompt_tokens': 627,
#                     'total_tokens': 652,
#                     'completion_tokens_details': {
#                         'accepted_prediction_tokens': None,
#                         'audio_tokens': None,
#                         'reasoning_tokens': 0,
#                         'rejected_prediction_tokens': None
#                     },
#                     'prompt_tokens_details': None
#                 },
#                 'model_provider': 'openai',
#                 'model_name': 'Qwen/Qwen2.5-7B-Instruct',
#                 'system_fingerprint': '',
#                 'id': '019b4df23fa88fd4dddc75196ee1fd43',
#                 'finish_reason': 'stop',
#                 'logprobs': None
#             },
#             id='lc_run--019b4df2-3f4a-78d0-aeef-e06a5b8ff68f-0',
#             usage_metadata={
#                 'input_tokens': 627,
#                 'output_tokens': 25,
#                 'total_tokens': 652,
#                 'input_token_details': {},
#                 'output_token_details': {'reasoning': 0}
#             }
#         )
#     ]
# }


# %% 提示词优化
from langmem import create_prompt_optimizer

optimizer = create_prompt_optimizer(
    "openai:Qwen/Qwen2.5-7B-Instruct",
    kind="prompt_memory",
    config={"max_reflection_steps": 5, "min_reflection_steps": 1},  # type: ignore
)

trajectories = [
    # 没有标注的对话
    (
        [
            {"role": "user", "content": "请告诉我Python的优点"},
            {"role": "assistant", "content": "Python是一种易于学习和使用的编程语言"},
            {"role": "user", "content": "能详细说说他的库支持吗？"},
        ],
        None,
    ),
    # 带有反馈的对话
    (
        [
            {"role": "user", "content": "Python有哪些流行的库"},
            {
                "role": "assistant",
                "content": "Python有很多流行的库，比如NumPy，pandas等",
            },
        ],
        {"score": 0.8, "comment": "可以增加库的应用场景和更多细节"},
    ),
    # 标注内容可以是不同类型
    # (),
]

initial_prompt = "您是一位乐于助人的写作助手"
optimized_prompt = optimizer.invoke(
    {"trajectories": trajectories, "prompt": initial_prompt}
)
optimized_prompt
