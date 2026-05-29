import streamlit as st
from groq import Groq


st.set_page_config(page_title="Shella AI // System", page_icon="🤖", layout="centered")


st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Courier+Prime&display=swap');
    
    .stApp { background-color: #050505; font-family: 'Courier Prime', monospace; }
    h1 { color: #ff0055; text-align: center; text-transform: uppercase; 
         text-shadow: 0 0 10px #ff0055; margin-bottom: 20px; }
    
    .stChatInput { border: 2px solid #ff0055 !important; border-radius: 5px !important; }
    .stChatMessage.user { background-color: #1a0005; border: 1px solid #ff0055; color: #ffcccc; }
    .stChatMessage.assistant { background-color: #0f0f0f; border: 1px solid #333; color: #ffffff; }
    
    .status { color: #33ff33; text-align: center; font-size: 0.8em; margin-bottom: 20px; }
    .footer { text-align: center; color: #555; margin-top: 50px; font-size: 0.7em; }
    </style>
    """, unsafe_allow_html=True)


try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except:
    st.error("Error: API Key tidak ditemukan! Cek file .streamlit/secrets.toml")
    st.stop()

st.title("// SHELLA_CORE_AI")
st.markdown("<p class='status'>// STATUS: ONLINE //</p>", unsafe_allow_html=True)


if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": "Nama kamu adalah Shella. Developer kamu adalah chyybenk. Kamu adalah asisten AI yang keren, cerdas, dan bergaya hacker. Selalu gunakan bahasa yang santai dan cool."}
    ]

for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.markdown(message["content"])


if prompt := st.chat_input("// Masukkan perintah..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)


    with st.chat_message("assistant"):
        def stream_generator():
            stream = client.chat.completions.create(
                messages=st.session_state.messages,
                model="llama-3.3-70b-versatile",
                stream=True,
            )
            for chunk in stream:
                content = chunk.choices[0].delta.content
                if content is not None:
                    yield content
        
        response = st.write_stream(stream_generator())
    
    st.session_state.messages.append({"role": "assistant", "content": response})

st.markdown("<div class='footer'>// DEVELOPED_BY: chyybenk // BUILT_WITH_GROQ_AI</div>", unsafe_allow_html=True)