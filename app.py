import streamlit as st
import google.generativeai as genai
import json

# --- CONFIGURATION ---
API_KEY = st.secrets["GOOGLE_API_KEY"]
genai.configure(api_key=API_KEY)

st.set_page_config(page_title="La Guerre des Clans", page_icon="🐾")

# --- DESIGN ---
st.markdown("<style>.stApp { background-color: #0e1612; } .stMarkdown, p, h1 { color: #d1d1d1 !important; }</style>", unsafe_allow_html=True)

@st.cache_resource
def get_best_model():
    try:
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        for preferred in ["models/gemini-3-flash-preview", "models/gemini-3-flash", "models/gemini-2.0-flash"]:
            if preferred in available_models: return preferred
        return available_models[0]
    except: return "gemini-1.5-flash"

MODEL_ID = get_best_model()

# --- BARRE LATÉRALE (SIDEBAR) ---
st.sidebar.title("🐾 Options du Jeu")

# Bouton pour recommencer
if st.sidebar.button("🗑️ Recommencer à zéro"):
    st.session_state.clear()
    st.rerun()

st.sidebar.divider()

# --- SYSTÈME DE SAUVEGARDE ---
st.sidebar.subheader("💾 Sauvegarde")

# Préparation du fichier de sauvegarde
if "messages" in st.session_state and len(st.session_state.messages) > 1:
    # On prépare un dictionnaire avec l'historique
    save_data = {
        "history": st.session_state.messages
    }
    json_save = json.dumps(save_data, ensure_ascii=False)
    
    st.sidebar.download_button(
        label="📥 Télécharger ma partie",
        data=json_save,
        file_name="mon_aventure_chat.json",
        mime="application/json"
    )

st.sidebar.divider()

# --- SYSTÈME DE CHARGEMENT ---
st.sidebar.subheader("📂 Charger une partie")
uploaded_file = st.sidebar.file_uploader("Choisis ton fichier .json", type="json")

if uploaded_file is not None:
    if st.sidebar.button("✨ Reprendre l'aventure"):
        data = json.load(uploaded_file)
        st.session_state.messages = data["history"]
        # On recrée le chat avec l'historique chargé
        model = genai.GenerativeModel(MODEL_ID, system_instruction=st.session_state.sys_prompt)
        # On convertit le format pour l'API
        api_history = []
        for msg in st.session_state.messages:
            role = "user" if msg["role"] == "user" else "model"
            api_history.append({"role": role, "parts": [msg["content"]]})
        
        st.session_state.chat = model.start_chat(history=api_history[:-1])
        st.rerun()

# --- LOGIQUE DU JEU ---
st.title("🐾 La Guerre des Clans")

SYSTEM_PROMPT = """Tu es le MJ de La Guerre des Clans. 
- Phase 1 : Crée le perso (Nom, âge, sexe, Clan, apparence).
- Phase 2 : Narration immersive sans jamais parler à la place du joueur.
- Utilise le lexique des livres."""

if "sys_prompt" not in st.session_state:
    st.session_state.sys_prompt = SYSTEM_PROMPT

if "chat" not in st.session_state:
    model = genai.GenerativeModel(MODEL_ID, system_instruction=st.session_state.sys_prompt)
    st.session_state.chat = model.start_chat(history=[])
    st.session_state.messages = []
    welcome_msg = "Bienvenue dans la forêt ! Créons ton chat : nom, âge, sexe, Clan et apparence ?"
    st.session_state.messages.append({"role": "assistant", "content": welcome_msg})

# Affichage des messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Entrée de la joueuse
if prompt := st.chat_input("Que fais-tu ?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            response = st.session_state.chat.send_message(prompt)
            st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
        except Exception as e:
            st.error(f"Erreur : {e}")
