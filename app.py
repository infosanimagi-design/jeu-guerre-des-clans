import streamlit as st
import google.generativeai as genai

# --- CONFIGURATION ---
# On récupère la clé de façon sécurisée via les "Secrets" de Streamlit
API_KEY = st.secrets["GOOGLE_API_KEY"]
genai.configure(api_key=API_KEY)

st.set_page_config(page_title="La Guerre des Clans", page_icon="🐾")
st.title("🐾 La Guerre des Clans : L'Aventure")

SYSTEM_PROMPT = """Tu es le Maître de Jeu (MJ) de La Guerre des Clans. 
RÈGLE D'OR : Ne jamais parler à la place du personnage de la joueuse.
Vocabulaire : Lunes, Bipèdes, Monstres.
Finis toujours par une question ou une situation qui demande une action."""

if "chat" not in st.session_state:
    model = genai.GenerativeModel("gemini-1.5-pro", system_instruction=SYSTEM_PROMPT)
    st.session_state.chat = model.start_chat(history=[])
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Que fait ton chat ?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        response = st.session_state.chat.send_message(prompt)
        st.markdown(response.text)
        st.session_state.messages.append({"role": "assistant", "content": response.text})
