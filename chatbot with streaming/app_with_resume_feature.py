import streamlit as st
import uuid
from langchain_core.messages import HumanMessage
from langgraph_bot import app

# -------------------------
# PAGE CONFIG

st.set_page_config(
    page_title="Qwen Streaming Chatbot",
    page_icon="🤖",
    layout="centered"
)

st.title("🤖 Qwen Streaming Chatbot")
st.caption("LangGraph + Qwen + Streaming + Streamlit")


#-------------------------
#init

if "chats" not in st.session_state:
    st.session_state["chats"] = {}

if "active_chat" not in st.session_state:
    st.session_state["active_chat"] = str(uuid.uuid4())

#create first chat automatically

if st.session_state["active_chat"] not in st.session_state["chats"]:
    st.session_state["chats"][st.session_state["active_chat"]]=[]


config={
    
    "configurable": {
        "thread_id": st.session_state["active_chat"]
    }
}

#-------------------------
#side bar

with st.sidebar:
    st.header("Chats 💬")

    #new chat button
    if st.button("New Chat"):
        new_id=str(uuid.uuid4())
        st.session_state["active_chat"]=new_id
        st.session_state["chats"][new_id]=[]
        st.rerun()

    st.divider()

    #show all chats
    for chat_id in st.session_state["chats"].keys():
        if st.button(f"Chat {chat_id[:8]}"):
            st.session_state["active_chat"]=chat_id
            st.rerun()


#-------------------------
#currrent chat history

messages=st.session_state["chats"][st.session_state["active_chat"]]

for msg in messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])


#------------------------------
#Input

prompt=st.chat_input("Type your message")

if prompt:

    messages.append({"role":"user","content":prompt})
    st.chat_message("user").markdown(prompt)

    with st.chat_message("assistant"):
        placeholder=st.empty()
        full_response=""

        for chunk in app.stream(
            {"messages":[HumanMessage(content=prompt)]},
            config=config,
            stream_mode=["messages"],
            version='v2'
        ):
            if chunk.get("type")!= "messages":
                continue

            msg_chunk,metadata=chunk["data"]

            content=getattr(msg_chunk,"content","")

            if content:
                full_response+=content
                placeholder.markdown(full_response + " 🚓")

        placeholder.markdown(full_response)

    messages.append({"role":"assistant","content":full_response})