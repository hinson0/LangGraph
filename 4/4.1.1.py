# %% 4-9 使用astream_events()执行图的输出

from langchain_openai import ChatOpenAI  # noqa: E402
from langgraph.graph import StateGraph, START, END, MessagesState  # noqa: E402
import asyncio
# from IPython.display import display

model = ChatOpenAI(model="Qwen/Qwen2.5-7B-Instruct")


def call_model_node(state: MessagesState):
    return {"messages": model.invoke(state["messages"])}


graph = StateGraph(MessagesState)
graph.add_node(call_model_node)
graph.add_edge(START, "call_model_node")
graph.add_edge("call_model_node", END)

agent = graph.compile()


async def start():
    messages = [{"role": "user", "content": "hello."}]
    async for event in agent.astream_events({"messages": messages}, version="v1"):
        kind = event["event"]
        display(event)
        # print(f"{kind}: {event['name']} {event['data']}")


# on_chain_start: LangGraph # 图开始触发on_chain_start，每次节点
#     on_chain_start: call_model_node # 节点开始触发on_chain_start
#         on_chat_model_start: ChatOpenAI # 节点触发on_chat_model_start，节点名字是ChatOpenAI
#             on_chat_model_stream: ChatOpenAI
#             on_chat_model_stream: ChatOpenAI
#             on_chat_model_stream: ChatOpenAI
#             on_chat_model_stream: ChatOpenAI
#             on_chat_model_stream: ChatOpenAI
#             on_chat_model_stream: ChatOpenAI
#             on_chat_model_stream: ChatOpenAI
#             on_chat_model_stream: ChatOpenAI
#             on_chat_model_stream: ChatOpenAI
#             on_chat_model_stream: ChatOpenAI
#         on_chat_model_stream: ChatOpenAI
#         on_chat_model_end: ChatOpenAI
#     on_chain_stream: call_model_node # 执行期间触发on_chain_stream
#     on_chain_end: call_model_node
# on_chain_stream: LangGraph # 每次节点执行后发出on_chain_stream
# on_chain_end: LangGraph # 每次节点执行完成出发on_chain_end


asyncio.run(start())

# {'event': 'on_chain_start',
#  'run_id': '019b3ac2-6a9e-7362-9aab-d59531717c1e',
#  'name': 'LangGraph',
#  'tags': [],
#  'metadata': {},
#  'data': {'input': {'messages': [{'role': 'user', 'content': 'hello.'}]}},
#  'parent_ids': []}
# {'event': 'on_chain_start',
#  'name': 'call_model_node',
#  'run_id': '019b3ac2-6a9f-7ff2-b40f-f74e52a2aa36',
#  'tags': ['graph:step:1'],
#  'metadata': {'langgraph_step': 1,
#   'langgraph_node': 'call_model_node',
#   'langgraph_triggers': ('branch:to:call_model_node',),
#   'langgraph_path': ('__pregel_pull', 'call_model_node'),
#   'langgraph_checkpoint_ns': 'call_model_node:03032164-f5ac-7756-1085-689eba6b53cc'},
#  'data': {'input': {'messages': [HumanMessage(content='hello.', additional_kwargs={}, response_metadata={}, id='cfa4d3ef-124f-4396-9bbc-9a686f461316')]}},
#  'parent_ids': []}
# {'event': 'on_chat_model_start',
#  'name': 'ChatOpenAI',
#  'run_id': '019b3ac2-6aa0-7232-808d-788a6bb8aeb3',
#  'tags': ['seq:step:1'],
#  'metadata': {'langgraph_step': 1,
#   'langgraph_node': 'call_model_node',
#   'langgraph_triggers': ('branch:to:call_model_node',),
#   'langgraph_path': ('__pregel_pull', 'call_model_node'),
#   'langgraph_checkpoint_ns': 'call_model_node:03032164-f5ac-7756-1085-689eba6b53cc',
#   'checkpoint_ns': 'call_model_node:03032164-f5ac-7756-1085-689eba6b53cc',
#   'ls_provider': 'openai',
#   'ls_model_name': 'Qwen/Qwen2.5-7B-Instruct',
#   'ls_model_type': 'chat',
#   'ls_temperature': None},
#  'data': {'input': {'messages': [[HumanMessage(content='hello.', additional_kwargs={}, response_metadata={}, id='cfa4d3ef-124f-4396-9bbc-9a686f461316')]]}},
#  'parent_ids': []}
# {'event': 'on_chat_model_stream',
#  'name': 'ChatOpenAI',
#  'run_id': '019b3ac2-6aa0-7232-808d-788a6bb8aeb3',
#  'tags': ['seq:step:1'],
#  'metadata': {'langgraph_step': 1,
#   'langgraph_node': 'call_model_node',
#   'langgraph_triggers': ('branch:to:call_model_node',),
#   'langgraph_path': ('__pregel_pull', 'call_model_node'),
#   'langgraph_checkpoint_ns': 'call_model_node:03032164-f5ac-7756-1085-689eba6b53cc',
#   'checkpoint_ns': 'call_model_node:03032164-f5ac-7756-1085-689eba6b53cc',
#   'ls_provider': 'openai',
#   'ls_model_name': 'Qwen/Qwen2.5-7B-Instruct',
#   'ls_model_type': 'chat',
#   'ls_temperature': None},
#  'data': {'chunk': AIMessageChunk(content='', additional_kwargs={}, response_metadata={'model_provider': 'openai'}, id='lc_run--019b3ac2-6aa0-7232-808d-788a6bb8aeb3', usage_metadata={'input_tokens': 31, 'output_tokens': 0, 'total_tokens': 31, 'input_token_details': {}, 'output_token_details': {}})},
#  'parent_ids': []}
# {'event': 'on_chat_model_stream',
#  'name': 'ChatOpenAI',
#  'run_id': '019b3ac2-6aa0-7232-808d-788a6bb8aeb3',
#  'tags': ['seq:step:1'],
#  'metadata': {'langgraph_step': 1,
#   'langgraph_node': 'call_model_node',
#   'langgraph_triggers': ('branch:to:call_model_node',),
#   'langgraph_path': ('__pregel_pull', 'call_model_node'),
#   'langgraph_checkpoint_ns': 'call_model_node:03032164-f5ac-7756-1085-689eba6b53cc',
#   'checkpoint_ns': 'call_model_node:03032164-f5ac-7756-1085-689eba6b53cc',
#   'ls_provider': 'openai',
#   'ls_model_name': 'Qwen/Qwen2.5-7B-Instruct',
#   'ls_model_type': 'chat',
#   'ls_temperature': None},
#  'data': {'chunk': AIMessageChunk(content='Hello', additional_kwargs={}, response_metadata={'model_provider': 'openai'}, id='lc_run--019b3ac2-6aa0-7232-808d-788a6bb8aeb3', usage_metadata={'input_tokens': 31, 'output_tokens': 1, 'total_tokens': 32, 'input_token_details': {}, 'output_token_details': {}})},
#  'parent_ids': []}
# {'event': 'on_chat_model_stream',
#  'name': 'ChatOpenAI',
#  'run_id': '019b3ac2-6aa0-7232-808d-788a6bb8aeb3',
#  'tags': ['seq:step:1'],
#  'metadata': {'langgraph_step': 1,
#   'langgraph_node': 'call_model_node',
#   'langgraph_triggers': ('branch:to:call_model_node',),
#   'langgraph_path': ('__pregel_pull', 'call_model_node'),
#   'langgraph_checkpoint_ns': 'call_model_node:03032164-f5ac-7756-1085-689eba6b53cc',
#   'checkpoint_ns': 'call_model_node:03032164-f5ac-7756-1085-689eba6b53cc',
#   'ls_provider': 'openai',
#   'ls_model_name': 'Qwen/Qwen2.5-7B-Instruct',
#   'ls_model_type': 'chat',
#   'ls_temperature': None},
#  'data': {'chunk': AIMessageChunk(content='!', additional_kwargs={}, response_metadata={'model_provider': 'openai'}, id='lc_run--019b3ac2-6aa0-7232-808d-788a6bb8aeb3', usage_metadata={'input_tokens': 31, 'output_tokens': 2, 'total_tokens': 33, 'input_token_details': {}, 'output_token_details': {}})},
#  'parent_ids': []}
# {'event': 'on_chat_model_stream',
#  'name': 'ChatOpenAI',
#  'run_id': '019b3ac2-6aa0-7232-808d-788a6bb8aeb3',
#  'tags': ['seq:step:1'],
#  'metadata': {'langgraph_step': 1,
#   'langgraph_node': 'call_model_node',
#   'langgraph_triggers': ('branch:to:call_model_node',),
#   'langgraph_path': ('__pregel_pull', 'call_model_node'),
#   'langgraph_checkpoint_ns': 'call_model_node:03032164-f5ac-7756-1085-689eba6b53cc',
#   'checkpoint_ns': 'call_model_node:03032164-f5ac-7756-1085-689eba6b53cc',
#   'ls_provider': 'openai',
#   'ls_model_name': 'Qwen/Qwen2.5-7B-Instruct',
#   'ls_model_type': 'chat',
#   'ls_temperature': None},
#  'data': {'chunk': AIMessageChunk(content=' How', additional_kwargs={}, response_metadata={'model_provider': 'openai'}, id='lc_run--019b3ac2-6aa0-7232-808d-788a6bb8aeb3', usage_metadata={'input_tokens': 31, 'output_tokens': 3, 'total_tokens': 34, 'input_token_details': {}, 'output_token_details': {}})},
#  'parent_ids': []}
# {'event': 'on_chat_model_stream',
#  'name': 'ChatOpenAI',
#  'run_id': '019b3ac2-6aa0-7232-808d-788a6bb8aeb3',
#  'tags': ['seq:step:1'],
#  'metadata': {'langgraph_step': 1,
#   'langgraph_node': 'call_model_node',
#   'langgraph_triggers': ('branch:to:call_model_node',),
#   'langgraph_path': ('__pregel_pull', 'call_model_node'),
#   'langgraph_checkpoint_ns': 'call_model_node:03032164-f5ac-7756-1085-689eba6b53cc',
#   'checkpoint_ns': 'call_model_node:03032164-f5ac-7756-1085-689eba6b53cc',
#   'ls_provider': 'openai',
#   'ls_model_name': 'Qwen/Qwen2.5-7B-Instruct',
#   'ls_model_type': 'chat',
#   'ls_temperature': None},
#  'data': {'chunk': AIMessageChunk(content=' can', additional_kwargs={}, response_metadata={'model_provider': 'openai'}, id='lc_run--019b3ac2-6aa0-7232-808d-788a6bb8aeb3', usage_metadata={'input_tokens': 31, 'output_tokens': 4, 'total_tokens': 35, 'input_token_details': {}, 'output_token_details': {}})},
#  'parent_ids': []}
# {'event': 'on_chat_model_stream',
#  'name': 'ChatOpenAI',
#  'run_id': '019b3ac2-6aa0-7232-808d-788a6bb8aeb3',
#  'tags': ['seq:step:1'],
#  'metadata': {'langgraph_step': 1,
#   'langgraph_node': 'call_model_node',
#   'langgraph_triggers': ('branch:to:call_model_node',),
#   'langgraph_path': ('__pregel_pull', 'call_model_node'),
#   'langgraph_checkpoint_ns': 'call_model_node:03032164-f5ac-7756-1085-689eba6b53cc',
#   'checkpoint_ns': 'call_model_node:03032164-f5ac-7756-1085-689eba6b53cc',
#   'ls_provider': 'openai',
#   'ls_model_name': 'Qwen/Qwen2.5-7B-Instruct',
#   'ls_model_type': 'chat',
#   'ls_temperature': None},
#  'data': {'chunk': AIMessageChunk(content=' I', additional_kwargs={}, response_metadata={'model_provider': 'openai'}, id='lc_run--019b3ac2-6aa0-7232-808d-788a6bb8aeb3', usage_metadata={'input_tokens': 31, 'output_tokens': 5, 'total_tokens': 36, 'input_token_details': {}, 'output_token_details': {}})},
#  'parent_ids': []}
# {'event': 'on_chat_model_stream',
#  'name': 'ChatOpenAI',
#  'run_id': '019b3ac2-6aa0-7232-808d-788a6bb8aeb3',
#  'tags': ['seq:step:1'],
#  'metadata': {'langgraph_step': 1,
#   'langgraph_node': 'call_model_node',
#   'langgraph_triggers': ('branch:to:call_model_node',),
#   'langgraph_path': ('__pregel_pull', 'call_model_node'),
#   'langgraph_checkpoint_ns': 'call_model_node:03032164-f5ac-7756-1085-689eba6b53cc',
#   'checkpoint_ns': 'call_model_node:03032164-f5ac-7756-1085-689eba6b53cc',
#   'ls_provider': 'openai',
#   'ls_model_name': 'Qwen/Qwen2.5-7B-Instruct',
#   'ls_model_type': 'chat',
#   'ls_temperature': None},
#  'data': {'chunk': AIMessageChunk(content=' assist', additional_kwargs={}, response_metadata={'model_provider': 'openai'}, id='lc_run--019b3ac2-6aa0-7232-808d-788a6bb8aeb3', usage_metadata={'input_tokens': 31, 'output_tokens': 6, 'total_tokens': 37, 'input_token_details': {}, 'output_token_details': {}})},
#  'parent_ids': []}
# {'event': 'on_chat_model_stream',
#  'name': 'ChatOpenAI',
#  'run_id': '019b3ac2-6aa0-7232-808d-788a6bb8aeb3',
#  'tags': ['seq:step:1'],
#  'metadata': {'langgraph_step': 1,
#   'langgraph_node': 'call_model_node',
#   'langgraph_triggers': ('branch:to:call_model_node',),
#   'langgraph_path': ('__pregel_pull', 'call_model_node'),
#   'langgraph_checkpoint_ns': 'call_model_node:03032164-f5ac-7756-1085-689eba6b53cc',
#   'checkpoint_ns': 'call_model_node:03032164-f5ac-7756-1085-689eba6b53cc',
#   'ls_provider': 'openai',
#   'ls_model_name': 'Qwen/Qwen2.5-7B-Instruct',
#   'ls_model_type': 'chat',
#   'ls_temperature': None},
#  'data': {'chunk': AIMessageChunk(content=' you', additional_kwargs={}, response_metadata={'model_provider': 'openai'}, id='lc_run--019b3ac2-6aa0-7232-808d-788a6bb8aeb3', usage_metadata={'input_tokens': 31, 'output_tokens': 7, 'total_tokens': 38, 'input_token_details': {}, 'output_token_details': {}})},
#  'parent_ids': []}
# {'event': 'on_chat_model_stream',
#  'name': 'ChatOpenAI',
#  'run_id': '019b3ac2-6aa0-7232-808d-788a6bb8aeb3',
#  'tags': ['seq:step:1'],
#  'metadata': {'langgraph_step': 1,
#   'langgraph_node': 'call_model_node',
#   'langgraph_triggers': ('branch:to:call_model_node',),
#   'langgraph_path': ('__pregel_pull', 'call_model_node'),
#   'langgraph_checkpoint_ns': 'call_model_node:03032164-f5ac-7756-1085-689eba6b53cc',
#   'checkpoint_ns': 'call_model_node:03032164-f5ac-7756-1085-689eba6b53cc',
#   'ls_provider': 'openai',
#   'ls_model_name': 'Qwen/Qwen2.5-7B-Instruct',
#   'ls_model_type': 'chat',
#   'ls_temperature': None},
#  'data': {'chunk': AIMessageChunk(content=' today', additional_kwargs={}, response_metadata={'model_provider': 'openai'}, id='lc_run--019b3ac2-6aa0-7232-808d-788a6bb8aeb3', usage_metadata={'input_tokens': 31, 'output_tokens': 8, 'total_tokens': 39, 'input_token_details': {}, 'output_token_details': {}})},
#  'parent_ids': []}
# {'event': 'on_chat_model_stream',
#  'name': 'ChatOpenAI',
#  'run_id': '019b3ac2-6aa0-7232-808d-788a6bb8aeb3',
#  'tags': ['seq:step:1'],
#  'metadata': {'langgraph_step': 1,
#   'langgraph_node': 'call_model_node',
#   'langgraph_triggers': ('branch:to:call_model_node',),
#   'langgraph_path': ('__pregel_pull', 'call_model_node'),
#   'langgraph_checkpoint_ns': 'call_model_node:03032164-f5ac-7756-1085-689eba6b53cc',
#   'checkpoint_ns': 'call_model_node:03032164-f5ac-7756-1085-689eba6b53cc',
#   'ls_provider': 'openai',
#   'ls_model_name': 'Qwen/Qwen2.5-7B-Instruct',
#   'ls_model_type': 'chat',
#   'ls_temperature': None},
#  'data': {'chunk': AIMessageChunk(content='?', additional_kwargs={}, response_metadata={'model_provider': 'openai'}, id='lc_run--019b3ac2-6aa0-7232-808d-788a6bb8aeb3', usage_metadata={'input_tokens': 31, 'output_tokens': 9, 'total_tokens': 40, 'input_token_details': {}, 'output_token_details': {}})},
#  'parent_ids': []}
# {'event': 'on_chat_model_stream',
#  'name': 'ChatOpenAI',
#  'run_id': '019b3ac2-6aa0-7232-808d-788a6bb8aeb3',
#  'tags': ['seq:step:1'],
#  'metadata': {'langgraph_step': 1,
#   'langgraph_node': 'call_model_node',
#   'langgraph_triggers': ('branch:to:call_model_node',),
#   'langgraph_path': ('__pregel_pull', 'call_model_node'),
#   'langgraph_checkpoint_ns': 'call_model_node:03032164-f5ac-7756-1085-689eba6b53cc',
#   'checkpoint_ns': 'call_model_node:03032164-f5ac-7756-1085-689eba6b53cc',
#   'ls_provider': 'openai',
#   'ls_model_name': 'Qwen/Qwen2.5-7B-Instruct',
#   'ls_model_type': 'chat',
#   'ls_temperature': None},
#  'data': {'chunk': AIMessageChunk(content='', additional_kwargs={}, response_metadata={'finish_reason': 'stop', 'model_name': 'Qwen/Qwen2.5-7B-Instruct', 'model_provider': 'openai'}, id='lc_run--019b3ac2-6aa0-7232-808d-788a6bb8aeb3', usage_metadata={'input_tokens': 31, 'output_tokens': 9, 'total_tokens': 40, 'input_token_details': {}, 'output_token_details': {}}, chunk_position='last')},
#  'parent_ids': []}
# {'event': 'on_chat_model_end',
#  'name': 'ChatOpenAI',
#  'run_id': '019b3ac2-6aa0-7232-808d-788a6bb8aeb3',
#  'tags': ['seq:step:1'],
#  'metadata': {'langgraph_step': 1,
#   'langgraph_node': 'call_model_node',
#   'langgraph_triggers': ('branch:to:call_model_node',),
#   'langgraph_path': ('__pregel_pull', 'call_model_node'),
#   'langgraph_checkpoint_ns': 'call_model_node:03032164-f5ac-7756-1085-689eba6b53cc',
#   'checkpoint_ns': 'call_model_node:03032164-f5ac-7756-1085-689eba6b53cc',
#   'ls_provider': 'openai',
#   'ls_model_name': 'Qwen/Qwen2.5-7B-Instruct',
#   'ls_model_type': 'chat',
#   'ls_temperature': None},
#  'data': {'input': {'messages': [[HumanMessage(content='hello.', additional_kwargs={}, response_metadata={}, id='cfa4d3ef-124f-4396-9bbc-9a686f461316')]]},
#   'output': {'generations': [[{'text': 'Hello! How can I assist you today?',
#       'generation_info': {'finish_reason': 'stop',
#        'model_name': 'Qwen/Qwen2.5-7B-Instruct'},
#       'type': 'ChatGeneration',
#       'message': AIMessage(content='Hello! How can I assist you today?', additional_kwargs={}, response_metadata={'finish_reason': 'stop', 'model_name': 'Qwen/Qwen2.5-7B-Instruct', 'model_provider': 'openai'}, id='lc_run--019b3ac2-6aa0-7232-808d-788a6bb8aeb3', usage_metadata={'input_tokens': 341, 'output_tokens': 54, 'total_tokens': 395, 'input_token_details': {}, 'output_token_details': {}})}]],
#    'llm_output': None,
#    'run': None,
#    'type': 'LLMResult'}},
#  'parent_ids': []}
# {'event': 'on_chain_stream',
#  'name': 'call_model_node',
#  'run_id': '019b3ac2-6a9f-7ff2-b40f-f74e52a2aa36',
#  'tags': ['graph:step:1'],
#  'metadata': {'langgraph_step': 1,
#   'langgraph_node': 'call_model_node',
#   'langgraph_triggers': ('branch:to:call_model_node',),
#   'langgraph_path': ('__pregel_pull', 'call_model_node'),
#   'langgraph_checkpoint_ns': 'call_model_node:03032164-f5ac-7756-1085-689eba6b53cc'},
#  'data': {'chunk': {'messages': AIMessage(content='Hello! How can I assist you today?', additional_kwargs={}, response_metadata={'finish_reason': 'stop', 'model_name': 'Qwen/Qwen2.5-7B-Instruct', 'model_provider': 'openai'}, id='lc_run--019b3ac2-6aa0-7232-808d-788a6bb8aeb3', usage_metadata={'input_tokens': 341, 'output_tokens': 54, 'total_tokens': 395, 'input_token_details': {}, 'output_token_details': {}})}},
#  'parent_ids': []}
# {'event': 'on_chain_end',
#  'name': 'call_model_node',
#  'run_id': '019b3ac2-6a9f-7ff2-b40f-f74e52a2aa36',
#  'tags': ['graph:step:1'],
#  'metadata': {'langgraph_step': 1,
#   'langgraph_node': 'call_model_node',
#   'langgraph_triggers': ('branch:to:call_model_node',),
#   'langgraph_path': ('__pregel_pull', 'call_model_node'),
#   'langgraph_checkpoint_ns': 'call_model_node:03032164-f5ac-7756-1085-689eba6b53cc'},
#  'data': {'input': {'messages': [HumanMessage(content='hello.', additional_kwargs={}, response_metadata={}, id='cfa4d3ef-124f-4396-9bbc-9a686f461316')]},
#   'output': {'messages': AIMessage(content='Hello! How can I assist you today?', additional_kwargs={}, response_metadata={'finish_reason': 'stop', 'model_name': 'Qwen/Qwen2.5-7B-Instruct', 'model_provider': 'openai'}, id='lc_run--019b3ac2-6aa0-7232-808d-788a6bb8aeb3', usage_metadata={'input_tokens': 341, 'output_tokens': 54, 'total_tokens': 395, 'input_token_details': {}, 'output_token_details': {}})}},
#  'parent_ids': []}
# {'event': 'on_chain_stream',
#  'run_id': '019b3ac2-6a9e-7362-9aab-d59531717c1e',
#  'tags': [],
#  'metadata': {},
#  'name': 'LangGraph',
#  'data': {'chunk': {'call_model_node': {'messages': AIMessage(content='Hello! How can I assist you today?', additional_kwargs={}, response_metadata={'finish_reason': 'stop', 'model_name': 'Qwen/Qwen2.5-7B-Instruct', 'model_provider': 'openai'}, id='lc_run--019b3ac2-6aa0-7232-808d-788a6bb8aeb3', usage_metadata={'input_tokens': 341, 'output_tokens': 54, 'total_tokens': 395, 'input_token_details': {}, 'output_token_details': {}})}}},
#  'parent_ids': []}
# {'event': 'on_chain_end',
#  'name': 'LangGraph',
#  'run_id': '019b3ac2-6a9e-7362-9aab-d59531717c1e',
#  'tags': [],
#  'metadata': {},
#  'data': {'output': {'call_model_node': {'messages': AIMessage(content='Hello! How can I assist you today?', additional_kwargs={}, response_metadata={'finish_reason': 'stop', 'model_name': 'Qwen/Qwen2.5-7B-Instruct', 'model_provider': 'openai'}, id='lc_run--019b3ac2-6aa0-7232-808d-788a6bb8aeb3', usage_metadata={'input_tokens': 341, 'output_tokens': 54, 'total_tokens': 395, 'input_token_details': {}, 'output_token_details': {}})}}},
#  'parent_ids': []}
