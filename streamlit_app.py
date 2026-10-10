
import streamlit as st
from agent import process_message, memory, SYSTEM_MESSAGE

st.set_page_config(
    page_title="CampusConnect Support",
    page_icon="🎓",
    layout="centered",
)

st.title("🎓 CampusConnect Support")
st.caption("AI-powered student support assistant")

with st.sidebar:
    st.header("Available tools")
    st.markdown(
        """
        - 🔎 Knowledge-base search
        - 📄 Policy lookup
        - 🎫 Support ticket creation
        - 🤝 Human escalation
        """
    )
    st.info("Demo application using fictional CampusConnect policies.")

if "messages" not in st.session_state:
    st.session_state.messages = []

if "agent_messages" not in st.session_state:
    st.session_state.agent_messages = [
        {"role": "system", "content": SYSTEM_MESSAGE}
    ]

if st.button("Clear conversation"):
    st.session_state.messages = []
    st.session_state.agent_messages = [
        {"role": "system", "content": SYSTEM_MESSAGE}
    ]
    memory.messages = st.session_state.agent_messages.copy()
    st.rerun()

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

prompt = st.chat_input("How can I help you today?")

if prompt:
    st.session_state.messages.append(
        {"role": "user", "content": prompt}
    )

    with st.chat_message("user"):
        st.markdown(prompt)

    
    with st.chat_message("assistant"):
        activity = st.status(
            "CampusConnect is processing your request...",
            expanded=True
        )

       
        def on_tool_event(event):
            tool_name = event.get("tool", "unknown")

            if event["type"] == "tool_start":
                activity.write(
                    event.get("message", f"Calling {tool_name}...")
                )

            elif event["type"] == "tool_result":
                if event.get("success"):
                    activity.write(
                        f"✅ {tool_name} completed successfully"
                    )
                else:
                    activity.write(
                        f"⚠️ {tool_name} failed"
                    )
    

        memory.messages = st.session_state.agent_messages.copy()
        reply = process_message(prompt, on_tool_event=on_tool_event)

        st.session_state.agent_messages = memory.messages.copy()

        activity.update(
            label="Tool activity completed",
            state="complete",
            expanded=True
        )

        st.markdown(reply)


    st.session_state.messages.append(
        {"role": "assistant", "content": reply}
    )
