# %% 4-15 使用graph.get_state_history()浏览执行历史记录
from typing import TypedDict
from langgraph.graph import StateGraph, START, END
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver


class MyState(TypedDict):
    topic: str
    joke: str


def refine_topic_node(state: MyState) -> MyState:
    return {"joke": state["topic"] + "和猫"}  # type: ignore


def generate_a_joke_node(state: MyState) -> MyState:
    llm = ChatOpenAI(model="Qwen/Qwen2.5-7B-Instruct")
    llm_response = llm.invoke(
        [{"role": "user", "content": f"generate a joke about {state['topic']}"}]
    )
    return {"joke": llm_response.content}


graph = StateGraph(MyState)
graph.add_node(refine_topic_node)
graph.add_node(generate_a_joke_node)
graph.set_entry_point(refine_topic_node.__name__)
graph.add_edge(refine_topic_node.__name__, generate_a_joke_node.__name__)

agent = graph.compile(checkpointer=MemorySaver())

config = {"configurable": {"thread_id": "my_thread_1"}}
for chunk in agent.stream({"topic": "冰淇淋"}, config=config, stream_mode="values"):
    rprint(chunk)

agent.get_state(config)

# {'topic': '冰淇淋'}
# {'topic': '冰淇淋', 'joke': '冰淇淋和猫'}
# {
#     'topic': '冰淇淋',
#     'joke':
# '当然可以！这里有一个关于冰淇淋的中文笑话：\n\n为什么冰淇淋不喜欢上网？\n\n因为它一上网，就总是“融化”了……（这里的“
# 融化”跟英文中的“登录”MDB Logan谐音，MDB Logan在英文中意为“总是登录”）'
# }
# %%
list(agent.get_state_history(config))

# %%
state_history = list(agent.get_state_history(config))
for snapshot in state_history:
    rprint(f"存档点 ID： {snapshot.config['configurable']['checkpoint_id']}")
    rprint(f"步骤metadata: {snapshot.metadata}")
    rprint(f"父图状态值: {snapshot.values}")
    rprint(f"下一个节点： {snapshot.next}")


# %% 重放
state_history = list(agent.get_state_history(config))
checkpoint_to_reply = state_history[2]
reply_config = checkpoint_to_reply.config
for chunk in agent.stream(None, reply_config, stream_mode="values"):
    rprint(chunk)

# {'topic': '冰淇淋'}
# {'topic': '冰淇淋', 'joke': '冰淇淋和猫'}
# {
#     'topic': '冰淇淋',
#     'joke':
# '当然可以！这里有一个关于冰淇淋的中文笑话：\n\n为什么冰淇淋不喜欢上网？\n\n因为它一上网，就总是“融化”了……（这里的“
# 融化”跟英文中的“登录”MDB Logan谐音，MDB Logan在英文中意为“总是登录”）'
# }


# %% 创建分支 使用.update_state(..., values)从存档点分支执行

checkpoint_to_branch = state_history[1]
branch_config = checkpoint_to_branch.config
new_branch = agent.update_state(branch_config, {"topic": "冰淇淋和狗"})

for chunk in agent.stream(None, new_branch, stream_mode="values"):
    rprint(chunk)

# {'topic': '冰淇淋和狗', 'joke': '冰淇淋和猫'}
# {
#     'topic': '冰淇淋和狗',
#     'joke':
# '当然可以！这里有一个关于冰淇淋和狗的中文笑话：\n\n为什么冰淇淋不喜欢和狗一起玩？\n\n因为它怕被“汪”一口！'
# }

"""
可以看到
第一个chunk是{'topic': '冰淇淋'}
第二个chunk是{'topic': '冰淇淋', 'joke': '冰淇淋和猫'}
第三个chunk是 
{
    'topic': '冰淇淋',
    'joke':
'当然可以！这里有一个关于冰淇淋的中文笑话：\n\n为什么冰淇淋不喜欢上网？\n\n因为它一上网，就总是“融化”了……（这里的“
融化”跟英文中的“登录”MDB Logan谐音，MDB Logan在英文中意为“总是登录”）'
}

从第二个主题被改了之后
chunk是{'topic': '冰淇淋和狗', 'joke': '冰淇淋和猫'}
然后第三个chunk成为了
{
    'topic': '冰淇淋和狗',
    'joke':
'当然可以！这里有一个关于冰淇淋和狗的中文笑话：\n\n为什么冰淇淋不喜欢和狗一起玩？\n\n因为它怕被“汪”一口！'
}

"""

# %% 子图subgraphs
from typing import TypedDict
from langgraph.graph import StateGraph, START, END
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver


class MyState(TypedDict):
    topic: str
    joke: str


def refine_topic_node(state: MyState) -> MyState:
    return {"joke": state["topic"] + "和猫"}  # type: ignore


def generate_a_joke_node(state: MyState) -> MyState:
    llm = ChatOpenAI(model="Qwen/Qwen2.5-7B-Instruct")
    llm_response = llm.invoke(
        [{"role": "user", "content": f"generate a joke about {state['topic']}"}]
    )
    return {"joke": llm_response.content}


graph = StateGraph(MyState)
graph.add_node(refine_topic_node)
graph.add_node(generate_a_joke_node)
graph.set_entry_point(refine_topic_node.__name__)
graph.add_edge(refine_topic_node.__name__, generate_a_joke_node.__name__)

agent = graph.compile(checkpointer=MemorySaver())
config = {"configurable": {"thread_id": "my_thread_1"}}
agent.stream({"topic": "冰淇淋"}, config=config, stream_mode="values")
subgraphs = agent.get_state(config, subgraphs=True)

# StateSnapshot(
#     values={
#         'topic': '冰淇淋和狗',
#         'joke': '当然，这里有一个关于冰激凌和狗的冷笑话：\n\n为什么冰激凌店里的狗最受欢迎？\n\n因为冰激凌总是说：“你真舔（香）！”\n\n（注：这里的“舔”听起来很像“香”，所以是冰激凌在夸奖狗狗。）'
#     },
#     next=(),
#     config={
#         'configurable': {
#             'thread_id': 'my_thread_1',
#             'checkpoint_ns': '',
#             'checkpoint_id': '1f0de371-f684-6f62-8003-d0c2f878c744'
#         }
#     },
#     metadata={'source': 'loop', 'step': 3, 'parents': {}},
#     created_at='2025-12-21T06:34:37.998200+00:00',
#     parent_config={
#         'configurable': {
#             'thread_id': 'my_thread_1',
#             'checkpoint_ns': '',
#             'checkpoint_id': '1f0de371-ee92-62b4-8002-adc3f2f9589f'
#         }
#     },
#     tasks=(),
#     interrupts=()
# )
