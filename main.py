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

import openai #added open AI
from PIL import Image #Added Image
# from streamlit_paste_button import paste_image  # Added to enable clipboard image pasting - 0310
# from streamlit_paste_button import paste_image_button as pbutton
from streamlit_paste_button import paste_image_button as pbutton
import io
import os
from openai import OpenAI
import base64  # Added to handle image conversion for GPT-4o - 0310

load_dotenv()

PINECONE_API_KEY = st.secrets['PINECONE_API_KEY']
OPENAI_API_KEY = st.secrets['OPENAI_API_KEY']
client = OpenAI(
    api_key=OPENAI_API_KEY,  # This is the default and can be omitted
)

pc = Pinecone(api_key=PINECONE_API_KEY)
# assistant = pc.assistant.Assistant(assistant_name="example-assistant2")
assistant = pc.assistant.Assistant(assistant_name="ie577")

if "messages" not in st.session_state:
    st.session_state.messages = []
if "uploaded_file" not in st.session_state:
    st.session_state.uploaded_file = None


def encode_image(image_bytes):

    return base64.b64encode(image_bytes).decode("utf-8")


def describe_image(uploaded_file):

    try:
        if uploaded_file is None:
            return "No image uploaded or pasted."

        # Send image to GPT-4o Vision model
        # base64_image = encode_image(image_bytes)  

        image = Image.open(uploaded_file)
# -------------------convert to legal format------
        # Ensure the image is in a supported format
        if image.mode in ("RGBA", "P"):  # Convert images with transparency to RGB
            image = image.convert("RGB")

        # Save the image as a clean, standard PNG or JPEG
        image_buffer = io.BytesIO()
        image.save(image_buffer, format="PNG")  # Ensure valid PNG format
        image_bytes = image_buffer.getvalue()
        # -------------------convert to legal format------
        # image_bytes = uploaded_file.read()

        # Encode the image bytes
        base64_image = encode_image(image_bytes)
        # base64_image = encode_image(uploaded_file)  
        
        response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "You are an AI specialized in extracting text, questions, tables, and figures from uploaded images. Extract only the questions, tables, and diagrams without adding explanations or unnecessary details. Maintain the original structure of the content as much as possible.",
                    },
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
                    },
                ],
            }
        ],
    )

        st.session_state.uploaded_file = None # added to clear
        st.session_state["uploader_key"] += 1  # ✅ 关键：强制刷新 file_uploader 
        # added0403 2025
        return response.choices[0].message.content  # Return AI-generated response

    except Exception as e:
        return f"Error processing the image: {str(e)}"

def process_input(uploaded_file=None, prompt=""): 
    image_description = ""  # Variable to store extracted text from image
    # Step 1: Process Uploaded Image
    if uploaded_file:
        if isinstance(uploaded_file, io.BytesIO):
            image = Image.open(uploaded_file)
        else:
            image = uploaded_file  # Directly use pasted images if they are already PIL objects

        # Display the uploaded image
        st.image(image, caption="Uploaded Image", use_container_width=True)

        image_description = describe_image(uploaded_file)
        # ✅ 新增：存储图像描述到 session（用于拼接）
        st.session_state.last_image_description = image_description
        # Store extracted content in chat history
        st.session_state.messages.append({"role": "assistant", "content": f"**Extracted Content from Image:**\n{image_description}"})

        # Display extracted content
        with st.chat_message("assistant"):
            st.markdown(f"**Extracted Content from Image:**\n\n{image_description}")

        # ✅ 新增：清除上传图片状态
        # st.session_state.uploaded_file = None
    st.session_state.uploaded_file = None  # ✅ MODIFIED: unified cleanup
    # ✅ 新增：如果没有新图，用 pop 拿一次旧图描述，并立即清除
    image_description = st.session_state.pop("last_image_description", "")
    # Step 2: Combine Extracted Image Text with User Prompt
    combined_prompt = f"{image_description}\n\nUser Query: {prompt}".strip() if image_description else prompt
    st.session_state.uploaded_file = None
    # st.session_state.pasted_image = None  # ✅ 确保粘贴的图片也被清除
        # **确保 UI 重新加载，以清除 file_uploader**
    # st.rerun()  # ✅ 强制刷新 Streamlit UI，避免 file_uploader 仍然显示旧图片 不可以 加了就不能回答了
    return combined_prompt  # Only return the combined prompt


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
# -------0403原来得上传
if "uploader_key" not in st.session_state:
    st.session_state["uploader_key"] = 0

# uploaded_file = st.file_uploader(
#     # "Upload an image or paste from clipboard",
#     "Upload an image",
#     type=["png", "jpg", "jpeg"],
#     key=st.session_state["uploader_key"]
# )
# # -------0403原来得上传

# if uploaded_file:
#     st.session_state.uploaded_file = uploaded_file


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
    # # enhanced_prompt = f"{prompt} Provide cited source text if available."
    # enhanced_prompt = f"{prompt} Also provide me the source cited text"
    combined_prompt =  process_input(uploaded_file, prompt)
    # combined_prompt = process_input(uploaded_file, prompt, has_new_image)
    enhanced_prompt = f"{combined_prompt}\n\nAlso provide me the source cited text if available"

    
    # 将增强后的输入加入聊天记录
    st.session_state.messages.append({"role": "user", "content": enhanced_prompt})
    
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(combined_prompt)

    # Display "I am thinking..." placeholder in assistant's response
    with st.chat_message("assistant"):
        thinking_placeholder = st.empty()
        thinking_placeholder.markdown("I am thinking...")
        answer = get_response_content(enhanced_prompt)
        thinking_placeholder.markdown(answer)  # <- update inside the same context
        st.session_state.messages.append({"role": "assistant", "content": answer})  # <- save to history
    # 👇 append upload control at the very end
    uploaded_file = st.file_uploader(
    # "Upload an image or paste from clipboard",
    "Upload an image",
    type=["png", "jpg", "jpeg"],
    key=st.session_state["uploader_key"]
)
    if uploaded_file:
    st.session_state.uploaded_file = uploaded_file

    # Generate actual response
    # answer = get_response_content(prompt)
    # answer = get_response_content(enhanced_prompt)

    # # Update the placeholder with the actual response
    # thinking_placeholder.markdown(answer)

    # # Add assistant response to chat history
    # st.session_state.messages.append({"role": "assistant", "content": answer})
