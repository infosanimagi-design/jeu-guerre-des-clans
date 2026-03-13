import streamlit as st
import google.generativeai as genai

# --- CONFIGURATION ---
API_KEY = st.secrets["GOOGLE_API_KEY"]
genai.configure(api_key=API_KEY)

# --- LOOK & FEEL ---
st.set_page_config(page_title="La Guerre des Clans", page_icon="🐾")

st.markdown("""
    <style>
    .stApp { background-color: #0e1612; }
    .stMarkdown, p, h1 { color: #d1d1d1 !important; }
    [data-testid="stChatMessage"] {
        background-color: #1a261f;
        border-radius: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🐾 La Guerre des Clans")

# --- LE PROMPT (Cerveau du jeu) ---
SYSTEM_PROMPT = """Tu es le MJ expert de La Guerre des Clans. 
- Joueuse : Enfant de 10 ans. 
- Style : Immersif, sensoriel, respecte le lexique des livres.
- RÈGLE D'OR : Ne décris JAMAIS les actions ou paroles de la joueuse.
- Finis par une situation qui demande une action."""

# --- INITIALISATION ---
if "chat" not in st.session_state:
    # On utilise ici le modèle STANDARD le plus robuste
    # Si tu veux tester le plus puissant, remplace par "gemini-1.5-pro"
    model = genai.GenerativeModel("gemini-1.5-flash", system_instruction=SYSTEM_PROMPT)
    st.session_state.chat = model.start_chat(history=[])
    st.session_state.messages = []

# Affichage
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Interaction
if prompt := st.chat_input("Que fait ton chat ?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            # Envoi du message au modèle standard
            response = st.session_state.chat.send_message(prompt)
            st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
        except Exception as e:
            st.error(f"Erreur de connexion : {e}")
