from openai import OpenAI
import streamlit as st
import base64
import os

api_key = os.getenv("API_KEY")
base_url = os.getenv("BASE_URL")

pass_word = os.getenv("PASSWORD")

model_list = [
    "Qwen/Qwen2-VL-72B-Instruct",
    "OpenGVLab/InternVL2-26B",
    "OpenGVLab/InternVL2-Llama3-76B"]

if "login" not in st.session_state:
    st.session_state.login = False

if "msg" not in st.session_state:
    st.session_state.msg = []

with st.sidebar:
    clear_btn = st.button("Clear", "clear_btn", type="primary", disabled=st.session_state.msg==[])
    model = st.selectbox("Model", model_list, 0, key="model", disabled=st.session_state.msg!=[])
    max_tokens = st.slider("Max Tokens", 1, 4096, 4096, 1, key="max_tokens", disabled=st.session_state.msg!=[])
    temperature = st.slider("Temperature", 0.00, 2.00, 0.70, 0.01, key="temperature", disabled=st.session_state.msg!=[])
    top_p = st.slider("Top P", 0.00, 1.00, 0.70, 0.01, key="top_p", disabled=st.session_state.msg!=[])
    frequency_penalty = st.slider("Frequency Penalty", -2.00, 2.00, 0.00, 0.01, key="frequency_penalty", disabled=st.session_state.msg!=[])
    presence_penalty = st.slider("Presence Penalty", -2.00, 2.00, 0.00, 0.01, key="presence_penalty", disabled=st.session_state.msg!=[])

if not st.session_state.login:
    password = st.text_input("Password", type="password", key="password")
    login_btn = st.button("Login", "login_btn", disabled=not password)

    if login_btn:
        if password == pass_word:
            st.session_state.login = True
        else:
            st.session_state.login = False
        st.rerun()

if st.session_state.login:
    image_file = st.file_uploader("Image", type=["png", "jpg", "jpeg"], key="image_file", disabled=st.session_state.msg!=[], label_visibility="collapsed")
    if image_file is not None:
        with st.expander("Image"):
            st.image(image_file)
        image_type = image_file.name.split(".")[-1].lower()
        image_bytes = image_file.read()
        image_b64 = base64.b64encode(image_bytes).decode("utf-8")
        image_url = f"data:image/{image_type};base64,{image_b64}"

    for i in st.session_state.msg:
        with st.chat_message(i["role"]):
            st.markdown(i["content"])
    
    if query := st.chat_input("Say something...", key="query", disabled=not image_file):
        st.session_state.msg.append({"role": "user", "content": query})
        with st.chat_message("user"):
            st.markdown(query)
        
        if len(st.session_state.msg) == 1:
            messages = [
                {"role": "user", "content": [
                    {"type": "text", "text": query},
                    {"type": "image_url", "image_url": {"url": image_url}}]}]
        else:
            messages = [
                {"role": "user", "content": [
                    {"type": "text", "text": st.session_state.msg[0]["content"]},
                    {"type": "image_url", "image_url": {"url": image_url}}]}] + st.session_state.msg[1:]
        
        client = OpenAI(api_key=api_key, base_url=base_url)
        with st.chat_message("assistant"):
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=top_p,
                frequency_penalty=frequency_penalty,
                presence_penalty=presence_penalty,
                stream=True)
            result = st.write_stream(chunk.choices[0].delta.content for chunk in response if chunk.choices[0].delta.content is not None)
            st.session_state.msg.append({"role": "assistant", "content": result})
        
        st.rerun()

if clear_btn:
    st.session_state.msg = []
    st.rerun()