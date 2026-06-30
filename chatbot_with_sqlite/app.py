import uuid
import streamlit as st

from langchain_core.messages import HumanMessage

from langgraph_bot import app
from chat_store import load_chat_ids, save_chat_ids


# ------------------------------------------------
# PAGE CONFIG


st.set_page_config(
    page_title="Qwen Chatbot",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 Qwen Resume Chatbot")


# ------------------------------------------------
# SESSION STATE INIT


if "chat_ids" not in st.session_state:
    st.session_state["chat_ids"] = load_chat_ids()


if "active_chat" not in st.session_state:

    if st.session_state["chat_ids"]:
        st.session_state["active_chat"] = \
            st.session_state["chat_ids"][0]

    else:
        new_id = str(uuid.uuid4())

        st.session_state["chat_ids"] = [new_id]

        save_chat_ids(
            st.session_state["chat_ids"]
        )

        st.session_state["active_chat"] = new_id


# ------------------------------------------------
# SIDEBAR


with st.sidebar:

    st.header("💬 Chats")

    if st.button("➕ New Chat"):

        new_id = str(uuid.uuid4())

        st.session_state["chat_ids"].append(
            new_id
        )

        save_chat_ids(
            st.session_state["chat_ids"]
        )

        st.session_state["active_chat"] = new_id

        st.rerun()

    st.divider()

    for chat_id in st.session_state["chat_ids"]:

        label = f"Chat {chat_id}"

        if st.button(label,key=f"chat_btn{chat_id}"):

            st.session_state["active_chat"] = \
                chat_id

            st.rerun()

    st.divider()

    st.write("Current Chat")

    st.code(
        st.session_state["active_chat"]
    )


# ------------------------------------------------
# LOAD CURRENT CHAT HISTORY
# ------------------------------------------------

config = {
    "configurable": {
        "thread_id":
            st.session_state["active_chat"]
    }
}

snapshot = app.get_state(config)

if snapshot.values:

    for msg in snapshot.values["messages"]:

        role = (
            "user"
            if msg.type == "human"
            else "assistant"
        )

        with st.chat_message(role):
            st.markdown(msg.content)


# ------------------------------------------------
# USER INPUT
# ------------------------------------------------

prompt = st.chat_input(
    "Type your message..."
)

if prompt:

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):

        placeholder = st.empty()

        full_response = ""

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

            if chunk.get("type") != "messages":
                continue

            msg_chunk, metadata = chunk["data"]

            content = getattr(
                msg_chunk,
                "content",
                ""
            )

            if content:
                full_response += content

                placeholder.markdown(
                    full_response + "▌"
                )

        placeholder.markdown(full_response)

    st.rerun()