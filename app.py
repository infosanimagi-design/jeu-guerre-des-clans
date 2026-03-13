import streamlit as st
import google.generativeai as genai
import json

# --- 1. SÉCURITÉ : LE MOT DE PASSE ---
st.set_page_config(page_title="La Guerre des Clans - Sécurisé", page_icon="🐾")

# Crée un mot de passe simple pour protéger tes crédits
MOT_DE_PASSE_SECRET = "EtoileDeFeu2026" # <--- CHANGE CE MOT DE PASSE ICI

if "authentifie" not in st.session_state:
    st.session_state.authentifie = False

if not st.session_state.authentifie:
    st.title("Accès Restreint 🐾")
    mdp = st.text_input("Entre le mot de passe du Clan pour jouer :", type="password")
    if st.button("Se connecter"):
        if mdp == MOT_DE_PASSE_SECRET:
            st.session_state.authentifie = True
            st.rerun()
        else:
            st.error("Mot de passe incorrect. Le Clan des Étoiles te rejette.")
    st.stop() # Arrête l'exécution du reste du code si pas authentifié

# --- 2. CONFIGURATION API ---
API_KEY = st.secrets["GOOGLE_API_KEY"]
genai.configure(api_key=API_KEY)

@st.cache_resource
def get_best_model():
    try:
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        for preferred in ["models/gemini-3-flash-preview", "models/gemini-3-flash", "models/gemini-1.5-pro"]:
            if preferred in available_models: return preferred
        return available_models[0]
    except: return "gemini-1.5-flash"

MODEL_ID = get_best_model()

# --- 3. DESIGN ---
st.markdown("<style>.stApp { background-color: #0e1612; } .stMarkdown, p, h1 { color: #d1d1d1 !important; }</style>", unsafe_allow_html=True)

# --- 4. BARRE LATÉRALE (SAUVEGARDE & OPTIONS) ---
st.sidebar.title("🐾 Options du Guerrier")

# RÉPARER LA SAUVEGARDE : On prépare les données systématiquement
if "messages" not in st.session_state:
    st.session_state.messages = []

# Bouton de téléchargement (toujours présent si au moins 1 message existe)
if len(st.session_state.messages) > 0:
    data_to_save = json.dumps({"history": st.session_state.messages}, ensure_ascii=False)
    st.sidebar.download_button(
        label="💾 Sauvegarder ma partie",
        data=data_to_save,
        file_name="aventure_guerre_des_clans.json",
        mime="application/json"
    )

st.sidebar.divider()

# CHARGEMENT
uploaded_file = st.sidebar.file_uploader("📂 Charger une aventure", type="json")
if uploaded_file is not None:
    if st.sidebar.button("✨ Lancer le chargement"):
        content = json.load(uploaded_file)
        st.session_state.messages = content["history"]
        # Reconstruction de la session de chat technique
        model = genai.GenerativeModel(MODEL_ID)
        history_api = []
        for m in st.session_state.messages:
            role = "user" if m["role"] == "user" else "model"
            history_api.append({"role": role, "parts": [m["content"]]})
        st.session_state.chat = model.start_chat(history=history_api[:-1])
        st.rerun()

if st.sidebar.button("🗑️ Recommencer à zéro"):
    st.session_state.clear()
    st.rerun()

# --- 5. LOGIQUE DU JEU (PROMPT RENFORCÉ) ---
st.title("🐾 La Guerre des Clans")

# On redouble d'effort ici pour le comportement
REINFORCED_PROMPT = """Tu es le Narrateur STRICT de "La Guerre des Clans".
### INTERDICTION FORMELLE :
1. Tu ne dois JAMAIS écrire une seule action, parole ou pensée pour le personnage de la joueuse. 
2. Tu ne décris pas ses mouvements (ex: Ne dis pas "Tu marches vers..."). 
3. Tu décris uniquement ce qui arrive AUTOUR d'elle.
4. Si elle dit "Je saute", tu décris la branche qui craque ou le vent, mais tu ne finis pas son saut.

### MISSION :
- Pose les questions de création (Nom, âge, sexe, Clan, apparence) au début.
- Sois sensoriel et bref. Termine toujours par une situation bloquée qui attend son choix."""

if "chat" not in st.session_state:
    model = genai.GenerativeModel(MODEL_ID, system_instruction=REINFORCED_PROMPT)
    st.session_state.chat = model.start_chat(history=[])
    welcome = "Bienvenue, jeune chat. Le Clan des Étoiles attend de te connaître. Quel est ton nom, ton âge, ton sexe, ton Clan et ton apparence ?"
    st.session_state.messages = [{"role": "assistant", "content": welcome}]

# Affichage du chat
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Entrée utilisateur
if prompt := st.chat_input("Que fais-tu ?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            # On ajoute un rappel invisible à chaque message pour "forcer" l'IA à obéir
            full_prompt = prompt + " (Rappel : Ne parle jamais pour moi. Décris juste l'environnement et arrête-toi.)"
            response = st.session_state.chat.send_message(full_prompt)
            st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
        except Exception as e:
            st.error(f"Le lien est rompu : {e}")
