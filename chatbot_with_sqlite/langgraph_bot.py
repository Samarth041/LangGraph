from typing import TypedDict, Annotated
from langchain_core.messages import BaseMessage
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
import sqlite3
from langgraph.checkpoint.sqlite import SqliteSaver

from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint


from dotenv import load_dotenv
load_dotenv()

import os

hf_token=os.getenv("HF_TOKEN")


llm=HuggingFaceEndpoint(
    repo_id="Qwen/Qwen2.5-7B-Instruct",
    task="conversational",
    huggingfacehub_api_token=hf_token,
    max_new_tokens=200,
    temperature=0.7,
    streaming=True
    
)

llm = ChatHuggingFace(llm=llm)

class State(TypedDict):
    messages: Annotated[list, add_messages]


def chatbot(state:State):
    #convert LangGraph messages-> plain prompt
    response=llm.invoke(state['messages'])
    return {"messages":[response]}

graph=StateGraph(State)

graph.add_node("chatbot",chatbot)


graph.add_edge(START,"chatbot")
graph.add_edge("chatbot", END)


conn = sqlite3.connect(
    "chat_memory.db",
    check_same_thread=False
)

memory = SqliteSaver(conn)

# -----------------------------------
# Compile Graph

app = graph.compile(
    checkpointer=memory
)
