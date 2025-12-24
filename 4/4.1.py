# %%
from typing import TypedDict
from langgraph.graph import StateGraph, START


class MyState(TypedDict):  # type: ignore
    topic: str
    joke: str


def refine_topic(state: MyState):  # type: ignore
    return {"topic": state["topic"] + " and cats"}


def generate_a_joke(state: MyState):  # type: ignore
    return {"joke": f"This is a joke about {state['topic']}"}


graph = StateGraph(MyState)
graph.add_node(refine_topic)
graph.add_node(generate_a_joke)
graph.add_edge(START, "refine_topic")
graph.add_edge("refine_topic", "generate_a_joke")

agent = graph.compile()

# %%
for chunk in agent.stream({"topic": "ice cream"}, stream_mode="values"):  # type: ignore
    print(chunk)

# {'topic': 'ice cream'}
# {'topic': 'ice cream and cats'}
# {'topic': 'ice cream and cats', 'joke': 'This is a joke about ice cream and cats'}


# %% 4-3 stream_mode=updates 更新流
for chunk in agent.stream({"topic": "ice cream"}, stream_mode="updates"):  # type: ignore
    print(chunk)

# {'refine_topic': {'topic': 'ice cream and cats'}}
# {'generate_a_joke': {'joke': 'This is a joke about ice cream and cats'}}

# %% 4-4 使用StreamWriter
from langgraph.types import StreamWriter  # noqa: E402
from typing import TypedDict  # noqa: E402
from langgraph.graph import StateGraph, START  # noqa: E402


class MyState(TypedDict):  # type: ignore
    topic: str
    joke: str


def refine_topic(state: MyState):  # type: ignore
    return {"topic": state["topic"] + " and cats"}


def generate_a_joke(state: MyState, writer: StreamWriter):  # type: ignore
    writer({"custom_key": "Writing custom data while generating a joke"})
    return {"joke": f"This is a joke about {state['topic']}"}


graph = StateGraph(MyState)
graph.add_node(refine_topic)
graph.add_node(generate_a_joke)
graph.add_edge(START, "refine_topic")
graph.add_edge("refine_topic", "generate_a_joke")

agent = graph.compile()

for chunk in agent.stream({"topic": "ice cream"}, stream_mode="custom"):  # type: ignore
    print(chunk)

# {'custom_key': 'Writing custom data while generating a joke'}


# %% 4-6 使用stream_mode='messages'

from langchain_openai import ChatOpenAI  # noqa: E402


class MyState(TypedDict):  # type: ignore
    topic: str
    joke: str


llm = ChatOpenAI(model="Qwen/Qwen2.5-7B-Instruct")


def generate_a_joke(state: MyState):  # type: ignore
    response = llm.invoke(
        [{"role": "user", "content": f"generate a joke about {state['topic']}"}]
    )
    return {"joke": response}


graph = StateGraph(MyState)
graph.add_node(refine_topic)
graph.add_node(generate_a_joke)
graph.add_edge(START, "refine_topic")
graph.add_edge("refine_topic", "generate_a_joke")

agent = graph.compile()


for chunk, metadata in agent.stream({"topic": "ice cream"}, stream_mode="messages"):  # type: ignore
    if chunk.content:  # type: ignore
        print(chunk.content, end="|", flush=True)  # type: ignore

# Why| did| the| cat| sit| on| the| ice| cream| cone|?

# |Because| she| wanted| to| see| if| it| would| pur|r|-f|ect|!|

# %%

from langchain_openai import ChatOpenAI  # noqa: E402
from langgraph.types import StreamWriter  # noqa: E402
from typing import TypedDict  # noqa: E402
from langgraph.graph import StateGraph, START, END  # noqa: E402


class MyState(TypedDict):  # type: ignore
    topic: str
    joke: str


llm = ChatOpenAI(model="Qwen/Qwen2.5-7B-Instruct")


def generate_a_joke(state: MyState):  # type: ignore
    response = llm.invoke(
        [{"role": "user", "content": f"今天江西抚州的{state['topic']}"}]
    )
    return {"joke": response}


graph = StateGraph(MyState)
graph.add_node(generate_a_joke)
graph.add_edge(START, "generate_a_joke")
graph.add_edge("generate_a_joke", END)

agent = graph.compile()


for idx, (chunk, metadata) in enumerate(
    agent.stream({"topic": "天气"}, stream_mode="messages")  # type: ignore
):
    print(idx, metadata)
    if chunk.content:  # type: ignore
        print(chunk.content)  # type: ignore

# 每次输出的idx的值都不一样，有60+，最高的也有140+。
# 0 {'langgraph_step': 1, 'langgraph_node': 'generate_a_joke', 'langgraph_triggers': ('branch:to:generate_a_joke',), 'langgraph_path': ('__pregel_pull', 'generate_a_joke'), 'langgraph_checkpoint_ns': 'generate_a_joke:5bd10d6b-e72c-d811-6b1f-e1baf600e1a5', 'checkpoint_ns': 'generate_a_joke:5bd10d6b-e72c-d811-6b1f-e1baf600e1a5', 'ls_provider': 'openai', 'ls_model_name': 'Qwen/Qwen2.5-7B-Instruct', 'ls_model_type': 'chat', 'ls_temperature': None}
# 1 {'langgraph_step': 1, 'langgraph_node': 'generate_a_joke', 'langgraph_triggers': ('branch:to:generate_a_joke',), 'langgraph_path': ('__pregel_pull', 'generate_a_joke'), 'langgraph_checkpoint_ns': 'generate_a_joke:5bd10d6b-e72c-d811-6b1f-e1baf600e1a5', 'checkpoint_ns': 'generate_a_joke:5bd10d6b-e72c-d811-6b1f-e1baf600e1a5', 'ls_provider': 'openai', 'ls_model_name': 'Qwen/Qwen2.5-7B-Instruct', 'ls_model_type': 'chat', 'ls_temperature': None}
# 要
# 2 {'langgraph_step': 1, 'langgraph_node': 'generate_a_joke', 'langgraph_triggers': ('branch:to:generate_a_joke',), 'langgraph_path': ('__pregel_pull', 'generate_a_joke'), 'langgraph_checkpoint_ns': 'generate_a_joke:5bd10d6b-e72c-d811-6b1f-e1baf600e1a5', 'checkpoint_ns': 'generate_a_joke:5bd10d6b-e72c-d811-6b1f-e1baf600e1a5', 'ls_provider': 'openai', 'ls_model_name': 'Qwen/Qwen2.5-7B-Instruct', 'ls_model_type': 'chat', 'ls_temperature': None}
# 获取
# 3 {'langgraph_step': 1, 'langgraph_node': 'generate_a_joke', 'langgraph_triggers': ('branch:to:generate_a_joke',), 'langgraph_path': ('__pregel_pull', 'generate_a_joke'), 'langgraph_checkpoint_ns': 'generate_a_joke:5bd10d6b-e72c-d811-6b1f-e1baf600e1a5', 'checkpoint_ns': 'generate_a_joke:5bd10d6b-e72c-d811-6b1f-e1baf600e1a5', 'ls_provider': 'openai', 'ls_model_name': 'Qwen/Qwen2.5-7B-Instruct', 'ls_model_type': 'chat', 'ls_temperature': None}
# 今天
# 4 {'langgraph_step': 1, 'langgraph_node': 'generate_a_joke', 'langgraph_triggers': ('branch:to:generate_a_joke',), 'langgraph_path': ('__pregel_pull', 'generate_a_joke'), 'langgraph_checkpoint_ns': 'generate_a_joke:5bd10d6b-e72c-d811-6b1f-e1baf600e1a5', 'checkpoint_ns': 'generate_a_joke:5bd10d6b-e72c-d811-6b1f-e1baf600e1a5', 'ls_provider': 'openai', 'ls_model_name': 'Qwen/Qwen2.5-7B-Instruct', 'ls_model_type': 'chat', 'ls_temperature': None}
# 江西
# 5 {'langgraph_step': 1, 'langgraph_node': 'generate_a_joke', 'langgraph_triggers': ('branch:to:generate_a_joke',), 'langgraph_path': ('__pregel_pull', 'generate_a_joke'), 'langgraph_checkpoint_ns': 'generate_a_joke:5bd10d6b-e72c-d811-6b1f-e1baf600e1a5', 'checkpoint_ns': 'generate_a_joke:5bd10d6b-e72c-d811-6b1f-e1baf600e1a5', 'ls_provider': 'openai', 'ls_model_name': 'Qwen/Qwen2.5-7B-Instruct', 'ls_model_type': 'chat', 'ls_temperature': None}
# 抚
# 6 {'langgraph_step': 1, 'langgraph_node': 'generate_a_joke', 'langgraph_triggers': ('branch:to:generate_a_joke',), 'langgraph_path': ('__pregel_pull', 'generate_a_joke'), 'langgraph_checkpoint_ns': 'generate_a_joke:5bd10d6b-e72c-d811-6b1f-e1baf600e1a5', 'checkpoint_ns': 'generate_a_joke:5bd10d6b-e72c-d811-6b1f-e1baf600e1a5', 'ls_provider': 'openai', 'ls_model_name': 'Qwen/Qwen2.5-7B-Instruct', 'ls_model_type': 'chat', 'ls_temperature': None}
# 州
# 7 {'langgraph_step': 1, 'langgraph_node': 'generate_a_joke', 'langgraph_triggers': ('branch:to:generate_a_joke',), 'langgraph_path': ('__pregel_pull', 'generate_a_joke'), 'langgraph_checkpoint_ns': 'generate_a_joke:5bd10d6b-e72c-d811-6b1f-e1baf600e1a5', 'checkpoint_ns': 'generate_a_joke:5bd10d6b-e72c-d811-6b1f-e1baf600e1a5', 'ls_provider': 'openai', 'ls_model_name': 'Qwen/Qwen2.5-7B-Instruct', 'ls_model_type': 'chat', 'ls_temperature': None}
# 的
# 8 {'langgraph_step': 1, 'langgraph_node': 'generate_a_joke', 'langgraph_triggers': ('branch:to:generate_a_joke',), 'langgraph_path': ('__pregel_pull', 'generate_a_joke'), 'langgraph_checkpoint_ns': 'generate_a_joke:5bd10d6b-e72c-d811-6b1f-e1baf600e1a5', 'checkpoint_ns': 'generate_a_joke:5bd10d6b-e72c-d811-6b1f-e1baf600e1a5', 'ls_provider': 'openai', 'ls_model_name': 'Qwen/Qwen2.5-7B-Instruct', 'ls_model_type': 'chat', 'ls_temperature': None}
# 天气
# 9 {'langgraph_step': 1, 'langgraph_node': 'generate_a_joke', 'langgraph_triggers': ('branch:to:generate_a_joke',), 'langgraph_path': ('__pregel_pull', 'generate_a_joke'), 'langgraph_checkpoint_ns': 'generate_a_joke:5bd10d6b-e72c-d811-6b1f-e1baf600e1a5', 'checkpoint_ns': 'generate_a_joke:5bd10d6b-e72c-d811-6b1f-e1baf600e1a5', 'ls_provider': 'openai', 'ls_model_name': 'Qwen/Qwen2.5-7B-Instruct', 'ls_model_type': 'chat', 'ls_temperature': None}
# 信息
# 10 {'langgraph_step': 1, 'langgraph_node': 'generate_a_joke', 'langgraph_triggers': ('branch:to:generate_a_joke',), 'langgraph_path': ('__pregel_pull', 'generate_a_joke'), 'langgraph_checkpoint_ns': 'generate_a_joke:5bd10d6b-e72c-d811-6b1f-e1baf600e1a5', 'checkpoint_ns': 'generate_a_joke:5bd10d6b-e72c-d811-6b1f-e1baf600e1a5', 'ls_provider': 'openai', 'ls_model_name': 'Qwen/Qwen2.5-7B-Instruct', 'ls_model_type': 'chat', 'ls_temperature': None}
# ，
# 11 {'langgraph_step': 1, 'langgraph_node': 'generate_a_joke', 'langgraph_triggers': ('branch:to:generate_a_joke',), 'langgraph_path': ('__pregel_pull', 'generate_a_joke'), 'langgraph_checkpoint_ns': 'generate_a_joke:5bd10d6b-e72c-d811-6b1f-e1baf600e1a5', 'checkpoint_ns': 'generate_a_joke:5bd10d6b-e72c-d811-6b1f-e1baf600e1a5', 'ls_provider': 'openai', 'ls_model_name': 'Qwen/Qwen2.5-7B-Instruct', 'ls_model_type': 'chat', 'ls_temperature': None}
# 我
# 12 {'langgraph_step': 1, 'langgraph_node': 'generate_a_joke', 'langgraph_triggers': ('branch:to:generate_a_joke',), 'langgraph_path': ('__pregel_pull', 'generate_a_joke'), 'langgraph_checkpoint_ns': 'generate_a_joke:5bd10d6b-e72c-d811-6b1f-e1baf600e1a5', 'checkpoint_ns': 'generate_a_joke:5bd10d6b-e72c-d811-6b1f-e1baf600e1a5', 'ls_provider': 'openai', 'ls_model_name': 'Qwen/Qwen2.5-7B-Instruct', 'ls_model_type': 'chat', 'ls_temperature': None}
# 需要
# 13 {'langgraph_step': 1, 'langgraph_node': 'generate_a_joke', 'langgraph_triggers': ('branch:to:generate_a_joke',), 'langgraph_path': ('__pregel_pull', 'generate_a_joke'), 'langgraph_checkpoint_ns': 'generate_a_joke:5bd10d6b-e72c-d811-6b1f-e1baf600e1a5', 'checkpoint_ns': 'generate_a_joke:5bd10d6b-e72c-d811-6b1f-e1baf600e1a5', 'ls_provider': 'openai', 'ls_model_name': 'Qwen/Qwen2.5-7B-Instruct', 'ls_model_type': 'chat', 'ls_temperature': None}
# 访问
# 14 {'langgraph_step': 1, 'langgraph_node': 'generate_a_joke', 'langgraph_triggers': ('branch:to:generate_a_joke',), 'langgraph_path': ('__pregel_pull', 'generate_a_joke'), 'langgraph_checkpoint_ns': 'generate_a_joke:5bd10d6b-e72c-d811-6b1f-e1baf600e1a5', 'checkpoint_ns': 'generate_a_joke:5bd10d6b-e72c-d811-6b1f-e1baf600e1a5', 'ls_provider': 'openai', 'ls_model_name': 'Qwen/Qwen2.5-7B-Instruct', 'ls_model_type': 'chat', 'ls_temperature': None}
# 最新的
# 15 {'langgraph_step': 1, 'langgraph_node': 'generate_a_joke', 'langgraph_triggers': ('branch:to:generate_a_joke',), 'langgraph_path': ('__pregel_pull', 'generate_a_joke'), 'langgraph_checkpoint_ns': 'generate_a_joke:5bd10d6b-e72c-d811-6b1f-e1baf600e1a5', 'checkpoint_ns': 'generate_a_joke:5bd10d6b-e72c-d811-6b1f-e1baf600e1a5', 'ls_provider': 'openai', 'ls_model_name': 'Qwen/Qwen2.5-7B-Instruct', 'ls_model_type': 'chat', 'ls_temperature': None}
# 气象
# 16 {'langgraph_step': 1, 'langgraph_node': 'generate_a_joke', 'langgraph_triggers': ('branch:to:generate_a_joke',), 'langgraph_path': ('__pregel_pull', 'generate_a_joke'), 'langgraph_checkpoint_ns': 'generate_a_joke:5bd10d6b-e72c-d811-6b1f-e1baf600e1a5', 'checkpoint_ns': 'generate_a_joke:5bd10d6b-e72c-d811-6b1f-e1baf600e1a5', 'ls_provider': 'openai', 'ls_model_name': 'Qwen/Qwen2.5-7B-Instruct', 'ls_model_type': 'chat', 'ls_temperature': None}
# 数据
# 17 {'langgraph_step': 1, 'langgraph_node': 'generate_a_joke', 'langgraph_triggers': ('branch:to:generate_a_joke',), 'langgraph_path': ('__pregel_pull', 'generate_a_joke'), 'langgraph_checkpoint_ns': 'generate_a_joke:5bd10d6b-e72c-d811-6b1f-e1baf600e1a5', 'checkpoint_ns': 'generate_a_joke:5bd10d6b-e72c-d811-6b1f-e1baf600e1a5', 'ls_provider': 'openai', 'ls_model_name': 'Qwen/Qwen2.5-7B-Instruct', 'ls_model_type': 'chat', 'ls_temperature': None}
# 。
# 18 {'langgraph_step': 1, 'langgraph_node': 'generate_a_joke', 'langgraph_triggers': ('branch:to:generate_a_joke',), 'langgraph_path': ('__pregel_pull', 'generate_a_joke'), 'langgraph_checkpoint_ns': 'generate_a_joke:5bd10d6b-e72c-d811-6b1f-e1baf600e1a5', 'checkpoint_ns': 'generate_a_joke:5bd10d6b-e72c-d811-6b1f-e1baf600e1a5', 'ls_provider': 'openai', 'ls_model_name': 'Qwen/Qwen2.5-7B-Instruct', 'ls_model_type': 'chat', 'ls_temperature': None}
# 由于
# 19 {'langgraph_step': 1, 'langgraph_node': 'generate_a_joke', 'langgraph_triggers': ('branch:to:generate_a_joke',), 'langgraph_path': ('__pregel_pull', 'generate_a_joke'), 'langgraph_checkpoint_ns': 'generate_a_joke:5bd10d6b-e72c-d811-6b1f-e1baf600e1a5', 'checkpoint_ns': 'generate_a_joke:5bd10d6b-e72c-d811-6b1f-e1baf600e1a5', 'ls_provider': 'openai', 'ls_model_name': 'Qwen/Qwen2.5-7B-Instruct', 'ls_model_type': 'chat', 'ls_temperature': None}
# 我
# 20 {'langgraph_step': 1, 'langgraph_node': 'generate_a_joke', 'langgraph_triggers': ('branch:to:generate_a_joke',), 'langgraph_path': ('__pregel_pull', 'generate_a_joke'), 'langgraph_checkpoint_ns': 'generate_a_joke:5bd10d6b-e72c-d811-6b1f-e1baf600e1a5', 'checkpoint_ns': 'generate_a_joke:5bd10d6b-e72c-d811-6b1f-e1baf600e1a5', 'ls_provider': 'openai', 'ls_model_name': 'Qwen/Qwen2.5-7B-Instruct', 'ls_model_type': 'chat', 'ls_temperature': None}
# 无法
# 21 {'langgraph_step': 1, 'langgraph_node': 'generate_a_joke', 'langgraph_triggers': ('branch:to:generate_a_joke',), 'langgraph_path': ('__pregel_pull', 'generate_a_joke'), 'langgraph_checkpoint_ns': 'generate_a_joke:5bd10d6b-e72c-d811-6b1f-e1baf600e1a5', 'checkpoint_ns': 'generate_a_joke:5bd10d6b-e72c-d811-6b1f-e1baf600e1a5', 'ls_provider': 'openai', 'ls_model_name': 'Qwen/Qwen2.5-7B-Instruct', 'ls_model_type': 'chat', 'ls_temperature': None}
# 实时
# 22 {'langgraph_step': 1, 'langgraph_node': 'generate_a_joke', 'langgraph_triggers': ('branch:to:generate_a_joke',), 'langgraph_path': ('__pregel_pull', 'generate_a_joke'), 'langgraph_checkpoint_ns': 'generate_a_joke:5bd10d6b-e72c-d811-6b1f-e1baf600e1a5', 'checkpoint_ns': 'generate_a_joke:5bd10d6b-e72c-d811-6b1f-e1baf600e1a5', 'ls_provider': 'openai', 'ls_model_name': 'Qwen/Qwen2.5-7B-Instruct', 'ls_model_type': 'chat', 'ls_temperature': None}
# 联网
# 23 {'langgraph_step': 1, 'langgraph_node': 'generate_a_joke', 'langgraph_triggers': ('branch:to:generate_a_joke',), 'langgraph_path': ('__pregel_pull', 'generate_a_joke'), 'langgraph_checkpoint_ns': 'generate_a_joke:5bd10d6b-e72c-d811-6b1f-e1baf600e1a5', 'checkpoint_ns': 'generate_a_joke:5bd10d6b-e72c-d811-6b1f-e1baf600e1a5', 'ls_provider': 'openai', 'ls_model_name': 'Qwen/Qwen2.5-7B-Instruct', 'ls_model_type': 'chat', 'ls_temperature': None}
# 查询
# 24 {'langgraph_step': 1, 'langgraph_node': 'generate_a_joke', 'langgraph_triggers': ('branch:to:generate_a_joke',), 'langgraph_path': ('__pregel_pull', 'generate_a_joke'), 'langgraph_checkpoint_ns': 'generate_a_joke:5bd10d6b-e72c-d811-6b1f-e1baf600e1a5', 'checkpoint_ns': 'generate_a_joke:5bd10d6b-e72c-d811-6b1f-e1baf600e1a5', 'ls_provider': 'openai', 'ls_model_name': 'Qwen/Qwen2.5-7B-Instruct', 'ls_model_type': 'chat', 'ls_temperature': None}
# ，
# 25 {'langgraph_step': 1, 'langgraph_node': 'generate_a_joke', 'langgraph_triggers': ('branch:to:generate_a_joke',), 'langgraph_path': ('__pregel_pull', 'generate_a_joke'), 'langgraph_checkpoint_ns': 'generate_a_joke:5bd10d6b-e72c-d811-6b1f-e1baf600e1a5', 'checkpoint_ns': 'generate_a_joke:5bd10d6b-e72c-d811-6b1f-e1baf600e1a5', 'ls_provider': 'openai', 'ls_model_name': 'Qwen/Qwen2.5-7B-Instruct', 'ls_model_type': 'chat', 'ls_temperature': None}
# 您可以
# 26 {'langgraph_step': 1, 'langgraph_node': 'generate_a_joke', 'langgraph_triggers': ('branch:to:generate_a_joke',), 'langgraph_path': ('__pregel_pull', 'generate_a_joke'), 'langgraph_checkpoint_ns': 'generate_a_joke:5bd10d6b-e72c-d811-6b1f-e1baf600e1a5', 'checkpoint_ns': 'generate_a_joke:5bd10d6b-e72c-d811-6b1f-e1baf600e1a5', 'ls_provider': 'openai', 'ls_model_name': 'Qwen/Qwen2.5-7B-Instruct', 'ls_model_type': 'chat', 'ls_temperature': None}
# 查看
# 27 {'langgraph_step': 1, 'langgraph_node': 'generate_a_joke', 'langgraph_triggers': ('branch:to:generate_a_joke',), 'langgraph_path': ('__pregel_pull', 'generate_a_joke'), 'langgraph_checkpoint_ns': 'generate_a_joke:5bd10d6b-e72c-d811-6b1f-e1baf600e1a5', 'checkpoint_ns': 'generate_a_joke:5bd10d6b-e72c-d811-6b1f-e1baf600e1a5', 'ls_provider': 'openai', 'ls_model_name': 'Qwen/Qwen2.5-7B-Instruct', 'ls_model_type': 'chat', 'ls_temperature': None}
# 当地的
# 28 {'langgraph_step': 1, 'langgraph_node': 'generate_a_joke', 'langgraph_triggers': ('branch:to:generate_a_joke',), 'langgraph_path': ('__pregel_pull', 'generate_a_joke'), 'langgraph_checkpoint_ns': 'generate_a_joke:5bd10d6b-e72c-d811-6b1f-e1baf600e1a5', 'checkpoint_ns': 'generate_a_joke:5bd10d6b-e72c-d811-6b1f-e1baf600e1a5', 'ls_provider': 'openai', 'ls_model_name': 'Qwen/Qwen2.5-7B-Instruct', 'ls_model_type': 'chat', 'ls_temperature': None}
# 气象
# 29 {'langgraph_step': 1, 'langgraph_node': 'generate_a_joke', 'langgraph_triggers': ('branch:to:generate_a_joke',), 'langgraph_path': ('__pregel_pull', 'generate_a_joke'), 'langgraph_checkpoint_ns': 'generate_a_joke:5bd10d6b-e72c-d811-6b1f-e1baf600e1a5', 'checkpoint_ns': 'generate_a_joke:5bd10d6b-e72c-d811-6b1f-e1baf600e1a5', 'ls_provider': 'openai', 'ls_model_name': 'Qwen/Qwen2.5-7B-Instruct', 'ls_model_type': 'chat', 'ls_temperature': None}
# 站
# 30 {'langgraph_step': 1, 'langgraph_node': 'generate_a_joke', 'langgraph_triggers': ('branch:to:generate_a_joke',), 'langgraph_path': ('__pregel_pull', 'generate_a_joke'), 'langgraph_checkpoint_ns': 'generate_a_joke:5bd10d6b-e72c-d811-6b1f-e1baf600e1a5', 'checkpoint_ns': 'generate_a_joke:5bd10d6b-e72c-d811-6b1f-e1baf600e1a5', 'ls_provider': 'openai', 'ls_model_name': 'Qwen/Qwen2.5-7B-Instruct', 'ls_model_type': 'chat', 'ls_temperature': None}
# 网站
# 31 {'langgraph_step': 1, 'langgraph_node': 'generate_a_joke', 'langgraph_triggers': ('branch:to:generate_a_joke',), 'langgraph_path': ('__pregel_pull', 'generate_a_joke'), 'langgraph_checkpoint_ns': 'generate_a_joke:5bd10d6b-e72c-d811-6b1f-e1baf600e1a5', 'checkpoint_ns': 'generate_a_joke:5bd10d6b-e72c-d811-6b1f-e1baf600e1a5', 'ls_provider': 'openai', 'ls_model_name': 'Qwen/Qwen2.5-7B-Instruct', 'ls_model_type': 'chat', 'ls_temperature': None}
# 、
# 32 {'langgraph_step': 1, 'langgraph_node': 'generate_a_joke', 'langgraph_triggers': ('branch:to:generate_a_joke',), 'langgraph_path': ('__pregel_pull', 'generate_a_joke'), 'langgraph_checkpoint_ns': 'generate_a_joke:5bd10d6b-e72c-d811-6b1f-e1baf600e1a5', 'checkpoint_ns': 'generate_a_joke:5bd10d6b-e72c-d811-6b1f-e1baf600e1a5', 'ls_provider': 'openai', 'ls_model_name': 'Qwen/Qwen2.5-7B-Instruct', 'ls_model_type': 'chat', 'ls_temperature': None}
# 使用
# 33 {'langgraph_step': 1, 'langgraph_node': 'generate_a_joke', 'langgraph_triggers': ('branch:to:generate_a_joke',), 'langgraph_path': ('__pregel_pull', 'generate_a_joke'), 'langgraph_checkpoint_ns': 'generate_a_joke:5bd10d6b-e72c-d811-6b1f-e1baf600e1a5', 'checkpoint_ns': 'generate_a_joke:5bd10d6b-e72c-d811-6b1f-e1baf600e1a5', 'ls_provider': 'openai', 'ls_model_name': 'Qwen/Qwen2.5-7B-Instruct', 'ls_model_type': 'chat', 'ls_temperature': None}
# 手机
# 34 {'langgraph_step': 1, 'langgraph_node': 'generate_a_joke', 'langgraph_triggers': ('branch:to:generate_a_joke',), 'langgraph_path': ('__pregel_pull', 'generate_a_joke'), 'langgraph_checkpoint_ns': 'generate_a_joke:5bd10d6b-e72c-d811-6b1f-e1baf600e1a5', 'checkpoint_ns': 'generate_a_joke:5bd10d6b-e72c-d811-6b1f-e1baf600e1a5', 'ls_provider': 'openai', 'ls_model_name': 'Qwen/Qwen2.5-7B-Instruct', 'ls_model_type': 'chat', 'ls_temperature': None}
# 上的
# 35 {'langgraph_step': 1, 'langgraph_node': 'generate_a_joke', 'langgraph_triggers': ('branch:to:generate_a_joke',), 'langgraph_path': ('__pregel_pull', 'generate_a_joke'), 'langgraph_checkpoint_ns': 'generate_a_joke:5bd10d6b-e72c-d811-6b1f-e1baf600e1a5', 'checkpoint_ns': 'generate_a_joke:5bd10d6b-e72c-d811-6b1f-e1baf600e1a5', 'ls_provider': 'openai', 'ls_model_name': 'Qwen/Qwen2.5-7B-Instruct', 'ls_model_type': 'chat', 'ls_temperature': None}
# 天气
# 36 {'langgraph_step': 1, 'langgraph_node': 'generate_a_joke', 'langgraph_triggers': ('branch:to:generate_a_joke',), 'langgraph_path': ('__pregel_pull', 'generate_a_joke'), 'langgraph_checkpoint_ns': 'generate_a_joke:5bd10d6b-e72c-d811-6b1f-e1baf600e1a5', 'checkpoint_ns': 'generate_a_joke:5bd10d6b-e72c-d811-6b1f-e1baf600e1a5', 'ls_provider': 'openai', 'ls_model_name': 'Qwen/Qwen2.5-7B-Instruct', 'ls_model_type': 'chat', 'ls_temperature': None}
# 应用程序
# 37 {'langgraph_step': 1, 'langgraph_node': 'generate_a_joke', 'langgraph_triggers': ('branch:to:generate_a_joke',), 'langgraph_path': ('__pregel_pull', 'generate_a_joke'), 'langgraph_checkpoint_ns': 'generate_a_joke:5bd10d6b-e72c-d811-6b1f-e1baf600e1a5', 'checkpoint_ns': 'generate_a_joke:5bd10d6b-e72c-d811-6b1f-e1baf600e1a5', 'ls_provider': 'openai', 'ls_model_name': 'Qwen/Qwen2.5-7B-Instruct', 'ls_model_type': 'chat', 'ls_temperature': None}
# 或
# 38 {'langgraph_step': 1, 'langgraph_node': 'generate_a_joke', 'langgraph_triggers': ('branch:to:generate_a_joke',), 'langgraph_path': ('__pregel_pull', 'generate_a_joke'), 'langgraph_checkpoint_ns': 'generate_a_joke:5bd10d6b-e72c-d811-6b1f-e1baf600e1a5', 'checkpoint_ns': 'generate_a_joke:5bd10d6b-e72c-d811-6b1f-e1baf600e1a5', 'ls_provider': 'openai', 'ls_model_name': 'Qwen/Qwen2.5-7B-Instruct', 'ls_model_type': 'chat', 'ls_temperature': None}
# 访问
# 39 {'langgraph_step': 1, 'langgraph_node': 'generate_a_joke', 'langgraph_triggers': ('branch:to:generate_a_joke',), 'langgraph_path': ('__pregel_pull', 'generate_a_joke'), 'langgraph_checkpoint_ns': 'generate_a_joke:5bd10d6b-e72c-d811-6b1f-e1baf600e1a5', 'checkpoint_ns': 'generate_a_joke:5bd10d6b-e72c-d811-6b1f-e1baf600e1a5', 'ls_provider': 'openai', 'ls_model_name': 'Qwen/Qwen2.5-7B-Instruct', 'ls_model_type': 'chat', 'ls_temperature': None}
# 可靠的
# 40 {'langgraph_step': 1, 'langgraph_node': 'generate_a_joke', 'langgraph_triggers': ('branch:to:generate_a_joke',), 'langgraph_path': ('__pregel_pull', 'generate_a_joke'), 'langgraph_checkpoint_ns': 'generate_a_joke:5bd10d6b-e72c-d811-6b1f-e1baf600e1a5', 'checkpoint_ns': 'generate_a_joke:5bd10d6b-e72c-d811-6b1f-e1baf600e1a5', 'ls_provider': 'openai', 'ls_model_name': 'Qwen/Qwen2.5-7B-Instruct', 'ls_model_type': 'chat', 'ls_temperature': None}
# 气象
# 41 {'langgraph_step': 1, 'langgraph_node': 'generate_a_joke', 'langgraph_triggers': ('branch:to:generate_a_joke',), 'langgraph_path': ('__pregel_pull', 'generate_a_joke'), 'langgraph_checkpoint_ns': 'generate_a_joke:5bd10d6b-e72c-d811-6b1f-e1baf600e1a5', 'checkpoint_ns': 'generate_a_joke:5bd10d6b-e72c-d811-6b1f-e1baf600e1a5', 'ls_provider': 'openai', 'ls_model_name': 'Qwen/Qwen2.5-7B-Instruct', 'ls_model_type': 'chat', 'ls_temperature': None}
# 服务
# 42 {'langgraph_step': 1, 'langgraph_node': 'generate_a_joke', 'langgraph_triggers': ('branch:to:generate_a_joke',), 'langgraph_path': ('__pregel_pull', 'generate_a_joke'), 'langgraph_checkpoint_ns': 'generate_a_joke:5bd10d6b-e72c-d811-6b1f-e1baf600e1a5', 'checkpoint_ns': 'generate_a_joke:5bd10d6b-e72c-d811-6b1f-e1baf600e1a5', 'ls_provider': 'openai', 'ls_model_name': 'Qwen/Qwen2.5-7B-Instruct', 'ls_model_type': 'chat', 'ls_temperature': None}
# 网站
# 43 {'langgraph_step': 1, 'langgraph_node': 'generate_a_joke', 'langgraph_triggers': ('branch:to:generate_a_joke',), 'langgraph_path': ('__pregel_pull', 'generate_a_joke'), 'langgraph_checkpoint_ns': 'generate_a_joke:5bd10d6b-e72c-d811-6b1f-e1baf600e1a5', 'checkpoint_ns': 'generate_a_joke:5bd10d6b-e72c-d811-6b1f-e1baf600e1a5', 'ls_provider': 'openai', 'ls_model_name': 'Qwen/Qwen2.5-7B-Instruct', 'ls_model_type': 'chat', 'ls_temperature': None}
# 如
# 44 {'langgraph_step': 1, 'langgraph_node': 'generate_a_joke', 'langgraph_triggers': ('branch:to:generate_a_joke',), 'langgraph_path': ('__pregel_pull', 'generate_a_joke'), 'langgraph_checkpoint_ns': 'generate_a_joke:5bd10d6b-e72c-d811-6b1f-e1baf600e1a5', 'checkpoint_ns': 'generate_a_joke:5bd10d6b-e72c-d811-6b1f-e1baf600e1a5', 'ls_provider': 'openai', 'ls_model_name': 'Qwen/Qwen2.5-7B-Instruct', 'ls_model_type': 'chat', 'ls_temperature': None}
# 中国
# 45 {'langgraph_step': 1, 'langgraph_node': 'generate_a_joke', 'langgraph_triggers': ('branch:to:generate_a_joke',), 'langgraph_path': ('__pregel_pull', 'generate_a_joke'), 'langgraph_checkpoint_ns': 'generate_a_joke:5bd10d6b-e72c-d811-6b1f-e1baf600e1a5', 'checkpoint_ns': 'generate_a_joke:5bd10d6b-e72c-d811-6b1f-e1baf600e1a5', 'ls_provider': 'openai', 'ls_model_name': 'Qwen/Qwen2.5-7B-Instruct', 'ls_model_type': 'chat', 'ls_temperature': None}
# 气象
# 46 {'langgraph_step': 1, 'langgraph_node': 'generate_a_joke', 'langgraph_triggers': ('branch:to:generate_a_joke',), 'langgraph_path': ('__pregel_pull', 'generate_a_joke'), 'langgraph_checkpoint_ns': 'generate_a_joke:5bd10d6b-e72c-d811-6b1f-e1baf600e1a5', 'checkpoint_ns': 'generate_a_joke:5bd10d6b-e72c-d811-6b1f-e1baf600e1a5', 'ls_provider': 'openai', 'ls_model_name': 'Qwen/Qwen2.5-7B-Instruct', 'ls_model_type': 'chat', 'ls_temperature': None}
# 局
# 47 {'langgraph_step': 1, 'langgraph_node': 'generate_a_joke', 'langgraph_triggers': ('branch:to:generate_a_joke',), 'langgraph_path': ('__pregel_pull', 'generate_a_joke'), 'langgraph_checkpoint_ns': 'generate_a_joke:5bd10d6b-e72c-d811-6b1f-e1baf600e1a5', 'checkpoint_ns': 'generate_a_joke:5bd10d6b-e72c-d811-6b1f-e1baf600e1a5', 'ls_provider': 'openai', 'ls_model_name': 'Qwen/Qwen2.5-7B-Instruct', 'ls_model_type': 'chat', 'ls_temperature': None}
# 网站
# 48 {'langgraph_step': 1, 'langgraph_node': 'generate_a_joke', 'langgraph_triggers': ('branch:to:generate_a_joke',), 'langgraph_path': ('__pregel_pull', 'generate_a_joke'), 'langgraph_checkpoint_ns': 'generate_a_joke:5bd10d6b-e72c-d811-6b1f-e1baf600e1a5', 'checkpoint_ns': 'generate_a_joke:5bd10d6b-e72c-d811-6b1f-e1baf600e1a5', 'ls_provider': 'openai', 'ls_model_name': 'Qwen/Qwen2.5-7B-Instruct', 'ls_model_type': 'chat', 'ls_temperature': None}
# ，
# 49 {'langgraph_step': 1, 'langgraph_node': 'generate_a_joke', 'langgraph_triggers': ('branch:to:generate_a_joke',), 'langgraph_path': ('__pregel_pull', 'generate_a_joke'), 'langgraph_checkpoint_ns': 'generate_a_joke:5bd10d6b-e72c-d811-6b1f-e1baf600e1a5', 'checkpoint_ns': 'generate_a_joke:5bd10d6b-e72c-d811-6b1f-e1baf600e1a5', 'ls_provider': 'openai', 'ls_model_name': 'Qwen/Qwen2.5-7B-Instruct', 'ls_model_type': 'chat', 'ls_temperature': None}
# 以
# 50 {'langgraph_step': 1, 'langgraph_node': 'generate_a_joke', 'langgraph_triggers': ('branch:to:generate_a_joke',), 'langgraph_path': ('__pregel_pull', 'generate_a_joke'), 'langgraph_checkpoint_ns': 'generate_a_joke:5bd10d6b-e72c-d811-6b1f-e1baf600e1a5', 'checkpoint_ns': 'generate_a_joke:5bd10d6b-e72c-d811-6b1f-e1baf600e1a5', 'ls_provider': 'openai', 'ls_model_name': 'Qwen/Qwen2.5-7B-Instruct', 'ls_model_type': 'chat', 'ls_temperature': None}
# 获取
# 51 {'langgraph_step': 1, 'langgraph_node': 'generate_a_joke', 'langgraph_triggers': ('branch:to:generate_a_joke',), 'langgraph_path': ('__pregel_pull', 'generate_a_joke'), 'langgraph_checkpoint_ns': 'generate_a_joke:5bd10d6b-e72c-d811-6b1f-e1baf600e1a5', 'checkpoint_ns': 'generate_a_joke:5bd10d6b-e72c-d811-6b1f-e1baf600e1a5', 'ls_provider': 'openai', 'ls_model_name': 'Qwen/Qwen2.5-7B-Instruct', 'ls_model_type': 'chat', 'ls_temperature': None}
# 最
# 52 {'langgraph_step': 1, 'langgraph_node': 'generate_a_joke', 'langgraph_triggers': ('branch:to:generate_a_joke',), 'langgraph_path': ('__pregel_pull', 'generate_a_joke'), 'langgraph_checkpoint_ns': 'generate_a_joke:5bd10d6b-e72c-d811-6b1f-e1baf600e1a5', 'checkpoint_ns': 'generate_a_joke:5bd10d6b-e72c-d811-6b1f-e1baf600e1a5', 'ls_provider': 'openai', 'ls_model_name': 'Qwen/Qwen2.5-7B-Instruct', 'ls_model_type': 'chat', 'ls_temperature': None}
# 准确
# 53 {'langgraph_step': 1, 'langgraph_node': 'generate_a_joke', 'langgraph_triggers': ('branch:to:generate_a_joke',), 'langgraph_path': ('__pregel_pull', 'generate_a_joke'), 'langgraph_checkpoint_ns': 'generate_a_joke:5bd10d6b-e72c-d811-6b1f-e1baf600e1a5', 'checkpoint_ns': 'generate_a_joke:5bd10d6b-e72c-d811-6b1f-e1baf600e1a5', 'ls_provider': 'openai', 'ls_model_name': 'Qwen/Qwen2.5-7B-Instruct', 'ls_model_type': 'chat', 'ls_temperature': None}
# 和
# 54 {'langgraph_step': 1, 'langgraph_node': 'generate_a_joke', 'langgraph_triggers': ('branch:to:generate_a_joke',), 'langgraph_path': ('__pregel_pull', 'generate_a_joke'), 'langgraph_checkpoint_ns': 'generate_a_joke:5bd10d6b-e72c-d811-6b1f-e1baf600e1a5', 'checkpoint_ns': 'generate_a_joke:5bd10d6b-e72c-d811-6b1f-e1baf600e1a5', 'ls_provider': 'openai', 'ls_model_name': 'Qwen/Qwen2.5-7B-Instruct', 'ls_model_type': 'chat', 'ls_temperature': None}
# 最新的
# 55 {'langgraph_step': 1, 'langgraph_node': 'generate_a_joke', 'langgraph_triggers': ('branch:to:generate_a_joke',), 'langgraph_path': ('__pregel_pull', 'generate_a_joke'), 'langgraph_checkpoint_ns': 'generate_a_joke:5bd10d6b-e72c-d811-6b1f-e1baf600e1a5', 'checkpoint_ns': 'generate_a_joke:5bd10d6b-e72c-d811-6b1f-e1baf600e1a5', 'ls_provider': 'openai', 'ls_model_name': 'Qwen/Qwen2.5-7B-Instruct', 'ls_model_type': 'chat', 'ls_temperature': None}
# 天气
# 56 {'langgraph_step': 1, 'langgraph_node': 'generate_a_joke', 'langgraph_triggers': ('branch:to:generate_a_joke',), 'langgraph_path': ('__pregel_pull', 'generate_a_joke'), 'langgraph_checkpoint_ns': 'generate_a_joke:5bd10d6b-e72c-d811-6b1f-e1baf600e1a5', 'checkpoint_ns': 'generate_a_joke:5bd10d6b-e72c-d811-6b1f-e1baf600e1a5', 'ls_provider': 'openai', 'ls_model_name': 'Qwen/Qwen2.5-7B-Instruct', 'ls_model_type': 'chat', 'ls_temperature': None}
# 预报
# 57 {'langgraph_step': 1, 'langgraph_node': 'generate_a_joke', 'langgraph_triggers': ('branch:to:generate_a_joke',), 'langgraph_path': ('__pregel_pull', 'generate_a_joke'), 'langgraph_checkpoint_ns': 'generate_a_joke:5bd10d6b-e72c-d811-6b1f-e1baf600e1a5', 'checkpoint_ns': 'generate_a_joke:5bd10d6b-e72c-d811-6b1f-e1baf600e1a5', 'ls_provider': 'openai', 'ls_model_name': 'Qwen/Qwen2.5-7B-Instruct', 'ls_model_type': 'chat', 'ls_temperature': None}
# 。
# 58 {'langgraph_step': 1, 'langgraph_node': 'generate_a_joke', 'langgraph_triggers': ('branch:to:generate_a_joke',), 'langgraph_path': ('__pregel_pull', 'generate_a_joke'), 'langgraph_checkpoint_ns': 'generate_a_joke:5bd10d6b-e72c-d811-6b1f-e1baf600e1a5', 'checkpoint_ns': 'generate_a_joke:5bd10d6b-e72c-d811-6b1f-e1baf600e1a5', 'ls_provider': 'openai', 'ls_model_name': 'Qwen/Qwen2.5-7B-Instruct', 'ls_model_type': 'chat', 'ls_temperature': None}
# 这些
# 59 {'langgraph_step': 1, 'langgraph_node': 'generate_a_joke', 'langgraph_triggers': ('branch:to:generate_a_joke',), 'langgraph_path': ('__pregel_pull', 'generate_a_joke'), 'langgraph_checkpoint_ns': 'generate_a_joke:5bd10d6b-e72c-d811-6b1f-e1baf600e1a5', 'checkpoint_ns': 'generate_a_joke:5bd10d6b-e72c-d811-6b1f-e1baf600e1a5', 'ls_provider': 'openai', 'ls_model_name': 'Qwen/Qwen2.5-7B-Instruct', 'ls_model_type': 'chat', 'ls_temperature': None}
# 平台
# 60 {'langgraph_step': 1, 'langgraph_node': 'generate_a_joke', 'langgraph_triggers': ('branch:to:generate_a_joke',), 'langgraph_path': ('__pregel_pull', 'generate_a_joke'), 'langgraph_checkpoint_ns': 'generate_a_joke:5bd10d6b-e72c-d811-6b1f-e1baf600e1a5', 'checkpoint_ns': 'generate_a_joke:5bd10d6b-e72c-d811-6b1f-e1baf600e1a5', 'ls_provider': 'openai', 'ls_model_name': 'Qwen/Qwen2.5-7B-Instruct', 'ls_model_type': 'chat', 'ls_temperature': None}
# 通常
# 61 {'langgraph_step': 1, 'langgraph_node': 'generate_a_joke', 'langgraph_triggers': ('branch:to:generate_a_joke',), 'langgraph_path': ('__pregel_pull', 'generate_a_joke'), 'langgraph_checkpoint_ns': 'generate_a_joke:5bd10d6b-e72c-d811-6b1f-e1baf600e1a5', 'checkpoint_ns': 'generate_a_joke:5bd10d6b-e72c-d811-6b1f-e1baf600e1a5', 'ls_provider': 'openai', 'ls_model_name': 'Qwen/Qwen2.5-7B-Instruct', 'ls_model_type': 'chat', 'ls_temperature': None}
# 能够
# 62 {'langgraph_step': 1, 'langgraph_node': 'generate_a_joke', 'langgraph_triggers': ('branch:to:generate_a_joke',), 'langgraph_path': ('__pregel_pull', 'generate_a_joke'), 'langgraph_checkpoint_ns': 'generate_a_joke:5bd10d6b-e72c-d811-6b1f-e1baf600e1a5', 'checkpoint_ns': 'generate_a_joke:5bd10d6b-e72c-d811-6b1f-e1baf600e1a5', 'ls_provider': 'openai', 'ls_model_name': 'Qwen/Qwen2.5-7B-Instruct', 'ls_model_type': 'chat', 'ls_temperature': None}
# 提供
# 63 {'langgraph_step': 1, 'langgraph_node': 'generate_a_joke', 'langgraph_triggers': ('branch:to:generate_a_joke',), 'langgraph_path': ('__pregel_pull', 'generate_a_joke'), 'langgraph_checkpoint_ns': 'generate_a_joke:5bd10d6b-e72c-d811-6b1f-e1baf600e1a5', 'checkpoint_ns': 'generate_a_joke:5bd10d6b-e72c-d811-6b1f-e1baf600e1a5', 'ls_provider': 'openai', 'ls_model_name': 'Qwen/Qwen2.5-7B-Instruct', 'ls_model_type': 'chat', 'ls_temperature': None}
# 包括
# 64 {'langgraph_step': 1, 'langgraph_node': 'generate_a_joke', 'langgraph_triggers': ('branch:to:generate_a_joke',), 'langgraph_path': ('__pregel_pull', 'generate_a_joke'), 'langgraph_checkpoint_ns': 'generate_a_joke:5bd10d6b-e72c-d811-6b1f-e1baf600e1a5', 'checkpoint_ns': 'generate_a_joke:5bd10d6b-e72c-d811-6b1f-e1baf600e1a5', 'ls_provider': 'openai', 'ls_model_name': 'Qwen/Qwen2.5-7B-Instruct', 'ls_model_type': 'chat', 'ls_temperature': None}
# 温度
# 65 {'langgraph_step': 1, 'langgraph_node': 'generate_a_joke', 'langgraph_triggers': ('branch:to:generate_a_joke',), 'langgraph_path': ('__pregel_pull', 'generate_a_joke'), 'langgraph_checkpoint_ns': 'generate_a_joke:5bd10d6b-e72c-d811-6b1f-e1baf600e1a5', 'checkpoint_ns': 'generate_a_joke:5bd10d6b-e72c-d811-6b1f-e1baf600e1a5', 'ls_provider': 'openai', 'ls_model_name': 'Qwen/Qwen2.5-7B-Instruct', 'ls_model_type': 'chat', 'ls_temperature': None}
# 、
# 66 {'langgraph_step': 1, 'langgraph_node': 'generate_a_joke', 'langgraph_triggers': ('branch:to:generate_a_joke',), 'langgraph_path': ('__pregel_pull', 'generate_a_joke'), 'langgraph_checkpoint_ns': 'generate_a_joke:5bd10d6b-e72c-d811-6b1f-e1baf600e1a5', 'checkpoint_ns': 'generate_a_joke:5bd10d6b-e72c-d811-6b1f-e1baf600e1a5', 'ls_provider': 'openai', 'ls_model_name': 'Qwen/Qwen2.5-7B-Instruct', 'ls_model_type': 'chat', 'ls_temperature': None}
# 降水
# 67 {'langgraph_step': 1, 'langgraph_node': 'generate_a_joke', 'langgraph_triggers': ('branch:to:generate_a_joke',), 'langgraph_path': ('__pregel_pull', 'generate_a_joke'), 'langgraph_checkpoint_ns': 'generate_a_joke:5bd10d6b-e72c-d811-6b1f-e1baf600e1a5', 'checkpoint_ns': 'generate_a_joke:5bd10d6b-e72c-d811-6b1f-e1baf600e1a5', 'ls_provider': 'openai', 'ls_model_name': 'Qwen/Qwen2.5-7B-Instruct', 'ls_model_type': 'chat', 'ls_temperature': None}
# 概率
# 68 {'langgraph_step': 1, 'langgraph_node': 'generate_a_joke', 'langgraph_triggers': ('branch:to:generate_a_joke',), 'langgraph_path': ('__pregel_pull', 'generate_a_joke'), 'langgraph_checkpoint_ns': 'generate_a_joke:5bd10d6b-e72c-d811-6b1f-e1baf600e1a5', 'checkpoint_ns': 'generate_a_joke:5bd10d6b-e72c-d811-6b1f-e1baf600e1a5', 'ls_provider': 'openai', 'ls_model_name': 'Qwen/Qwen2.5-7B-Instruct', 'ls_model_type': 'chat', 'ls_temperature': None}
# 、
# 69 {'langgraph_step': 1, 'langgraph_node': 'generate_a_joke', 'langgraph_triggers': ('branch:to:generate_a_joke',), 'langgraph_path': ('__pregel_pull', 'generate_a_joke'), 'langgraph_checkpoint_ns': 'generate_a_joke:5bd10d6b-e72c-d811-6b1f-e1baf600e1a5', 'checkpoint_ns': 'generate_a_joke:5bd10d6b-e72c-d811-6b1f-e1baf600e1a5', 'ls_provider': 'openai', 'ls_model_name': 'Qwen/Qwen2.5-7B-Instruct', 'ls_model_type': 'chat', 'ls_temperature': None}
# 风
# 70 {'langgraph_step': 1, 'langgraph_node': 'generate_a_joke', 'langgraph_triggers': ('branch:to:generate_a_joke',), 'langgraph_path': ('__pregel_pull', 'generate_a_joke'), 'langgraph_checkpoint_ns': 'generate_a_joke:5bd10d6b-e72c-d811-6b1f-e1baf600e1a5', 'checkpoint_ns': 'generate_a_joke:5bd10d6b-e72c-d811-6b1f-e1baf600e1a5', 'ls_provider': 'openai', 'ls_model_name': 'Qwen/Qwen2.5-7B-Instruct', 'ls_model_type': 'chat', 'ls_temperature': None}
# 速
# 71 {'langgraph_step': 1, 'langgraph_node': 'generate_a_joke', 'langgraph_triggers': ('branch:to:generate_a_joke',), 'langgraph_path': ('__pregel_pull', 'generate_a_joke'), 'langgraph_checkpoint_ns': 'generate_a_joke:5bd10d6b-e72c-d811-6b1f-e1baf600e1a5', 'checkpoint_ns': 'generate_a_joke:5bd10d6b-e72c-d811-6b1f-e1baf600e1a5', 'ls_provider': 'openai', 'ls_model_name': 'Qwen/Qwen2.5-7B-Instruct', 'ls_model_type': 'chat', 'ls_temperature': None}
# 和
# 72 {'langgraph_step': 1, 'langgraph_node': 'generate_a_joke', 'langgraph_triggers': ('branch:to:generate_a_joke',), 'langgraph_path': ('__pregel_pull', 'generate_a_joke'), 'langgraph_checkpoint_ns': 'generate_a_joke:5bd10d6b-e72c-d811-6b1f-e1baf600e1a5', 'checkpoint_ns': 'generate_a_joke:5bd10d6b-e72c-d811-6b1f-e1baf600e1a5', 'ls_provider': 'openai', 'ls_model_name': 'Qwen/Qwen2.5-7B-Instruct', 'ls_model_type': 'chat', 'ls_temperature': None}
# 湿度
# 73 {'langgraph_step': 1, 'langgraph_node': 'generate_a_joke', 'langgraph_triggers': ('branch:to:generate_a_joke',), 'langgraph_path': ('__pregel_pull', 'generate_a_joke'), 'langgraph_checkpoint_ns': 'generate_a_joke:5bd10d6b-e72c-d811-6b1f-e1baf600e1a5', 'checkpoint_ns': 'generate_a_joke:5bd10d6b-e72c-d811-6b1f-e1baf600e1a5', 'ls_provider': 'openai', 'ls_model_name': 'Qwen/Qwen2.5-7B-Instruct', 'ls_model_type': 'chat', 'ls_temperature': None}
# 等
# 74 {'langgraph_step': 1, 'langgraph_node': 'generate_a_joke', 'langgraph_triggers': ('branch:to:generate_a_joke',), 'langgraph_path': ('__pregel_pull', 'generate_a_joke'), 'langgraph_checkpoint_ns': 'generate_a_joke:5bd10d6b-e72c-d811-6b1f-e1baf600e1a5', 'checkpoint_ns': 'generate_a_joke:5bd10d6b-e72c-d811-6b1f-e1baf600e1a5', 'ls_provider': 'openai', 'ls_model_name': 'Qwen/Qwen2.5-7B-Instruct', 'ls_model_type': 'chat', 'ls_temperature': None}
# 在内的
# 75 {'langgraph_step': 1, 'langgraph_node': 'generate_a_joke', 'langgraph_triggers': ('branch:to:generate_a_joke',), 'langgraph_path': ('__pregel_pull', 'generate_a_joke'), 'langgraph_checkpoint_ns': 'generate_a_joke:5bd10d6b-e72c-d811-6b1f-e1baf600e1a5', 'checkpoint_ns': 'generate_a_joke:5bd10d6b-e72c-d811-6b1f-e1baf600e1a5', 'ls_provider': 'openai', 'ls_model_name': 'Qwen/Qwen2.5-7B-Instruct', 'ls_model_type': 'chat', 'ls_temperature': None}
# 详细
# 76 {'langgraph_step': 1, 'langgraph_node': 'generate_a_joke', 'langgraph_triggers': ('branch:to:generate_a_joke',), 'langgraph_path': ('__pregel_pull', 'generate_a_joke'), 'langgraph_checkpoint_ns': 'generate_a_joke:5bd10d6b-e72c-d811-6b1f-e1baf600e1a5', 'checkpoint_ns': 'generate_a_joke:5bd10d6b-e72c-d811-6b1f-e1baf600e1a5', 'ls_provider': 'openai', 'ls_model_name': 'Qwen/Qwen2.5-7B-Instruct', 'ls_model_type': 'chat', 'ls_temperature': None}
# 天气
# 77 {'langgraph_step': 1, 'langgraph_node': 'generate_a_joke', 'langgraph_triggers': ('branch:to:generate_a_joke',), 'langgraph_path': ('__pregel_pull', 'generate_a_joke'), 'langgraph_checkpoint_ns': 'generate_a_joke:5bd10d6b-e72c-d811-6b1f-e1baf600e1a5', 'checkpoint_ns': 'generate_a_joke:5bd10d6b-e72c-d811-6b1f-e1baf600e1a5', 'ls_provider': 'openai', 'ls_model_name': 'Qwen/Qwen2.5-7B-Instruct', 'ls_model_type': 'chat', 'ls_temperature': None}
# 信息
# 78 {'langgraph_step': 1, 'langgraph_node': 'generate_a_joke', 'langgraph_triggers': ('branch:to:generate_a_joke',), 'langgraph_path': ('__pregel_pull', 'generate_a_joke'), 'langgraph_checkpoint_ns': 'generate_a_joke:5bd10d6b-e72c-d811-6b1f-e1baf600e1a5', 'checkpoint_ns': 'generate_a_joke:5bd10d6b-e72c-d811-6b1f-e1baf600e1a5', 'ls_provider': 'openai', 'ls_model_name': 'Qwen/Qwen2.5-7B-Instruct', 'ls_model_type': 'chat', 'ls_temperature': None}
# 。
# 79 {'langgraph_step': 1, 'langgraph_node': 'generate_a_joke', 'langgraph_triggers': ('branch:to:generate_a_joke',), 'langgraph_path': ('__pregel_pull', 'generate_a_joke'), 'langgraph_checkpoint_ns': 'generate_a_joke:5bd10d6b-e72c-d811-6b1f-e1baf600e1a5', 'checkpoint_ns': 'generate_a_joke:5bd10d6b-e72c-d811-6b1f-e1baf600e1a5', 'ls_provider': 'openai', 'ls_model_name': 'Qwen/Qwen2.5-7B-Instruct', 'ls_model_type': 'chat', 'ls_temperature': None}
# %% 4-7 stream_mode="debug"
for chunk in agent.stream({"topic": "天气"}, stream_mode="debug"):  # type: ignore
    print(chunk)  # type: ignore

# %% 4-8 组合模式
from typing import TypedDict  # noqa: E402
from langgraph.graph import StateGraph, START  # noqa: E402
from langgraph.types import StreamWriter  # noqa: E402


class MyState(TypedDict):  # type: ignore
    topic: str
    joke: str


def refine_topic(state: MyState):  # type: ignore
    return {"topic": state["topic"] + " and cats"}


def generate_a_joke(state: MyState, writer: StreamWriter):  # type: ignore
    writer({"custom_key": "writing custom data while generating a joke"})
    return {"joke": f"This is a joke about {state['topic']}"}


graph = StateGraph(MyState)
graph.add_node(refine_topic)
graph.add_node(generate_a_joke)
graph.add_edge(START, "refine_topic")
graph.add_edge("refine_topic", "generate_a_joke")

agent = graph.compile()

for stream_mode, chunk in agent.stream(
    {"topic": "ice cream"},  # type: ignore
    stream_mode=["updates", "custom"],
):
    print(f"stream mode: {stream_mode}")
    print(chunk)
    print()

# stream mode: updates
# {'refine_topic': {'topic': 'ice cream and cats'}}

# stream mode: custom
# {'custom_key': 'writing custom data while generating a joke'}

# stream mode: updates
# {'generate_a_joke': {'joke': 'This is a joke about ice cream and cats'}}
