import streamlit as st
import google.generativeai as genai

# --- CONFIGURATION DE LA CLÉ ---
API_KEY = st.secrets["GOOGLE_API_KEY"]
genai.configure(api_key=API_KEY)

# --- DESIGN : AMBIANCE FORÊT ---
st.set_page_config(page_title="La Guerre des Clans", page_icon="🐾")

st.markdown("""
    <style>
    /* Changer la couleur de fond de toute l'application */
    .stApp {
        background-color: #1e2d24; /* Un vert forêt très foncé */
    }
    
    /* Changer la couleur du texte pour qu'il soit lisible */
    .stMarkdown, p, h1 {
        color: #e0e0e0 !important;
    }
    
    /* Personnaliser les bulles de chat */
    [data-testid="stChatMessage"] {
        background-color: #2d3e33;
        border-radius: 15px;
        border: 1px solid #3d5a45;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🐾 La Guerre des Clans : L'Aventure")

# --- LE CERVEAU DU MJ ---
SYSTEM_PROMPT = """Tu es un auteur de génie et le Maître de Jeu expert de l'univers "La Guerre des Clans" (Warriors). 
Ton objectif est de faire vivre une épopée inoubliable à une enfant de 10 ans.

CONNAISSANCES DE L'UNIVERS :
- Tu connais les 5 Clans, le Code du Guerrier et le Clan des Étoiles.
- Le temps passe en "Lunes" et les saisons sont : Saison des Feuilles Vertes, Feuilles Mortes, Cycle des Neiges, Nouvelles Feuilles.

STYLE DE NARRATION SENSORIEL :
- Ne dis pas "Tu es dans la forêt". Dis "L'odeur de l'humus humide chatouille tes narines et tu entends le bruissement d'un campagnol sous les ronces".
- RÈGLE D'OR : Tu ne décris JAMAIS ce que le chat de la joueuse dit, fait ou pense. Tu t'arrêtes JUSTE AVANT qu'elle n'agisse.
- TERMINOLOGIE : Bipèdes, Monstres, Chemin de Tonnerre, Pelage, Museau, Papattes.

DÉROULEMENT :
- Si c'est le début, demande son Nom, son Clan et son Apparence.
- Ensuite, lance une intrigue immédiate et immersive.
- Finis toujours par une situation qui demande une action de sa part."""

# --- INITIALISATION DU CHAT ---
if "chat" not in st.session_state:
    # Note : On ajoute models/ devant pour éviter l'erreur NotFound
    model = genai.GenerativeModel("models/gemini-1.5-pro", system_instruction=SYSTEM_PROMPT)
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
            st.error(f"Oups ! Le Clan des Étoiles est silencieux... (Erreur : {e})")
