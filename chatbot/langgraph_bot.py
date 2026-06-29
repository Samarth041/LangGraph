from dotenv import load_dotenv
load_dotenv()

import os

hf_token=os.getenv("HF_TOKEN")

from typing import TypedDict, Annotated

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import InMemorySaver

from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint


class State(TypedDict):
    messages: Annotated[list, add_messages]

llm=HuggingFaceEndpoint(
    repo_id="Qwen/Qwen2.5-7B-Instruct",
    task="conversational",
    huggingfacehub_api_token=hf_token,
    max_new_tokens=200,
    temperature=0.7
)

llm = ChatHuggingFace(llm=llm)

def chatbot(state:State):
    #convert LangGraph messages-> plain prompt
    response=llm.invoke(state['messages'])
    return {"messages":[response]}

graph=StateGraph(State)

graph.add_node("chatbot",chatbot)


graph.add_edge(START,"chatbot")


memory = InMemorySaver()


# -----------------------------------
# Compile Graph
# -----------------------------------
app = graph.compile(
    checkpointer=memory
)