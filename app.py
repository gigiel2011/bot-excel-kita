import streamlit as st
import pandas as pd
from groq import Groq

st.set_page_config(page_title="Chatbot Excel", layout="centered")

# Pastikan Secret wujud
if "GROQ_API_KEY" not in st.secrets:
    st.error("Sila masukkan GROQ_API_KEY dalam Advanced Settings!")
    st.stop()

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

st.title("📊 Chatbot Data Excel")

@st.cache_data
def load_data():
    df = pd.read_excel("data.xlsx")
    # Ambil 20 baris pertama sahaja untuk ujian jika fail terlalu besar
    # atau tukar ke format yang lebih ringkas
    return df.to_string(index=False, max_rows=50) 

try:
    context_data = load_data()
except Exception as e:
    st.error(f"Gagal baca Excel: {e}")
    st.stop()

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
        try:
    chat_completion = client.chat.completions.create(
        # Gunakan model terbaru ini
        model="llama-3.1-8b-instant", 
        messages=[
            {
                "role": "system", 
                "content": f"Anda pembantu data. Jawab ringkas berdasarkan data ini:\n\n{context_data}"
            },
            {"role": "user", "content": prompt}
        ],
        temperature=0.2,
    )
    response = chat_completion.choices[0].message.content
    st.markdown(response)
    st.session_state.messages.append({"role": "assistant", "content": response})
except Exception as e:
    st.error(f"Ralat Groq: {e}")
