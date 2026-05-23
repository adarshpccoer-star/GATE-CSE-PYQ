from langgraph.graph import START, END, StateGraph
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from typing import Literal, TypedDict
from pydantic import Field, BaseModel
from dotenv import load_dotenv

load_dotenv()


# ---------------- STATE ---------------- #

class State(TypedDict):
    input: str
    decision: str
    output: str


# ---------------- ROUTER OUTPUT ---------------- #

class RouterOutput(BaseModel):
    step: Literal["poem", "story", "joke"] = Field(
        description="The next step in routing"
    )


# ---------------- MODEL ---------------- #

model = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0.7
)

router_model = model.with_structured_output(RouterOutput)


# ---------------- NODES ---------------- #

def joke_node(state: State):
    msg = model.invoke(
        f"Write a short joke about {state['input']}"
    )
    return {"output": msg.content}


def story_node(state: State):
    msg = model.invoke(
        f"Write a short story in 60 words on topic: {state['input']}"
    )
    return {"output": msg.content}


def poem_node(state: State):
    msg = model.invoke(
        f"Write a 4-line poem on topic: {state['input']}"
    )
    return {"output": msg.content}


# ---------------- ROUTER NODE ---------------- #

def decision_topic(state: State):

    decision = router_model.invoke([
        SystemMessage(
            content="Route the input to story, joke, or poem based on the user's request."
        ),
        HumanMessage(content=state["input"]),
    ])

    return {"decision": decision.step}


# ---------------- CONDITIONAL ROUTER ---------------- #

def router_decision(state: State):

    if state["decision"] == "story":
        return "story_node"

    elif state["decision"] == "joke":
        return "joke_node"

    else:
        return "poem_node"


# ---------------- BUILD GRAPH ---------------- #

router_builder = StateGraph(State)

router_builder.add_node("decision_topic", decision_topic)
router_builder.add_node("poem_node", poem_node)
router_builder.add_node("story_node", story_node)
router_builder.add_node("joke_node", joke_node)

router_builder.add_edge(START, "decision_topic")

router_builder.add_conditional_edges(
    "decision_topic",
    router_decision,
    {
        "poem_node": "poem_node",
        "story_node": "story_node",
        "joke_node": "joke_node",
    }
)

router_builder.add_edge("poem_node", END)
router_builder.add_edge("story_node", END)
router_builder.add_edge("joke_node", END)

# ---------------- COMPILE ---------------- #

router_workflow = router_builder.compile()

# ---------------- RUN ---------------- #

state = router_workflow.invoke(
    {"input": "Write me a joke about cats"}
)

print(state["output"])