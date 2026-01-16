import streamlit as st
import pandas as pd
from groq import Groq

st.set_page_config(page_title="Chatbot Excel", layout="centered")

if "GROQ_API_KEY" not in st.secrets:
    st.error("Sila masukkan GROQ_API_KEY dalam Secrets!")
    st.stop()

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

st.title("📊 Chatbot Data Excel (Safe Mode)")

@st.cache_data
def load_data():
    try:
        df = pd.read_excel("data.xlsx")
        # KURANGKAN HAD: Ambil 10 baris teratas sahaja untuk elak ralat 413
        # Ini akan menjimatkan penggunaan token (TPM)
        return df.head(10).to_string(index=False)
    except Exception as e:
        return f"Ralat baca fail: {e}"

context_data = load_data()

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Tanya tentang data Excel..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            chat_completion = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {
                        "role": "system", 
                        "content": f"Anda pembantu data. Rujuk data ringkas ini: {context_data}"
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=500 # Hadkan panjang jawapan AI juga
            )
            response = chat_completion.choices[0].message.content
            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})
        except Exception as e:
            # Jika masih ralat, beritahu pengguna secara spesifik
            if "rate_limit_exceeded" in str(e):
                st.error("Data terlalu besar untuk diproses serentak. Sila kurangkan saiz fail Excel anda.")
            else:
                st.error(f"Ralat: {e}")
