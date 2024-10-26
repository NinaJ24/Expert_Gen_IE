import streamlit as st
import random
import time
from dotenv import load_dotenv
# import threading  # 导入 threading 模块
# import logging    # 导入 logging 模块
from pinecone_plugins.assistant.models.chat import Message
from pinecone import Pinecone


load_dotenv()

PINECONE_API_KEY = st.secrets['PINECONE_API_KEY']

pc = Pinecone(api_key=PINECONE_API_KEY)
assistant = pc.assistant.Assistant(assistant_name="example-assistant2")

def get_response_content(query):
    # Create a Message object using the input text
    msg = Message(content=query)

    # Call the chat function with the Message object
    resp = assistant.chat(messages=[msg])

    # Extract the content part of the response
    answer = resp.get("message", {}).get("content", "")

    # Output and return the content part
    print(answer)
    # display(Markdown(content_text))

    return answer


# Streamed response emulator
def response_generator():
    response = random.choice(
        [
            "Hello there! How can I assist you today?",
            "Hi, human! Is there anything I can help you with?",
            "Do you need help?",
        ]
    )
    for word in response.split():
        yield word + " "
        time.sleep(0.05)


st.title("ExpertGen")
st.subheader("A generative AI-powered learning assistant providing professional, in-depth insights in tailored domains.")
# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("Ask your query about civil engineering"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)
    answer = get_response_content(prompt)
    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        # response = st.write_stream(response_generator())
        st.markdown(answer)
    # Add assistant response to chat history
    # st.session_state.messages.append({"role": "assistant", "content": response})
    st.session_state.messages.append({"role": "assistant", "content": answer})
