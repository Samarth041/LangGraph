import streamlit as st
import uuid

from langchain_core.messages import HumanMessage
from langgraph_bot import app


# -------------------------
# PAGE CONFIG
# -------------------------
st.set_page_config(
    page_title="Qwen Streaming Chatbot",
    page_icon="🤖",
    layout="centered"
)

st.title("🤖 Qwen Streaming Chatbot")
st.caption("LangGraph + Qwen + Streaming + Streamlit")


# -------------------------
# SESSION STATE
# -------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())


config = {
    "configurable": {
        "thread_id": st.session_state.thread_id
    }
}


# -------------------------
# SHOW CHAT HISTORY
# -------------------------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])


# -------------------------
# USER INPUT
# -------------------------
prompt = st.chat_input("Type your message...")

if prompt:

    # show user message
    st.chat_message("user").markdown(prompt)

    st.session_state.messages.append({
        "role": "user",
        "content": prompt
    })

    # assistant response container
    with st.chat_message("assistant"):
        placeholder = st.empty()
        full_response = ""

        # -------------------------
        # STREAMING CALL
        # -------------------------
        for chunk in app.stream(
            {
                "messages": [
                    HumanMessage(content=prompt)
                ]
            },
            config=config,
            stream_mode=["messages"],
            version="v2"
        ):

            # 🔥 SAFE CHECK (IMPORTANT)
            if chunk.get("type") != "messages":
                continue

            # extract message + metadata
            msg_chunk, metadata = chunk["data"]

            # get text safely
            content = getattr(msg_chunk, "content", "")

            if content:
                full_response += content
                placeholder.markdown(full_response + "▌")

        # final render (remove cursor)
        placeholder.markdown(full_response)

    # save assistant message
    st.session_state.messages.append({
        "role": "assistant",
        "content": full_response
    })


# -------------------------
# SIDEBAR
# -------------------------
with st.sidebar:
    st.header("Options")

    if st.button("Clear Chat 🗑️"):
        st.session_state.messages = []
        st.session_state.thread_id = str(uuid.uuid4())
        st.rerun()

    st.divider()

    st.write("Thread ID:")
    st.code(st.session_state.thread_id)