#1.
# define tools and models

from langchain.tools import tool
from langchain.chat_models import init_chat_model
from dotenv import load_dotenv
load_dotenv()

from langchain_google_genai import ChatGoogleGenerativeAI

model = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0.1
)
# define tools

@tool
def multiply(a:int,b:int)->int:
    """
    Multiply `a` and `b`

    Args:
        a:First int
        b:Second int
    """
    return a*b

@tool
def add(a:int, b:int)->int:
    """
    Add `a` and`b`
    Args:
        a:irst int
        b:Second int
    """
    return a+b

@tool
def divide(a:int,b:int)->int:
    """
    Divide `a` and `b`
    
    Args:
        a:First int
        b:Second int
    """
    return a/b


#Augment the LLM with tools
tools=[add,multiply,divide]

tools_by_name={tool.name : tool for tool in tools}
model_with_tools=model.bind_tools(tools)
#-------------------------------------------------------------------------------

from langgraph.graph import add_messages
from langchain_core.messages import (
    SystemMessage,
    HumanMessage,
    BaseMessage
)

from langchain_core.messages.tool import ToolCall
from langchain_core.messages import BaseMessage

from langgraph.func import entrypoint,task

#2.define model node

# the model node is used to call the LLm and decide whether to call a tool or not

@task
def call_llm(messages:list[BaseMessage]):
    """LLM decides whether to call a tool or not"""
    return model_with_tools.invoke(
        [
            SystemMessage(content="You are a helpful assistant tasked with performing arthmetic on inputs")
        ]
        +messages
    )

#-------------------------------------------------
#3.define tool model
#--> it is used to call the tools and return the results
@task
def call_tool(tool_call:ToolCall): #tool_call from llm
    """Perform the tool call"""
    tool=tools_by_name[tool_call["name"]]
    return tool.invoke(tool_call)

#---------------------------------------------------------

# 4. Define agent-the agent is built using @entrypoint function

#In the Functional API, instead of defining nodes and edges explicitly, you write standard control flow logic (loops, conditionals) within a single function.

@entrypoint()
def agent(messages:list[BaseMessage]):
    model_response=call_llm(messages).result()

    while True:
        if not model_response.tool_calls:
            break

        #execute tools
        tool_result_features=[
            call_tool(tool_call) for tool_call in model_response.tool_calls 
        ]
        tool_results=[fut.result() for fut in tool_result_features]
        messages = add_messages(messages, [model_response, *tool_results])
        model_response=call_llm(messages).result()

    messages=add_messages(messages,[model_response])
    return messages

#invoke

messages=[HumanMessage(content="Add 3 and 4.")]
stream = agent.stream_events(messages, version="v3")

for i, snapshot in enumerate(stream.values):
    print(f"\n========== SNAPSHOT {i} ==========")

    for msg in snapshot:
        print(f"\n--- {type(msg).__name__} ---")
        if hasattr(msg, "content"):
            print(msg.content)
        else:
            print(msg)