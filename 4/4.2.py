# %%  4-10 在config中传递thread_id

config = {"configurale": {"thread_id": "user_conversation_123"}}

# %% 4-11 使用MemorySaver编译具有持久化的LangGraph

from langgraph.checkpoint.memory import MemorySaver

checkpointer = MemorySaver()
agent = graph.compile(checkpointer)

# %% 4-12 使用SqliteSaver编译具有持久化的LangGraph
# pip install langgraph-checkpoint-sqlite
import sqlite3
from langgraph.checkpoint.sqlite import SqliteSaver

conn = sqlite3.connect("checkpoints.sqlite")
checkpointer = SqliteSaver(conn)


# %% 使用PostgresSave编译具有持久化的LangGraph
# pip install langgraph-checkpoint-postgres psycopg psycopg-pool
from langgraph.checkpoint.postgres import PostgresSaver

db_uri = "postgresql://postgres:postgres@localhost:5442/postgres?sslmode=disable"
with PostgresSaver.from_conn_string(db_uri) as checkpointer:
    checkpointer.setup()
    config = {"configurable": {"thread_id"}}
    agent = graph.compile(checkpointer, config)

# %% 使用MongoDBSaver编译具有持久化的LangGraph
# pip install langgraph-checkpoint-mongodb pymongo
from langgraph.checkpoint.mongodb import MongoDBSaver

db_uri = "mongodb://localhost:27017/"
with MongoDBSaver.from_conn_string(db_uri) as checkpointer:
    agent = graph.compile(checkpointer)


# %%
print(1)

# %%
