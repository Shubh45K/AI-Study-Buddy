import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv
import os

load_dotenv()

genai.configure(
    api_key=os.getenv("GEMINI_API_KEY")
)

model = genai.GenerativeModel(
    "gemini-2.5-flash"
)

st.set_page_config(
    page_title="AI Study Buddy",
    layout="wide"
)

st.title("AI Study Buddy")

prompt = st.chat_input(
    "Ask anything about your studies..."
)

if prompt:

    with st.chat_message("user"):
        st.write(prompt)

    response = model.generate_content(
        prompt
    )

    with st.chat_message("assistant"):
        st.write(response.text)