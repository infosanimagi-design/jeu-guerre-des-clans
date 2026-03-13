import streamlit as st
import google.generativeai as genai

# --- CONFIGURATION ---
API_KEY = st.secrets["GOOGLE_API_KEY"]
genai.configure(api_key=API_KEY)

# --- LOOK & FEEL ---
st.set_page_config(page_title="La Guerre des Clans 2026", page_icon="🐾")
st.markdown("<style>.stApp { background-color: #0e1612; } .stMarkdown, p, h1 { color: #d1d1d1 !important; }</style>", unsafe_allow_html=True)

# --- FONCTION DE DÉTECTION DU MODÈLE ---
@st.cache_resource
def get_best_model():
    """Cherche le meilleur modèle Gemini 3 ou 2 disponible sur le compte."""
    try:
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        # Priorité aux modèles Gemini 3 que tu as vus dans ton Studio
        for preferred in ["models/gemini-3-flash-preview", "models/gemini-3-flash", "models/gemini-2.0-flash"]:
            if preferred in available_models:
                return preferred
        return available_models[0] # Au pire, prend le premier disponible
    except:
        return "gemini-1.5-flash" # Repli de secours

MODEL_ID = get_best_model()

st.title(f"🐾 L'Aventure des Clans")
st.caption(f"Propulsé par le moteur : {MODEL_ID.split('/')[-1]}")

# --- PROMPT IMMERSIF ---
SYSTEM_PROMPT = """Tu es le Maître de Jeu expert de "La Guerre des Clans".
Joueuse : Enfant de 10 ans. 
Ton style est ultra-immersif (odeurs, sons, météo).
INTERDICTION : Ne jamais décrire les actions/pensées du personnage de la joueuse.
Lexique obligatoire : Lunes, Bipèdes, Monstres, Chemin de Tonnerre."""

# --- INITIALISATION ---
if "chat" not in st.session_state:
    model = genai.GenerativeModel(MODEL_ID, system_instruction=SYSTEM_PROMPT)
    st.session_state.chat = model.start_chat(history=[])
    st.session_state.messages = []

# Affichage des messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Entrée de la joueuse
if prompt := st.chat_input("Que fait ton chat ?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            response = st.session_state.chat.send_message(prompt)
            st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
        except Exception as e:
            st.error(f"Le Clan des Étoiles est troublé... Erreur : {e}")
