# %% 6-13 在Functional API工作流中实现任务的并行执行
from langgraph.func import task, entrypoint
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.runnables.config import RunnableConfig
import time


@task
def task_one(item):
    time.sleep(2)
    return f"任务一处理:{item}"


@task
def task_two(item):
    time.sleep(5)
    return f"任务二处理:{item}"


@entrypoint(checkpointer=MemorySaver())
def parallel_workflow(items: list) -> dict:
    futures = [task_one(item) for item in items]
    results_task_one = [f.result() for f in futures]
    futures2 = [task_two(item) for item in items]
    results_task_two = [f.result() for f in futures2]
    return {"task_one_results": results_task_one, "task_two_results": results_task_two}


config: RunnableConfig = {"configurable": {"thread_id": "thread_id_1600"}}
items = ["item_a", "item_b", "item_c"]
starttime = time.time()
parallel_results = parallel_workflow.invoke(items, config=config)
print(parallel_results)
print(time.time() - starttime)
# {'task_one_results': ['任务一处理:item_a', '任务一处理:item_b', '任务一处理:item_c'], 'task_two_results': ['任务二处理:item_a', '任务二处理:item_b', '任务二处理:item_c']}
# 7.027064800262451

# 前后只花了7s，说明task_one的3个是同时执行的。task_two的3个也是同时执行的。


# %% 6-14 在Functional API中调用子图

from langgraph.func import task, entrypoint
from langgraph.checkpoint.memory import MemorySaver


@entrypoint(checkpointer=MemorySaver())
def inner_workflow(value: str) -> str:
    return value


@entrypoint(checkpointer=MemorySaver())
def outer_workflow(value: str) -> dict:
    inner_result = inner_workflow.invoke("inner input...")
    print(inner_workflow.get_state(config))
    # StateSnapshot(
    #     values={},
    #     next=(),
    #     config={'configurable': {'thread_id': 'thread_1617'}},
    #     metadata=None,
    #     created_at=None,
    #     parent_config=None,
    #     tasks=(),
    #     interrupts=()
    # )
    return {"output": value, "inner": inner_result}


config = {"configurable": {"thread_id": "thread_1617"}}
result = outer_workflow.invoke("outer input...", config=config)
print(result)
# {'output': 'outer input...', 'inner': 'inner input...'}


outer_workflow.get_state(config)
# StateSnapshot(
#     values={'output': 'outer input...', 'inner': 'inner input...'},
#     next=(),
#     config={
#         'configurable': {
#             'thread_id': 'thread_1617',
#             'checkpoint_ns': '',
#             'checkpoint_id': '1f0e16b2-ca0e-64aa-8000-cf57d0923a16'
#         }
#     },
#     metadata={'source': 'loop', 'step': 0, 'parents': {}},
#     created_at='2025-12-25T08:24:47.497736+00:00',
#     parent_config={
#         'configurable': {
#             'thread_id': 'thread_1617',
#             'checkpoint_ns': '',
#             'checkpoint_id': '1f0e16b2-c9fa-60b8-bfff-5162e6a571fb'
#         }
#     },
#     tasks=(),
#     interrupts=()
# )

# %% 6-15 在Functional API中演示自定义数据流式传输

from langgraph.func import task, entrypoint
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import StreamWriter


@entrypoint(checkpointer=MemorySaver())
def streaming_workflow(input_value, writer: StreamWriter):
    writer({"key1": '"工作流开始..."'})
    result = f"正在处理{input_value}"
    writer("工作流结束...")
    return result


config = {"configurable": {"thread_id": "thread_id_1630"}}
for chunk in streaming_workflow.stream(
    "hehe...", config, stream_mode=["custom", "updates"]
):
    print(f"stream chunk: {chunk}")


""" 这是stream_mode=['custom', 'values']的结果
stream chunk: ('custom', '工作流开始...')
stream chunk: ('custom', '工作流结束...')
stream chunk: ('values', '正在处理hehe...')
) 

这是stream_mode=['custom', 'updates']的结果

stream chunk: ('custom', '工作流开始...')
stream chunk: ('custom', '工作流结束...')
stream chunk: ('updates', {'streaming_workflow': '正在处理hehe...'})
"""

# %% 6-16 在Functional API中实现重试策略
from langgraph.func import task, entrypoint
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import RetryPolicy

retry_policy = RetryPolicy(max_attempts=3, retry_on=ValueError)


@task(retry_policy=retry_policy)
def unreliable_task():
    print(1)
    import random

    if random.random() < 0.8:
        raise ValueError("任务失败！")
    return "ok..."


@entrypoint(checkpointer=MemorySaver())
def retry_workflow(input: str):
    result = unreliable_task().result()
    return result


config = {"configurable": {"thread_id": "thread_id_1720"}}
result = retry_workflow.invoke("test input...", config)
result

""" 
1
1
1
ValueError: 任务失败！                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     
"""

# %% 6-17 在Functional API中实现短期记忆
from langgraph.func import entrypoint
from langgraph.checkpoint.memory import MemorySaver


@entrypoint(checkpointer=MemorySaver())
def counter_workflow(increment: int, previous):
    previous = previous or 0
    current_count = previous + increment
    return entrypoint.final(value=current_count, save=current_count)


config = {"configurable": {"thread_id": {"thread_id_1806"}}}
print(counter_workflow.invoke(1, config))
print(counter_workflow.invoke(2, config))
print(counter_workflow.invoke(3, config))

""" 
1
3
6
"""

# %% 6-18 在Functional API中管理长期记忆
