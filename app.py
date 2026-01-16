import streamlit as st
import pandas as pd
from groq import Groq

st.set_page_config(page_title="Chatbot Excel", layout="centered")

# Masukkan API Key dari Secrets Streamlit
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

st.title("📊 Chatbot Data Excel")

# Baca data
@st.cache_data
def load_data():
    df = pd.read_excel("data.xlsx")
    return df.to_string()

context_data = load_data()

# Chat interface
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Tanya tentang data Excel anda..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": f"Rujuk data ini: {context_data}"},
                {"role": "user", "content": prompt}
            ],
            model="llama3-8b-8192",
        )
        response = chat_completion.choices[0].message.content
        st.markdown(response)
    st.session_state.messages.append({"role": "assistant", "content": response})
