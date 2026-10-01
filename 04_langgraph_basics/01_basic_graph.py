from typing import TypedDict
from langgraph.graph import StateGraph, START, END


class State(TypedDict):
    total: int
    status: str
    data_gathered: bool


def evaluate_node(state: State):
    print("Inside evaluate_node")

    if state["total"] >= 20000:
        return {
            "status": "ready"
        }

    if state["data_gathered"]:
        return {
            "status": "ready"
        }

    return {
        "status": "needs_more_data"
    }


def ready_node(state: State):
    print("Inside ready_node")

    return {
        "status": "ready"
    }


def needs_more_data_node(state: State):
    print("Inside needs_more_data_node")

    return {
        "status": "needs_more_data"
    }

def gather_data_node(state: State):
    print("Inside gather_data_node")

    return {
        "data_gathered": True
    }

def decide_next_node(state: State):
    print("Inside decide_next_node")

    if state["status"] == "ready":
        return "ready"

    return "needs_more_data"


graph_builder = StateGraph(State)


graph_builder.add_node("evaluate", evaluate_node)
graph_builder.add_node("ready", ready_node)
graph_builder.add_node("needs_more_data", needs_more_data_node)
graph_builder.add_node("gather_data", gather_data_node)


graph_builder.add_edge(START, "evaluate")


graph_builder.add_conditional_edges(
    "evaluate",
    decide_next_node,
    {
        "ready": "ready",
        "needs_more_data": "gather_data"
    }
)


graph_builder.add_edge("ready", END)
graph_builder.add_edge("needs_more_data", END)
graph_builder.add_edge("gather_data", "evaluate")

graph = graph_builder.compile()


result = graph.invoke({
    "total": 3000,
    "status": "",
    "data_gathered": False
})


print(result)