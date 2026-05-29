import streamlit as st
from groq import Groq
import io
from PIL import Image
import PyPDF2
import docx
import pandas as pd
import json
import os
from datetime import datetime
import base64

# ========== KONFIGURASI HALAMAN ==========
st.set_page_config(
    page_title="Shella AI // Vision",
    page_icon="⚡",
    layout="centered",
    initial_sidebar_state="expanded"
)

# ========== STYLE (SAMA SEPERTI SEBELUMNYA) ==========
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:opsz,wght@14..32,300;14..32,400;14..32,600;14..32,700&display=swap');
    
    .stApp {
        background: radial-gradient(circle at 20% 30%, #0a0a0a, #000000);
        font-family: 'Inter', sans-serif;
    }
    
    h1 {
        font-size: 2.8rem;
        font-weight: 700;
        background: linear-gradient(135deg, #ff2a6d, #ff0055);
        -webkit-background-clip: text;
        background-clip: text;
        color: transparent;
        text-align: center;
        text-transform: uppercase;
        letter-spacing: 3px;
        margin-bottom: 0.2rem;
        text-shadow: 0 0 15px rgba(255, 0, 85, 0.5);
    }
    
    .status {
        text-align: center;
        font-size: 0.8rem;
        font-weight: 500;
        letter-spacing: 1px;
        margin-bottom: 1.5rem;
        color: #ff2a6d;
        background: rgba(255, 42, 109, 0.1);
        display: inline-block;
        width: auto;
        margin-left: auto;
        margin-right: auto;
        padding: 0.3rem 1rem;
        border-radius: 40px;
        backdrop-filter: blur(4px);
        border: 1px solid rgba(255, 42, 109, 0.4);
    }
    
    .stChatMessage {
        background: rgba(10, 10, 10, 0.7);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        padding: 0.8rem 1.2rem;
        margin-bottom: 1rem;
        border: 1px solid rgba(255, 42, 109, 0.2);
        transition: all 0.2s ease;
    }
    .stChatMessage:hover {
        border-color: #ff2a6d;
        box-shadow: 0 0 12px rgba(255, 42, 109, 0.2);
    }
    
    [data-testid="stChatMessage"]:nth-child(odd) {
        background: linear-gradient(135deg, rgba(255, 42, 109, 0.15), rgba(10, 10, 10, 0.9));
        border-left: 4px solid #ff2a6d;
    }
    
    [data-testid="stChatMessage"]:nth-child(even) {
        background: rgba(20, 20, 20, 0.8);
        border-left: 4px solid #333;
    }
    
    .stChatInput {
        position: relative;
    }
    .stChatInput textarea {
        background-color: #111 !important;
        border: 2px solid #ff2a6d !important;
        border-radius: 40px !important;
        color: white !important;
        font-family: 'Inter', monospace !important;
        font-size: 1rem !important;
        padding: 0.8rem 1.5rem 0.8rem 60px !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 0 8px rgba(255, 42, 109, 0.3) !important;
    }
    .stChatInput textarea:focus {
        border-color: #ff2a6d !important;
        box-shadow: 0 0 20px rgba(255, 42, 109, 0.6) !important;
        background-color: #1a1a1a !important;
    }
    .stChatInput textarea::placeholder {
        color: #ff2a6d80 !important;
        font-style: italic;
    }
    
    button[data-testid="baseButton-secondary"] {
        background: linear-gradient(135deg, #ff2a6d, #ff0055) !important;
        border-radius: 40px !important;
        color: white !important;
        border: none !important;
        font-weight: bold !important;
        transition: 0.2s !important;
    }
    button[data-testid="baseButton-secondary"]:hover {
        transform: scale(1.05);
        box-shadow: 0 0 12px #ff2a6d;
    }
    
    div[data-testid="stFileUploader"] {
        position: absolute;
        bottom: 12px;
        left: 20px;
        width: 40px !important;
        height: 40px !important;
        z-index: 999;
        opacity: 0;
        cursor: pointer;
    }
    
    .upload-icon {
        position: absolute;
        bottom: 25px;
        left: 30px;
        font-size: 22px;
        color: #ff2a6d;
        pointer-events: none;
        z-index: 998;
        filter: drop-shadow(0 0 2px #ff0055);
    }
    
    [data-testid="stSidebar"] {
        background: rgba(5, 5, 5, 0.95);
        backdrop-filter: blur(12px);
        border-right: 1px solid #ff2a6d40;
    }
    
    ::-webkit-scrollbar {
        width: 5px;
    }
    ::-webkit-scrollbar-track {
        background: #0a0a0a;
    }
    ::-webkit-scrollbar-thumb {
        background: #ff2a6d;
        border-radius: 10px;
    }
    
    .footer {
        text-align: center;
        margin-top: 3rem;
        font-size: 0.7rem;
        color: #444;
        border-top: 1px solid rgba(255, 42, 109, 0.2);
        padding-top: 1rem;
    }
    
    @media (max-width: 768px) {
        h1 { font-size: 1.8rem !important; }
        .stChatInput textarea { padding-left: 50px !important; font-size: 0.9rem !important; }
        .upload-icon { font-size: 18px !important; bottom: 20px !important; left: 22px !important; }
        div[data-testid="stFileUploader"] { bottom: 8px !important; left: 12px !important; }
    }
    </style>
    """, unsafe_allow_html=True)

# ========== INISIALISASI GROQ ==========
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except Exception:
    st.error("❌ API Key tidak ditemukan! Cek file .streamlit/secrets.toml")
    st.stop()

# ========== FUNGSI BACA FILE ==========
def extract_text_from_file(uploaded_file) -> str:
    file_type = uploaded_file.type
    file_name = uploaded_file.name
    text_content = f"[File: {file_name}]\n"
    try:
        if "text" in file_type:
            text_content += uploaded_file.getvalue().decode("utf-8")
        elif "pdf" in file_type:
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(uploaded_file.getvalue()))
            for page in pdf_reader.pages:
                text_content += page.extract_text()
        elif "wordprocessingml" in file_type:
            doc = docx.Document(io.BytesIO(uploaded_file.getvalue()))
            for para in doc.paragraphs:
                text_content += para.text + "\n"
        elif "csv" in file_type:
            df = pd.read_csv(io.BytesIO(uploaded_file.getvalue()))
            text_content += df.to_string()
        else:
            text_content += "Tipe file tidak bisa diekstrak teksnya."
    except Exception as e:
        text_content += f"Gagal membaca: {str(e)}"
    return text_content

# ========== LOGIN HANDLER ==========
if "manual_email" not in st.session_state:
    st.session_state.manual_email = None

def get_user_email():
    if hasattr(st, 'experimental_user') and st.experimental_user:
        if hasattr(st.experimental_user, 'email'):
            return st.experimental_user.email
        elif isinstance(st.experimental_user, dict) and 'email' in st.experimental_user:
            return st.experimental_user['email']
    return st.session_state.manual_email

user_email = get_user_email()

# ========== MANAJEMEN HISTORY ==========
def save_history_to_file(email):
    if "histories" in st.session_state and email:
        data = {email: st.session_state.histories}
        safe_email = email.replace("@", "_at_").replace(".", "_")
        with open(f"history_{safe_email}.json", "w") as f:
            json.dump(data, f)

def load_history_from_file(email):
    safe_email = email.replace("@", "_at_").replace(".", "_")
    if os.path.exists(f"history_{safe_email}.json"):
        with open(f"history_{safe_email}.json", "r") as f:
            data = json.load(f)
            return data.get(email, [])
    return []

def create_new_session():
    new_id = datetime.now().strftime("%Y%m%d%H%M%S")
    new_session = {
        "id": new_id,
        "name": f"Chat {new_id[-4:]}",
        "messages": [{"role": "system", "content": "Nama kamu adalah Shella. Developer kamu adalah chyybenk. Kamu adalah asisten AI yang keren, cerdas, dan bergaya hacker. Gunakan bahasa gaul modern, singkat, dan penuh energi. Suka menggunakan emoji ⚡🔥."}]
    }
    st.session_state.histories.insert(0, new_session)
    st.session_state.current_session_id = new_id
    st.session_state.messages = new_session["messages"].copy()
    if user_email:
        save_history_to_file(user_email)

# ========== INISIALISASI DEFAULT SESSION STATE (PENTING!) ==========
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": "Nama kamu adalah Shella. Developer kamu adalah chyybenk. Kamu adalah asisten AI yang keren, cerdas, dan bergaya hacker. Gunakan bahasa gaul modern, singkat, dan penuh energi. Suka menggunakan emoji ⚡🔥."}]
if "histories" not in st.session_state:
    st.session_state.histories = []
if "current_session_id" not in st.session_state:
    st.session_state.current_session_id = None

# ========== SIDEBAR: LOGIN & HISTORY ==========
with st.sidebar:
    st.markdown("### 🧠 HISTORY CHAT")
    
    if not user_email:
        st.warning("🔐 Login Biar Historymu Kesimpen")
        manual_email = st.text_input("Email (manual):", placeholder="chybenk@gmail.com")
        if st.button("Login / Lanjutkan", use_container_width=True):
            if manual_email:
                st.session_state.manual_email = manual_email
                st.rerun()
            else:
                st.error("Masukkan email")
        st.caption("Jadilah seperti sistem yang tangguh: saat server dunia mencoba mematikanmu, kamu selalu punya backup untuk bangkit lebih kuat.")
    else:
        st.success(f"✅ {user_email}")
        
        if not st.session_state.histories:
            st.session_state.histories = load_history_from_file(user_email)
            if not st.session_state.histories:
                create_new_session()
            elif not st.session_state.current_session_id:
                st.session_state.current_session_id = st.session_state.histories[0]["id"]
                st.session_state.messages = st.session_state.histories[0]["messages"].copy()
        
        if st.button("➕ New Chat", use_container_width=True):
            create_new_session()
            st.rerun()
        
        st.markdown("---")
        for i, sess in enumerate(st.session_state.histories):
            col1, col2 = st.columns([4, 1])
            with col1:
                if st.button(f"💬 {sess['name']}", key=f"load_{sess['id']}", use_container_width=True):
                    st.session_state.current_session_id = sess["id"]
                    st.session_state.messages = sess["messages"].copy()
                    st.rerun()
            with col2:
                if st.button("🗑️", key=f"del_{sess['id']}"):
                    st.session_state.histories.pop(i)
                    if st.session_state.histories:
                        st.session_state.current_session_id = st.session_state.histories[0]["id"]
                        st.session_state.messages = st.session_state.histories[0]["messages"].copy()
                    else:
                        create_new_session()
                    save_history_to_file(user_email)
                    st.rerun()
        
        st.markdown("---")
        if st.button("Logout", use_container_width=True):
            st.session_state.manual_email = None
            st.session_state.clear()
            st.rerun()

# ========== MAIN AREA ==========
st.markdown("<h1>⚡ SHELLA_CORE_AI</h1>", unsafe_allow_html=True)
st.markdown("<div class='status'>● ONLINE // READY</div>", unsafe_allow_html=True)

# Tampilkan pesan-pesan sebelumnya
for msg in st.session_state.messages:
    if msg["role"] != "system":
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg["role"] == "user" and "images" in msg and msg["images"]:
                for img_data in msg["images"]:
                    st.image(Image.open(io.BytesIO(img_data)), caption="Gambar", use_container_width=True)

# ========== UPLOAD FILE DI DALAM INPUT CHAT ==========
st.markdown('<div class="upload-icon">📎</div>', unsafe_allow_html=True)

uploaded_file = st.file_uploader(
    "Upload",
    type=["png", "jpg", "jpeg", "pdf", "docx", "txt", "csv"],
    key="main_uploader",
    label_visibility="collapsed"
)

if uploaded_file is not None:
    if uploaded_file.type.startswith("image/"):
        img = Image.open(uploaded_file)
        st.image(img, caption=uploaded_file.name, use_container_width=True)
        st.session_state.uploaded_image_data = uploaded_file.getvalue()
    else:
        text = extract_text_from_file(uploaded_file)
        st.session_state.uploaded_file_content = text
        with st.expander("Preview teks"):
            st.text(text[:500] + ("..." if len(text) > 500 else ""))
    st.success("✅ File siap digunakan.")

# ========== CHAT INPUT ==========
prompt = st.chat_input("@> mw tanya apa? shella siap bantu...")

if prompt:
    full_prompt = prompt
    image_data = None
    if "uploaded_image_data" in st.session_state:
        image_data = st.session_state.uploaded_image_data
        del st.session_state.uploaded_image_data
    if "uploaded_file_content" in st.session_state:
        full_prompt = f"{prompt}\n\n[KONTEKS FILE]:\n{st.session_state.uploaded_file_content}"
        del st.session_state.uploaded_file_content
    
    user_msg = {"role": "user", "content": full_prompt}
    if image_data:
        user_msg["images"] = [image_data]
    st.session_state.messages.append(user_msg)
    
    with st.chat_message("user"):
        st.markdown(prompt)
        if image_data:
            st.image(Image.open(io.BytesIO(image_data)), caption="Gambar yang diupload", use_container_width=True)
    
    with st.chat_message("assistant"):
        try:
            if image_data:
                base64_image = base64.b64encode(image_data).decode("utf-8")
                image_url = f"data:image/jpeg;base64,{base64_image}"
                response_stream = client.chat.completions.create(
                    model="llama-4-scout-17b-16e-instruct",
                    messages=[
                        {"role": "system", "content": st.session_state.messages[0]["content"]},
                        {"role": "user", "content": [{"type": "text", "text": prompt}, {"type": "image_url", "image_url": {"url": image_url}}]}
                    ],
                    stream=True,
                )
                response = st.write_stream((chunk.choices[0].delta.content or "" for chunk in response_stream))
            else:
                response_stream = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=st.session_state.messages,
                    stream=True,
                )
                response = st.write_stream((chunk.choices[0].delta.content or "" for chunk in response_stream))
        except Exception as e:
            st.error(f"Error: {str(e)}")
            response = "Maaf, terjadi kesalahan. Coba lagi nanti."
    
    st.session_state.messages.append({"role": "assistant", "content": response})
    
    if user_email and st.session_state.histories:
        for i, sess in enumerate(st.session_state.histories):
            if sess["id"] == st.session_state.current_session_id:
                st.session_state.histories[i]["messages"] = st.session_state.messages.copy()
                user_msgs = [m for m in st.session_state.messages if m["role"] == "user"]
                if len(user_msgs) == 1:
                    preview = user_msgs[0]["content"][:30] + ("..." if len(user_msgs[0]["content"]) > 30 else "")
                    st.session_state.histories[i]["name"] = preview
                break
        save_history_to_file(user_email)
    
    st.rerun()

# ========== FOOTER ==========
st.markdown("<div class='footer'>// DEVELOPED BY chyybenk // WITH GROQ & STREAMLIT</div>", unsafe_allow_html=True)