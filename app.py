import streamlit as st
import os
import requests
import json

url = "http://localhost:8000/v1/chat/completions"

headers = {
    "Content-Type": "application/json"
}

# App title
st.set_page_config(page_title="💬 LLM Chatbot")


# @st.cache_resource()
# def ChatModel(temperature, top_p):
#     return AutoModelForCausalLM.from_pretrained(
#         'ggml-llama-2-7b-chat-q4_0.bin',
#         model_type='llama',
#         temperature=temperature,
#         top_p=top_p)


# Replicate Credentials
with st.sidebar:
    st.title('💬 LLM Chatbot')

    # Refactored from <https://github.com/a16z-infra/llama2-chatbot>
    st.subheader('Models and parameters')
    selected_model = st.sidebar.selectbox('Choose an LLM', ['Llama2-Chinese-13b-Chat', "llama-2-13b-chat-hf", 'Qwen-14B-Chat', "chatglm3-6b", 'Baichuan2-13B-Chat'], key='selected_model')
    temperature = st.sidebar.slider('temperature', min_value=0.01, max_value=2.0, value=0.1, step=0.01)
    top_p = st.sidebar.slider('top_p', min_value=0.01, max_value=1.0, value=0.9, step=0.01)
    max_tokens = st.sidebar.slider('max_tokens', min_value=64, max_value=4096, value=512, step=8)
    # chat_model = ChatModel(temperature, top_p)
    # st.markdown('📖 Learn how to build this app in this [blog](#link-to-blog)!')

# Store LLM generated responses
if "messages" not in st.session_state.keys():
    st.session_state.messages = [{"role": "assistant", "content": "How may I assist you today?"}]

# Display or clear chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])


def clear_chat_history():
    st.session_state.messages = [{"role": "assistant", "content": "How may I assist you today?"}]


st.sidebar.button('Clear Chat History', on_click=clear_chat_history)


# Function for generating LLaMA2 response
def generate_llama2_response(prompt_input):
    string_dialogue = "You are a helpful assistant. You do not respond as 'User' or pretend to be 'User'. You only respond once as 'Assistant'."
    for dict_message in st.session_state.messages:
        if dict_message["role"] == "user":
            string_dialogue += "User: " + dict_message["content"] + "\\n\\n"
        else:
            string_dialogue += "Assistant: " + dict_message["content"] + "\\n\\n"

    data = {
        "model": f"{selected_model}",
        "messages": [
            {"role": "user", "content": f"{prompt_input}"}
        ],
        "top_p": top_p,
        "temperature": temperature,
        "max_tokens": max_tokens
    }

    response = requests.post(url, headers=headers, data=json.dumps(data))
    response_data = response.json()

    # 获取 "content" 字段的内容
    output = response_data["choices"][0]["message"]["content"]

    # output = chat_model(f"prompt {string_dialogue} {prompt_input} Assistant: ")
    return output


# User-provided prompt
if prompt := st.chat_input():
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

# Generate a new response if last message is not from assistant
if st.session_state.messages[-1]["role"] != "assistant":
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = generate_llama2_response(prompt)
            placeholder = st.empty()
            full_response = ''
            for item in response:
                full_response += item
                placeholder.markdown(full_response)
            placeholder.markdown(full_response)
    message = {"role": "assistant", "content": full_response}
    st.session_state.messages.append(message)
