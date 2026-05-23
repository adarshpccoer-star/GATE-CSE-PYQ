from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

class State(TypedDict):
    topic: str
    joke: str
    improved_joke: str
    final_joke: str

model = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0.7
)

def generate_joke(state: State):
    msg = model.invoke(
        f"Write a short joke about {state['topic']}"
    )
    return {"joke": msg.content}


def check_punchline(state: State):
    if "?" in state["joke"] or "!" in state["joke"]:
        return "Pass"
    return "Fail"


def improve_joke(state: State):
    msg = model.invoke(
        f"Make this joke funnier: {state['joke']}"
    )
    return {"improved_joke": msg.content}


def polish_joke(state: State):
    msg = model.invoke(
        f"Polish this joke: {state['improved_joke']}"
    )
    return {"final_joke": msg.content}


workflow = StateGraph(State)

workflow.add_node("generate_joke", generate_joke)
workflow.add_node("improve_joke", improve_joke)
workflow.add_node("polish_joke", polish_joke)

workflow.add_edge(START, "generate_joke")

workflow.add_conditional_edges(
    "generate_joke",
    check_punchline,
    {
        "Fail": "improve_joke",
        "Pass": END
    }
)

workflow.add_edge("improve_joke", "polish_joke")
workflow.add_edge("polish_joke", END)

graph = workflow.compile()

chat = graph.invoke({
    "topic": "layoff in tech due to ai"
})

print(chat)