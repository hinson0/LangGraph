from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_openai import ChatOpenAI
from typing_extensions import TypedDict, Annotated
import asyncio


class State(TypedDict):
    messages: Annotated[list, add_messages]


# Simple agent graph
llm = ChatOpenAI(model="gpt-4o-mini", streaming=True)


def agent_node(state: State):
    return {"messages": [llm.invoke(state["messages"])]}


graph = (
    StateGraph(State)
    .add_node("agent", agent_node)
    .add_edge(START, "agent")
    .add_edge("agent", END)
    .compile()
)


async def stream_events():
    config = {"configurable": {"thread_id": "1"}}
    input_message = {"messages": [{"role": "user", "content": "What's 2+2?"}]}

    # Stream ALL events (LCEL-style)
    async for event in graph.astream_events(input_message, config, version="v1"):
        print(f"Event: {event['event']}")
        print(f"  Name: {event['name']}")
        print(f"  Run ID: {event['run_id'][:8]}...")

        if event["event"] == "on_chat_model_stream":
            print(f"  Token: {event['data']['chunk'].content}")
        elif event["event"] == "on_chain_end":
            print(f"  Final output: {event['data']['output']}")
        print("---")


# Run it
asyncio.run(stream_events())
