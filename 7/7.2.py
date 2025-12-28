# %%7-11 使用LangGraph Supervisor类搭建具有数学智能体和研究智能体的主管架构

from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from langgraph_supervisor import create_supervisor

llm = ChatOpenAI(model="Qwen/Qwen3-8B")


def add(one: float, two: float) -> float:
    """一个加法工具"""
    return one + two


def multiply(number: float, number2: float) -> float:
    """一个乘法工具"""
    return number * number2


math_agent = create_agent(
    model=llm,
    name="math_expert",
    tools=[add, multiply],
    system_prompt="你是一个数学专家，始终使用一个工具",
)


def web_search(input: str) -> str:
    """在网络上搜索信息"""
    return (
        "2025年FAANG的员工数量如下---：\n"
        "Meta(原Facebook)，78,450 人，2025 年 Q3 末（财报数据，含全职）\n"
        "Amazon（亚马逊）	1,556,000 人	2025 年《财富》世界 500 强口径（含全职 / 兼职 / 子公司）\n"
        "Apple（苹果）	166,000 人	2025 财年末（9 月 27 日，财报数据）\n"
        "Netflix（奈飞）	约 12,000 人	2025 年公开披露（行业统计口径，含核心团队）\n"
        "Alphabet（谷歌母公司）	190,167 人	2025 年 Q3 末（财报数据，含全子公司）"
    )


research_agent = create_agent(
    model=llm,
    name="research_expert",
    tools=[web_search],
    system_prompt="你是一个是世界一流的研究专家，可以进行网络搜索，不要做任何数学计算",
)

supervisor = create_supervisor(
    [math_agent, research_agent],
    model=llm,
    prompt="你是一位团队主管，管理一位研究专家和一位数学专家。研究专家可以使用网络搜索工具进行查询",
)
app = supervisor.compile()
messages = [("user", "2025年FAANG公司有多少员工数量?")]
response = app.invoke({"messages": messages})
print(response["messages"][-1].content)

# %% the 3rd result
""" 

2025年FAANG公司（Facebook/ Meta、Amazon、Apple、Netflix、Alphabet）的员工数量如下：

1. **Meta（原Facebook）**：约78,450人（2025年第三季度末，含全职员工）。
2. **Amazon（亚马逊）**：约1,556,000人（2025年《财富》世界500强统计口径，含全职、兼职及子公司员工）。
3. **Apple（苹果）**：约166,000人（2025财年末，即9月27日，财报数据）。
4. **Netflix（奈飞）**：约12,000人（2025年公开披露数据，含核心团队）。
5. **Alphabet（谷歌母公司）**：约190,167人（2025年第三季度末，含全子公司员工）。

总计：大约 **2,380,000** 名员工（以上数据基于各公司的财报或公开披露信息，可能因统计口径或子公司范围略有差异）。如果需要更精确的数据或进一步分析，可以告诉我


{
    'messages': [
        HumanMessage(
            content='2025年FAANG公司有多少员工数量?',
            additional_kwargs={},
            response_metadata={},
            id='0a47e6a5-8f99-4f01-8738-1225c7c896ed'
        ),
        AIMessage(
            content='',
            additional_kwargs={'refusal': None},
            response_metadata={
                'token_usage': {
                    'completion_tokens': 19,
                    'prompt_tokens': 233,
                    'total_tokens': 252,
                    'completion_tokens_details': {
                        'accepted_prediction_tokens': None,
                        'audio_tokens': None,
                        'reasoning_tokens': 0,
                        'rejected_prediction_tokens': None
                    },
                    'prompt_tokens_details': None
                },
                'model_provider': 'openai',
                'model_name': 'Qwen/Qwen3-8B',
                'system_fingerprint': '',
                'id': '019b6003efcb0f33f32c31b8f3c346d0',
                'finish_reason': 'tool_calls',
                'logprobs': None
            },
            name='supervisor',
            id='lc_run--019b6003-eea2-7241-8fa8-fb778e41d0a3-0',
            tool_calls=[
                {
                    'name': 'transfer_to_research_expert',
                    'args': {},
                    'id': '019b6003f33aadff3bee9770f5d01922',
                    'type': 'tool_call'
                }
            ],
            usage_metadata={
                'input_tokens': 233,
                'output_tokens': 19,
                'total_tokens': 252,
                'input_token_details': {},
                'output_token_details': {'reasoning': 0}
            }
        ),
        ToolMessage(
            content='Successfully transferred to research_expert',
            name='transfer_to_research_expert',
            id='b8db845e-c105-4d80-b913-78e6e939f968',
            tool_call_id='019b6003f33aadff3bee9770f5d01922'
        ),
        AIMessage(
            content='2025年FAANG公司的员工数量如下：\n\n1. **Meta（原Facebook）**：约78,450人（2025年第三季度末，含全职员工）。\n2. **Amazon（亚马逊）**：约1,556,000人（2025年《财富》世界500强统计口径，含全职、兼职及子公司员工）。\n3. **Apple（苹果）**：约166,000人（2025财年末，即9月27日，财报数据）。\n4. **Netflix（奈飞）**：约12,000人（2025年公开披露数据，含核心团队）。\n5. **Alphabet（谷歌母公司）**：约190,167人（2025年第三季度末，含全子公司员工）。\n\n请注意，这些数据是基于各公司的财报或公开披露信息，可能因统计口径、子公司范围或时间点的不同而略有差异。',
            additional_kwargs={'refusal': None},
            response_metadata={
                'token_usage': {
                    'completion_tokens': 226,
                    'prompt_tokens': 457,
                    'total_tokens': 683,
                    'completion_tokens_details': {
                        'accepted_prediction_tokens': None,
                        'audio_tokens': None,
                        'reasoning_tokens': 0,
                        'rejected_prediction_tokens': None
                    },
                    'prompt_tokens_details': None
                },
                'model_provider': 'openai',
                'model_name': 'Qwen/Qwen3-8B',
                'system_fingerprint': '',
                'id': '019b6003fb1a80f6178d70ee7838b3e9',
                'finish_reason': 'stop',
                'logprobs': None
            },
            name='research_expert',
            id='lc_run--019b6003-fa66-7253-879a-655452a38c2f-0',
            usage_metadata={
                'input_tokens': 457,
                'output_tokens': 226,
                'total_tokens': 683,
                'input_token_details': {},
                'output_token_details': {'reasoning': 0}
            }
        ),
        AIMessage(
            content='Transferring back to supervisor',
            additional_kwargs={},
            response_metadata={'__is_handoff_back': True},
            name='research_expert',
            id='b6e2841d-3012-4801-9f10-58be9c545878',
            tool_calls=[
                {
                    'name': 'transfer_back_to_supervisor',
                    'args': {},
                    'id': '12ce7b38-2920-49d5-babc-289a085effab',
                    'type': 'tool_call'
                }
            ]
        ),
        ToolMessage(
            content='Successfully transferred back to supervisor',
            name='transfer_back_to_supervisor',
            id='800daed2-8dda-4d15-ac1f-ba3e40fbf1ff',
            tool_call_id='12ce7b38-2920-49d5-babc-289a085effab'
        ),
        AIMessage(
            content='2025年FAANG公司（Facebook/ Meta、Amazon、Apple、Netflix、Alphabet）的员工数量如下：\n\n1. **Meta（原Facebook）**：约78,450人（2025年第三季度末，含全职员工）。\n2. **Amazon（亚马逊）**：约1,556,000人（2025年《财富》世界500强统计口径，含全职、兼职及子公司员工）。\n3. **Apple（苹果）**：约166,000人（2025财年末，即9月27日，财报数据）。\n4. **Netflix（奈飞）**：约12,000人（2025年公开披露数据，含核心团队）。\n5. **Alphabet（谷歌母公司）**：约190,167人（2025年第三季度末，含全子公司员工）。\n\n总计：大约 **2,380,000** 名员工（以上数据基于各公司的财报或公开披露信息，可能因统计口径或子公司范围略有差异）。如果需要更精确的数据或进一步分析，可以告诉我！',
            additional_kwargs={'refusal': None},
            response_metadata={
                'token_usage': {
                    'completion_tokens': 262,
                    'prompt_tokens': 547,
                    'total_tokens': 809,
                    'completion_tokens_details': {
                        'accepted_prediction_tokens': None,
                        'audio_tokens': None,
                        'reasoning_tokens': 0,
                        'rejected_prediction_tokens': None
                    },
                    'prompt_tokens_details': None
                },
                'model_provider': 'openai',
                'model_name': 'Qwen/Qwen3-8B',
                'system_fingerprint': '',
                'id': '019b600421f2b0f68492a231d526b4fc',
                'finish_reason': 'stop',
                'logprobs': None
            },
            name='supervisor',
            id='lc_run--019b6004-2160-7d61-91bc-feb9a686f56f-0',
            usage_metadata={
                'input_tokens': 547,
                'output_tokens': 262,
                'total_tokens': 809,
                'input_token_details': {},
                'output_token_details': {'reasoning': 0}
            }
        )
    ]
}

 """

# %% the 2nd result
""" 

FAANG公司（Facebook、Apple、Amazon、Netflix和Google的母公司Alphabet）的员工总数大致估算为约 **1,910,000人**，但需要注意的是，这个数字是基于不同公司公开数据和统计口径的粗略总和，可能会因统计时间、是否包含子公司、兼职员工等因素存在差异。

如果你有更具体的统计需求或需要更详细的数据，可以进一步说明，我会尽力协助。


{
    'messages': [
        HumanMessage(
            content='现在FAANG公司有多少员工?',
            additional_kwargs={},
            response_metadata={},
            id='64ffc462-ae61-45d6-9a12-b290d324be60'
        ),
        AIMessage(
            content='',
            additional_kwargs={'refusal': None},
            response_metadata={
                'token_usage': {
                    'completion_tokens': 19,
                    'prompt_tokens': 228,
                    'total_tokens': 247,
                    'completion_tokens_details': {
                        'accepted_prediction_tokens': None,
                        'audio_tokens': None,
                        'reasoning_tokens': 0,
                        'rejected_prediction_tokens': None
                    },
                    'prompt_tokens_details': None
                },
                'model_provider': 'openai',
                'model_name': 'Qwen/Qwen3-8B',
                'system_fingerprint': '',
                'id': '019b5ffed2786458fa4035a44887e056',
                'finish_reason': 'tool_calls',
                'logprobs': None
            },
            name='supervisor',
            id='lc_run--019b5ffe-d176-7903-bc3b-1c9877eb05a5-0',
            tool_calls=[
                {
                    'name': 'transfer_to_research_expert',
                    'args': {},
                    'id': '019b5ffed6c4667a89b7c9d2d7057576',
                    'type': 'tool_call'
                }
            ],
            usage_metadata={
                'input_tokens': 228,
                'output_tokens': 19,
                'total_tokens': 247,
                'input_token_details': {},
                'output_token_details': {'reasoning': 0}
            }
        ),
        ToolMessage(
            content='Successfully transferred to research_expert',
            name='transfer_to_research_expert',
            id='0762b3e0-b5a4-4712-b97a-9c93e1916329',
            tool_call_id='019b5ffed6c4667a89b7c9d2d7057576'
        ),
        AIMessage(
            content='FAANG公司员工总数的估算如下：\n\n- **Meta（原Facebook）**：约78,450人（截至2025年Q3末，含全职员工）\n- **Amazon（亚马逊）**：约1,556,000人（截至2025年《财富》世界500强统计口径，含全职、兼职及子公司员工）\n- **Apple（苹果）**：约166,000人（截至2025财年末，9月27日，财报数据）\n- **Netflix（奈飞）**：约12,000人（截至2025年公开披露数据，行业统计口径，含核心团队）\n- **Alphabet（谷歌母公司）**：约190,167人（截至2025年Q3末，含全子公司员工）\n\n如果将这些数据相加，FAANG公司的总员工人数大约为 **1,910,000人**（注：此为粗略估算，具体数字可能因统计口径不同而有所差异）。',
            additional_kwargs={'refusal': None},
            response_metadata={
                'token_usage': {
                    'completion_tokens': 241,
                    'prompt_tokens': 447,
                    'total_tokens': 688,
                    'completion_tokens_details': {
                        'accepted_prediction_tokens': None,
                        'audio_tokens': None,
                        'reasoning_tokens': 0,
                        'rejected_prediction_tokens': None
                    },
                    'prompt_tokens_details': None
                },
                'model_provider': 'openai',
                'model_name': 'Qwen/Qwen3-8B',
                'system_fingerprint': '',
                'id': '019b5ffedc51b67ff6ea6758167cedd9',
                'finish_reason': 'stop',
                'logprobs': None
            },
            name='research_expert',
            id='lc_run--019b5ffe-dba4-7a63-a9c6-e2e98ce58451-0',
            usage_metadata={
                'input_tokens': 447,
                'output_tokens': 241,
                'total_tokens': 688,
                'input_token_details': {},
                'output_token_details': {'reasoning': 0}
            }
        ),
        AIMessage(
            content='Transferring back to supervisor',
            additional_kwargs={},
            response_metadata={'__is_handoff_back': True},
            name='research_expert',
            id='4fe15ff3-96d0-4255-b2a5-65ef47387bb1',
            tool_calls=[
                {
                    'name': 'transfer_back_to_supervisor',
                    'args': {},
                    'id': '2468a619-f516-4d78-97e3-c3e5fadbadf6',
                    'type': 'tool_call'
                }
            ]
        ),
        ToolMessage(
            content='Successfully transferred back to supervisor',
            name='transfer_back_to_supervisor',
            id='d50dfb0a-f246-4080-9356-0599a8f8a896',
            tool_call_id='2468a619-f516-4d78-97e3-c3e5fadbadf6'
        ),
        AIMessage(
            content='FAANG公司（Facebook、Apple、Amazon、Netflix和Google的母公司Alphabet）的员工总数大致估算为约 **1,910,000人**，但需要注意的是，这个数字是基于不同公司公开数据和统计口径的粗略总和，可能会因统计时间、是否包含子公司、兼职员工等因素存在差异。\n\n如果你有更具体的统计需求或需要更详细的数据，可以进一步说明，我会尽力协助。',
            additional_kwargs={'refusal': None},
            response_metadata={
                'token_usage': {
                    'completion_tokens': 94,
                    'prompt_tokens': 557,
                    'total_tokens': 651,
                    'completion_tokens_details': {
                        'accepted_prediction_tokens': None,
                        'audio_tokens': None,
                        'reasoning_tokens': 0,
                        'rejected_prediction_tokens': None
                    },
                    'prompt_tokens_details': None
                },
                'model_provider': 'openai',
                'model_name': 'Qwen/Qwen3-8B',
                'system_fingerprint': '',
                'id': '019b5ffef00eb16d9d733d114d85542e',
                'finish_reason': 'stop',
                'logprobs': None
            },
            name='supervisor',
            id='lc_run--019b5ffe-ef95-7e43-b16a-aedefcc150e4-0',
            usage_metadata={
                'input_tokens': 557,
                'output_tokens': 94,
                'total_tokens': 651,
                'input_token_details': {},
                'output_token_details': {'reasoning': 0}
            }
        )
    ]
}

 """

# %% the result of the 1st trial
# FAANG公司（Facebook、Amazon、Apple、Netflix、Alphabet）的员工总数根据最近的公开数据和财报，大概如下：

# 1. **Meta（原Facebook）**：约78,450名员工（截至2025年Q3末）。
# 2. **Amazon（亚马逊）**：约1,556,000名员工（基于2025年《财富》世界500强数据，包含全职、兼职以及所有子公司员工）。
# 3. **Apple（苹果）**：约166,000名员工（截至2025财年末，即9月27日）。
# 4. **Netflix（奈飞）**：约12,000名员工（截至2025年，包含核心团队）。
# 5. **Alphabet（谷歌母公司）**：约190,167名员工（截至2025年Q3末，包含所有子公司的员工）。

# 综上，FAANG公司员工总数大约在 **2,399,000人左右**，这个数字可能会随着公司战略调整、业务扩展或人员变动而有所变化。如需更准确的实时数据，建议参考各公司最新的官方报告或新闻公告。


""" 

{
    'messages': [
        HumanMessage(
            content='现在FAANG公司有多少员工?',
            additional_kwargs={},
            response_metadata={},
            id='2db7d0b4-ed4d-4bed-ab14-386b49abe3f8'
        ),
        AIMessage(
            content='',
            additional_kwargs={'refusal': None},
            response_metadata={
                'token_usage': {
                    'completion_tokens': 19,
                    'prompt_tokens': 204,
                    'total_tokens': 223,
                    'completion_tokens_details': {
                        'accepted_prediction_tokens': None,
                        'audio_tokens': None,
                        'reasoning_tokens': 0,
                        'rejected_prediction_tokens': None
                    },
                    'prompt_tokens_details': None
                },
                'model_provider': 'openai',
                'model_name': 'Qwen/Qwen3-8B',
                'system_fingerprint': '',
                'id': '019b5ff86c43fabbaee279852e5c50a9',
                'finish_reason': 'tool_calls',
                'logprobs': None
            },
            name='supervisor',
            id='lc_run--019b5ff8-6b21-7ee1-8f21-d82acfe3f7ff-0',
            tool_calls=[
                {
                    'name': 'transfer_to_research_expert',
                    'args': {},
                    'id': '019b5ff8701795b6b450476625a8a757',
                    'type': 'tool_call'
                }
            ],
            usage_metadata={
                'input_tokens': 204,
                'output_tokens': 19,
                'total_tokens': 223,
                'input_token_details': {},
                'output_token_details': {'reasoning': 0}
            }
        ),
        ToolMessage(
            content='Successfully transferred to research_expert',
            name='transfer_to_research_expert',
            id='1eb83755-be8c-433e-8e82-39a408a55f49',
            tool_call_id='019b5ff8701795b6b450476625a8a757'
        ),
        AIMessage(
            content='FAANG公司（Facebook、Amazon、Apple、Netflix、Alphabet）的员工总数如下（基于2024年的数据）：\n\n1. **Meta (原Facebook)**：约78,450人（2025年Q3末，含全职员工）。\n2. **Amazon（亚马逊）**：约1,556,000人（2025年《财富》世界500强口径，含全职、兼职及子公司员工）。\n3. **Apple（苹果）**：约166,000人（2025财年末，即9月27日，财报数据）。\n4. **Netflix（奈飞）**：约12,000人（2025年公开披露数据，含核心团队）。\n5. **Alphabet（谷歌母公司）**：约190,167人（2025年Q3末，含全子公司员工）。\n\n以上数据综合了各公司的最新财报和公开披露信息。需要注意的是，这些数字可能会随着公司扩展、裁剪或其他变动而发生变化。',
            additional_kwargs={'refusal': None},
            response_metadata={
                'token_usage': {
                    'completion_tokens': 244,
                    'prompt_tokens': 446,
                    'total_tokens': 690,
                    'completion_tokens_details': {
                        'accepted_prediction_tokens': None,
                        'audio_tokens': None,
                        'reasoning_tokens': 0,
                        'rejected_prediction_tokens': None
                    },
                    'prompt_tokens_details': None
                },
                'model_provider': 'openai',
                'model_name': 'Qwen/Qwen3-8B',
                'system_fingerprint': '',
                'id': '019b5ff874f15d67efb2c8adf50dcdb1',
                'finish_reason': 'stop',
                'logprobs': None
            },
            name='research_expert',
            id='lc_run--019b5ff8-7478-72a0-985f-cfbe6fa156a1-0',
            usage_metadata={
                'input_tokens': 446,
                'output_tokens': 244,
                'total_tokens': 690,
                'input_token_details': {},
                'output_token_details': {'reasoning': 0}
            }
        ),
        AIMessage(
            content='Transferring back to supervisor',
            additional_kwargs={},
            response_metadata={'__is_handoff_back': True},
            name='research_expert',
            id='6e58975b-219c-47ac-a4f9-559a3e99bec7',
            tool_calls=[
                {
                    'name': 'transfer_back_to_supervisor',
                    'args': {},
                    'id': '0bf3080d-c453-42a3-bb81-79238c786f6e',
                    'type': 'tool_call'
                }
            ]
        ),
        ToolMessage(
            content='Successfully transferred back to supervisor',
            name='transfer_back_to_supervisor',
            id='71e29f22-de69-4406-bd64-afbddfc2735d',
            tool_call_id='0bf3080d-c453-42a3-bb81-79238c786f6e'
        ),
        AIMessage(
            content='FAANG公司（Facebook、Amazon、Apple、Netflix、Alphabet）的员工总数根据最近的公开数据和财报，大概如下：\n\n1. **Meta（原Facebook）**：约78,450名员工（截至2025年Q3末）。\n2. **Amazon（亚马逊）**：约1,556,000名员工（基于2025年《财富》世界500强数据，包含全职、兼职以及所有子公司员工）。\n3. **Apple（苹果）**：约166,000名员工（截至2025财年末，即9月27日）。\n4. **Netflix（奈飞）**：约12,000名员工（截至2025年，包含核心团队）。\n5. **Alphabet（谷歌母公司）**：约190,167名员工（截至2025年Q3末，包含所有子公司的员工）。\n\n综上，FAANG公司员工总数大约在 **2,399,000人左右**，这个数字可能会随着公司战略调整、业务扩展或人员变动而有所变化。如需更准确的实时数据，建议参考各公司最新的官方报告或新闻公告。',
            additional_kwargs={'refusal': None},
            response_metadata={
                'token_usage': {
                    'completion_tokens': 276,
                    'prompt_tokens': 536,
                    'total_tokens': 812,
                    'completion_tokens_details': {
                        'accepted_prediction_tokens': None,
                        'audio_tokens': None,
                        'reasoning_tokens': 0,
                        'rejected_prediction_tokens': None
                    },
                    'prompt_tokens_details': None
                },
                'model_provider': 'openai',
                'model_name': 'Qwen/Qwen3-8B',
                'system_fingerprint': '',
                'id': '019b5ff89a9f07751a1aeb373e736c9c',
                'finish_reason': 'stop',
                'logprobs': None
            },
            name='supervisor',
            id='lc_run--019b5ff8-9957-7980-ac64-c4d033b68767-0',
            usage_metadata={
                'input_tokens': 536,
                'output_tokens': 276,
                'total_tokens': 812,
                'input_token_details': {},
                'output_token_details': {'reasoning': 0}
            }
        )
    ]
}

 """

# %% 7-12 具有”研究团队“主管智能体和”写作团队“主管智能体的分层系统

from langgraph_supervisor import create_supervisor
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent

llm = ChatOpenAI(model="Qwen/Qwen3-8B")

# the following codes is about `writing team`


def write_export(topic: str) -> str:
    """撰写关于给定主题的报告"""
    return f"写关于{topic}的报告：（报告的详细内容）"


def publish_export(report: str) -> str:
    """发布报告"""
    return f"报告已发布：{report}"


writer = create_agent(
    name="writer", model=llm, tools=[write_export], system_prompt="你是一个写作作家。"
)

publisher = create_agent(
    name="publisher",
    model=llm,
    tools=[publish_export],
    system_prompt="你是一个出版社。",
)


writing_team_supervisor = create_supervisor([writer, publisher], model=llm)
writing_team = writing_team_supervisor.compile(name="writing_team")


# the following codes is about `research team` supervisor
def add(one: float, two: float) -> float:
    """一个加法工具"""
    return one + two


def multiply(number: float, number2: float) -> float:
    """一个乘法工具"""
    return number * number2


math_expert = create_agent(
    model=llm,
    tools=[add, multiply],
    name="math_expert",
    system_prompt="你是一个数学专家，始终使用一个工具",
)


def web_search(query: str) -> str:
    """在网络上搜索信息"""
    return (
        "2025年FAANG的员工数量如下---：\n"
        "Meta(原Facebook)，78,450 人，2025 年 Q3 末（财报数据，含全职）\n"
        "Amazon（亚马逊）	1,556,000 人	2025 年《财富》世界 500 强口径（含全职 / 兼职 / 子公司）\n"
        "Apple（苹果）	166,000 人	2025 财年末（9 月 27 日，财报数据）\n"
        "Netflix（奈飞）	约 12,000 人	2025 年公开披露（行业统计口径，含核心团队）\n"
        "Alphabet（谷歌母公司）	190,167 人	2025 年 Q3 末（财报数据，含全子公司）"
    )


research_expert = create_agent(
    name="research_expert",
    model=llm,
    tools=[web_search],
    system_prompt="你是一个研究专家，可以使用网络搜索工具。但不需要做数学计算。",
)

research_team_supervisor = create_supervisor(
    [math_expert, research_expert],
    model=llm,
    prompt="你正在管理一个研究团队，该团队由数学专家和研究专家组成。研究专家可以使用网络搜索工具进行查询。",
)

research_team = research_team_supervisor.compile(name="research_team")

# combine `research_team` and `writing_team`
top_level_supervisor_agent = create_supervisor(
    [writing_team, research_team],
    model=llm,
    prompt="你是一个顶层主管，管理研究团队和写作团队。",
)
top_level_supervisor = top_level_supervisor_agent.compile(name="top_level_supervisor")

# %% the result of 1st trial
messages = [("user", "2025年,FAANG公司的人数分别是多少，总的员工人数是多少？")]
response = top_level_supervisor.invoke({"messages": messages})
print(response["messages"][-1].content)
""" 

2025年，FAANG公司的总员工人数约为 **1,998,067人**。以下是各公司的员工人数：

- **Meta（原Facebook）**：约 78,450 人  
- **Amazon（亚马逊）**：约 1,556,000 人  
- **Apple（苹果）**：约 166,000 人  
- **Netflix（奈飞）**：约 12,000 人  
- **Alphabet（谷歌母公司）**：约 190,167 人  

如需进一步分析或数据支持，请随时告知！
 """

# %% the 2nd result
""" 

2025年FAANG公司（Facebook、Apple、Amazon、Netflix、Google）的具体员工人数没有官方公开的精确数据，但我们可以基于2024年的信息进行估算：

- **Facebook（Meta）**：约 **98,000至102,000人**
- **Apple**：约 **195,000至205,000人**
- **Amazon**：约 **1,700,000至1,800,000人**
- **Netflix**：约 **9,000至11,000人**
- **Google（Alphabet）**：约 **125,000至135,000人**

### 总的员工人数估算（2025年）：
假设各公司人数基本稳定，总人数可能在 **2,227,000至2,342,000人之间**。

这些数据是基于近年来的趋势进行的合理推测，实际数字可能会因为以下因素而有所不同：

1. **招聘和裁员**：公司可能会根据业务发展和市场状况调整招聘计划。
2. **合并与分拆**：部分公司（如Meta和Facebook）可能经历更进一步的重组或业务调整。
3. **全球扩张或收缩**：公司可能会在某些地区增加或减少办公地点，影响总人数。
4. **员工流动**：包括内部调动、离职或入职等因素。

如需最新、最准确的数字，建议参考各公司最新发布的财报或官方公告。是否需要我帮助查找这些官方数据？
 """

# %%
messages = [("user", "写一篇关于入职的报告，大约800字")]
response = top_level_supervisor.invoke({"messages": messages})
print(response["messages"][-1].content)

# the 1st test result
""" 

**入职报告**

尊敬的领导：

您好！

我怀着无比激动和期待的心情写下这份入职报告，正式成为公司的一员，开启职业生涯的新篇章。通过这段时间的深入了解和适应，我对公司的发展前景、企业文化以及岗位职责有了更加全面的认识，也对即将开展的工作充满信心。

首先，我衷心感谢公司为我提供了这样一个宝贵的发展平台。通过面试和入职培训，我深刻感受到公司对人才的重视和对员工成长的关注。公司强调“以人为本、追求卓越”的核心理念，注重创新、合作与持续学习，这与我自身的职业价值观高度契合。我非常荣幸能够加入这样一个充满活力和潜力的组织。

在入职过程中，我有幸接触到公司各个部门的同事，并参与了初步的团队协作活动。大家热情友好、专业敬业，这让我迅速融入了团队氛围。同时，公司也为我们提供了系统的培训课程，帮助我们了解公司业务流程、行业背景以及岗位的具体要求，为今后的工作打下坚实的基础。

作为市场部的一员，我主要负责品牌推广与市场分析相关工作。虽然这是我首次接触这一领域，但我在前期的学习中已经掌握了基础的市场研究方法和品牌传播策略。未来，我将不断学习和提升自己的专业能力，积极配合团队完成各项任务，努力为公司创造价值。

我深知，入职不仅是一次职业转型，更是一份沉甸甸的责任。我将严格遵守公司的各项规章制度，保持高度的敬业精神和责任心，以积极的态度面对工作中的挑战，争取在最短的时间内胜任岗位要求，为团队贡献自己的力量。

最后，我希望在未来的工作中，能够与公司共同成长，不断突破自我，实现个人价值与公司发展的双赢。我相信，在这里，我不仅能够收获宝贵的工作经验，还能结识志同道合的同事，共同书写属于我们的精彩篇章。

此致  
敬礼！

**报告人：XXX**  
**日期：2023年X月X日**
 """

# %% the 2nd result
""" 

以下是关于入职的报告，约800字：

---

**入职报告**

尊敬的领导：

您好！

我谨以此报告向您汇报我近期的入职情况和初步感受。作为一名新入职的员工，我深感荣幸能够加入贵公司这个充满活力与机遇的大家庭。入职以来，我经历了从准备到正式加入的几个阶段，现将具体情况总结如下：

首先，在接到录用通知后，我立即着手准备所需材料，包括身份证、学历证明、健康检查报告等，确保所有手续能够按时完成。在公司安排的入职培训中，我深入了解了公司的企业文化、组织架构、各项规章制度以及岗位职责等，这为我后续的工作奠定了坚实的基础。

其次，我逐渐适应了新的工作环境。虽然最初对公司的运作流程和团队协作方式感到有些陌生，但在同事们的热情帮助下，我迅速融入了团队。大家耐心地解答我提出的各种问题，分享他们的工作经验，让我在短时间内对岗位有了更清晰的认识。我还参加了几次部门会议，了解了团队的工作目标和任务分配，这让我更加明确了自身的职责。

再次，在工作中，我感受到了公司对员工的重视与培养。公司不仅提供了良好的办公环境和完善的福利制度，还设置了系统的培训计划，帮助我们不断提升专业技能。此外，领导层对新员工的关注也让我倍感温暖，他们经常与我们交流，了解我们的需求和想法，这让我对公司的未来充满信心。

在工作中，我还意识到沟通和协作的重要性。作为一个团队的一员，我需要与不同部门的同事保持密切的沟通，确保信息的准确传递和任务的有效执行。通过与同事们的合作，我不仅提高了工作效率，也增强了团队意识。

最后，我对未来的工作充满期待和动力。我希望能够在未来的工作中不断提升自己，为公司的发展贡献更多力量。我也相信，在公司的培养和支持下，我能够更好地适应岗位要求，实现个人价值与公司目标的双赢。

总之，入职以来的经历让我受益匪浅，我对公司充满了感激之情。我会继续努力，不断提升自己，为公司的发展做出更大的贡献。

此致  
敬礼！

[您的姓名]  
[日期]  

---

如果您有任何具体需求或需要进一步修改的内容，请随时告知。
 """
# %%
messages = [
    (
        "user",
        (
            "写一篇想念兄弟的信件，在监狱里面，我们的关系很好，经常在一起抽烟畅聊未来的事业。"
            "他还在监狱中，大概5月份出狱，他姓罗，年纪比我小。他最牵挂的是他的小儿子（4岁），"
            "至今还未见到一面。还有就是他母亲的病.现在已经控制住了,字数在1000字左右。"
        ),
    )
]
response = top_level_supervisor.invoke({"messages": messages})
print(response["messages"][-1].content)
