from ast import If
from langgraph.graph import MessagesState
from langchain_core.messages import RemoveMessage


def should_remove_message(message):
    raise NotImplementedError


def filter_message_node(state: MessagesState):
    message_history = state["messages"]
    messages_to_remove = []
    for message in message_history:
        if should_remove_message(message):
            messages_to_remove.append(RemoveMessage(id=message.id))
    return {"messages": message_history}
