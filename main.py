import streamlit as st
import random
import time
from dotenv import load_dotenv
# import threading  # 导入 threading 模块
# import logging    # 导入 logging 模块
# from pinecone_plugins.assistant.models.chat import Message
from pinecone_plugins.assistant.models.chat import Message
# from pinecone import Message
from pinecone import Pinecone


load_dotenv()

PINECONE_API_KEY = st.secrets['PINECONE_API_KEY']

pc = Pinecone(api_key=PINECONE_API_KEY)
# assistant = pc.assistant.Assistant(assistant_name="example-assistant2")
assistant = pc.assistant.Assistant(assistant_name="ie577")
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

# # Accept user input
# if prompt := st.chat_input("Ask your query about human factors, safety engineering, and applied ergonomics. "):
#     # Add user message to chat history
#     st.session_state.messages.append({"role": "user", "content": prompt})
#     # Display user message in chat message container
#     with st.chat_message("user"):
#         st.markdown(prompt)
#     answer = get_response_content(prompt)
#     # Display assistant response in chat message container
#     with st.chat_message("assistant"):
#         # response = st.write_stream(response_generator())
#         st.markdown(answer)
#     # Add assistant response to chat history
#     # st.session_state.messages.append({"role": "assistant", "content": response})
#     st.session_state.messages.append({"role": "assistant", "content": answer})

if prompt := st.chat_input("Ask your query about human factors, safety engineering, and applied ergonomics."):
    # Add user message to chat history
    # st.session_state.messages.append({"role": "user", "content": prompt})
    # 在用户输入后附加内容
    # enhanced_prompt = f"{prompt} Provide cited source text if available."
    enhanced_prompt = f"{prompt} Also provide me the source cited text"
    
    # 将增强后的输入加入聊天记录
    st.session_state.messages.append({"role": "user", "content": enhanced_prompt})
    
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)

    # Display "I am thinking..." placeholder in assistant's response
    with st.chat_message("assistant"):
        thinking_placeholder = st.empty()
        thinking_placeholder.markdown("I am thinking...")

    # Generate actual response
    # answer = get_response_content(prompt)
    answer = get_response_content(enhanced_prompt)

    # Update the placeholder with the actual response
    thinking_placeholder.markdown(answer)

    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": answer})
