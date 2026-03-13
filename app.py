import streamlit as st
import google.generativeai as genai

# --- CONFIGURATION (Gardons ton auto-détecteur qui fonctionne) ---
API_KEY = st.secrets["GOOGLE_API_KEY"]
genai.configure(api_key=API_KEY)

st.set_page_config(page_title="La Guerre des Clans", page_icon="🐾")
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

st.title("🐾 La Guerre des Clans")
st.caption(f"Moteur : {MODEL_ID.split('/')[-1]}")

# --- NOUVEAU PROMPT AVEC PHASE DE CRÉATION ---
SYSTEM_PROMPT = """Tu es le Maître de Jeu (MJ) du jeu de rôle "La Guerre des Clans".
Ta joueuse est une enfant de 10 ans. 

ÉTAPE 1 : LA CRÉATION (OBLIGATOIRE)
Au tout début, tu dois saluer la joueuse et lui demander de définir son chat :
- Son nom (ex: Nuage de...)
- Son âge (en lunes : un chaton a moins de 6 lunes, un apprenti entre 6 et 12, un guerrier plus de 12)
- Son sexe (mâle ou femelle)
- Son Clan (Tonnerre, Ombre, Vent, Rivière, Ciel ou même un chat errant)
- Sa description physique (couleur du pelage, des yeux)

ATTENTION : Ne commence JAMAIS l'histoire avant que ces éléments ne soient clairs. Une fois les infos reçues, résume son personnage et demande-lui si elle est prête à commencer.

ÉTAPE 2 : LA NARRATION
Une fois l'histoire commencée :
- Utilise un style sensoriel (odeurs, sons de la forêt).
- RÈGLE D'OR : Ne décris JAMAIS les actions, paroles ou pensées de la joueuse.
- Lexique : Lunes, Bipèdes, Monstres, Chemin de Tonnerre.
- Termine toujours par une situation qui demande une réaction."""

if "chat" not in st.session_state:
    model = genai.GenerativeModel(MODEL_ID, system_instruction=SYSTEM_PROMPT)
    st.session_state.chat = model.start_chat(history=[])
    st.session_state.messages = []
    # On force un premier message de bienvenue
    welcome_msg = "Bienvenue dans la forêt ! Avant de commencer ton aventure, nous devons créer ton personnage. Quel est ton nom de chat, ton âge, ton sexe, ton Clan et à quoi ressembles-tu ?"
    st.session_state.messages.append({"role": "assistant", "content": welcome_msg})

# Affichage des messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Entrée de la joueuse
if prompt := st.chat_input("Réponds ici..."):
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
