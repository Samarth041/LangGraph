import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage


#import compiled langgraph app
from langgraph_bot import app

#page configuration
st.set_page_config(
    page_title="Qwen Chatbot",
    page_icon="🤖",
    layout="centered"
)

st.title("Qwen Chatbot")

st.caption("This chatbot is built with LangGraph + Qwen + Streamlit")

#initialise UI chat history

if "messages" not in st.session_state:
    st.session_state.messages=[]

#create a persistent thread id

if "thread_id" not in st.session_state:
    st.session_state.thread_id = "streamlit_chat"

config={
    "configurable": {"thread_id": st.session_state.thread_id}
}

#display previous chat messages


for message in st.session_state.messages:

    with st.chat_message(message["role"]):
        st.markdown(message["content"])

#user input

prompt = st.chat_input("Type your message here...")

if prompt:

    #display user message
    with st.chat_message("user"):
        st.markdown(prompt)

    st.session_state.messages.append({"role": "user", "content": prompt})

    #call Langgraph

    with st.chat_message("assistant"):
        with st.spinner("thinking..."):
            result=app.invoke(
                {
                    "messages":[HumanMessage(content=prompt)]
                },
                config=config
            )

            response=result["messages"][-1].content

            st.markdown(response)

    #save assistant response

    st.session_state.messages.append(
        {"role": "assistant", "content": response}
    )

#sidebar
with st.sidebar:
    st.header("Options")

    if st.button("Clear Chat 🗑️"):
        st.session_state.messages=[]


        #start a fresh conversation

        import uuid

        st.session_state.thread_id=str(uuid.uuid4())
        st.rerun()

    st.divider()

    st.write("Current Thread ID : ")

    st.code(st.session_state.thread_id)