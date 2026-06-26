# define tools and model

from dotenv import load_dotenv
load_dotenv()

from langchain.tools import tool
from langchain.chat_models import init_chat_model
from langchain_google_genai import ChatGoogleGenerativeAI

model = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0.1
)

#define tools

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
        a:First int
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


#augment the LLM With tools
tools=[add,multiply,divide]
tools_by_name={tool.name:tool for tool in tools}
model_with_tools=model.bind_tools(tools)

#------------------------------------------------------------------------

# 2. Define State-the graph state is used to store the messages and numbr of LLm calls

from langchain.messages import AnyMessage, SystemMessage
from typing_extensions import Annotated,TypedDict
import operator

class MessagesState(TypedDict):
    messages:Annotated[list[AnyMessage],operator.add] #Tell LangGraph that messages is a list of chat messages and that new messages should be appended to the existing list instead of replacing it.
    llm_calls:int

#------------------------------------------------------------------------

# 3. Define model node
#the model node is used to call the LLM and deciede whether to call a tool or not



def llm_call(state:dict):
    """LLM decides whether to call a tool or not"""
    return {
        "messages":[
            model_with_tools.invoke(
                [
                    SystemMessage(
                        content="You are a helpful assistants tasked with performing arthmetic on inputs"
                    )
                ]
                +state["messages"]
            )
        ],
        "llm_calls":state.get('llm_calls',0)+1 #dict.get(key, default)
    }

#--------------------------------------------------------------------------------------

# 4.define tool node

#the tool node is used to call the tools and return the result

from langchain.messages import ToolMessage

def tool_call(state:dict):
    """Perform the tool call"""
    result=[]
    for tool_call in state["messages"][-1].tool_calls:
        tool=tools_by_name[tool_call["name"]]
        observation=tool.invoke(tool_call["args"])
        result.append(ToolMessage(content=observation,tool_call_id=tool_call['id']))

    return {"messages":result}
    
#--------------------------------------------------------------------------------------

# 5. Define end logic:- the conditional edge function is used to route to the tool node or end based upon wheter the llm called tool or not

from typing import Literal
from langgraph.graph import MessagesState, StateGraph, START, END

def should_continue(state:MessagesState)->Literal["tool_node",END]:
    """Decide if we should continue the loop or stope based upon whether the LLM made a tool call"""

    messages=state['messages']
    last_message=messages[-1]

    #if the LLM makes a tool call, then perform an action
    if last_message.tool_calls:
        return "tool_node"
    #otherwise, we stop(reply to the user)
    return END

#--------------------------------------------------------------------------------------

# 6. Build and compile the agent

agent_builder=StateGraph(MessagesState)

# add nodes

agent_builder.add_node("llm_call",llm_call) #name of node "llm_call" and whenever this node is executed , run the Python function llm_call
agent_builder.add_node("tool_node",tool_call)

#add edges to coonect nodes

agent_builder.add_edge(START,"llm_call")
agent_builder.add_conditional_edges("llm_call",should_continue,["tool_node",END])

agent_builder.add_edge("tool_node","llm_call")

#compile the agent
agent=agent_builder.compile()

#show the agent

#from IPython.display import Image,display
#display(Image(agent.get_graph(xray=True).draw_mermaid_png()))

#invoke

from langchain.messages import HumanMessage

messages=[HumanMessage(content="Add 3 and 4")]
messages=agent.invoke({"messages":messages})

for m in messages["messages"]:
    m.pretty_print()


