# %%
import operator
from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END


class State(TypedDict):
    aggregate: Annotated[list, operator.add]


def a(state: State):
    print(f"adding a to {state['aggregate']}")
    return {"aggregate": ["A"]}


def b(state: State):
    print(f"adding b to {state['aggregate']}")
    return {"aggregate": ["B"]}


def c(state: State):
    print(f"adding c to {state['aggregate']}")
    return {"aggregate": ["C"]}


def d(state: State):
    print(f"adding d to {state['aggregate']}")
    return {"aggregate": ["D"]}


builder = StateGraph(State)
builder.add_node(a)
builder.add_node(b)
builder.add_node(c)
builder.add_node(d)

builder.add_edge(START, "a")
builder.add_edge("a", "b")
builder.add_edge("a", "c")
builder.add_edge("b", "d")
builder.add_edge("c", "d")
builder.add_edge("d", END)
graph = builder.compile()

graph.invoke({"aggregate": []}, {"configurable": {"thread_id": "foo"}})

# adding a to []
# adding b to ['A']
# adding c to ['A']
# adding d to ['A', 'B', 'b', 'C']
# {'aggregate': ['A', 'B', 'b', 'C', 'D']}


# %%
def b2(state: State):
    print(f"adding b2 to {state['aggregate']}")
    return {"aggregate": ["b2"]}


builder = StateGraph(State)
builder.add_node(a)
builder.add_node(b)
builder.add_node(b2)
builder.add_node(c)
builder.add_node(d)

builder.add_edge(START, "a")
builder.add_edge("a", "b")
builder.add_edge("a", "c")
builder.add_edge("b", "b2")
# builder.add_edge(["c", "b2"], "d")
builder.add_edge(["b2", "c"], "d")
builder.add_edge("d", END)
graph = builder.compile()

graph.invoke({"aggregate": []}, {"configurable": {"thread_id": "foo"}})

# adding a to []
# adding b to ['A']
# adding c to ['A']
# adding d to ['A', 'B', 'C', 'b2']

# %%
