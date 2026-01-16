import streamlit as st
import pandas as pd
from groq import Groq

st.set_page_config(page_title="Chatbot Excel", layout="centered")

# 1. Pastikan API Key ada
if "GROQ_API_KEY" not in st.secrets:
    st.error("Sila masukkan GROQ_API_KEY dalam Advanced Settings > Secrets!")
    st.stop()

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

st.title("📊 Chatbot Data Excel")

# 2. Fungsi baca data
@st.cache_data
def load_data():
    try:
        df = pd.read_excel("data.xlsx")
        # Kita ambil 50 baris pertama supaya tidak 'Error 400' (terlalu panjang)
        return df.to_string(index=False, max_rows=50)
    except Exception as e:
        return f"Fail data.xlsx tidak ditemui. Ralat: {e}"

context_data = load_data()

# 3. Urus sejarah mesej
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 4. Kotak input chat
if prompt := st.chat_input("Tanya tentang data Excel anda..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        # Bahagian TRY yang menyebabkan error tadi sudah dibetulkan jaraknya
        try:
            chat_completion = client.chat.completions.create(
                model="llama-3.1-8b-instant", # Model terbaru
                messages=[
                    {
                        "role": "system", 
                        "content": f"Anda pembantu data. Jawab berdasarkan data ini sahaja:\n\n{context_data}"
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
