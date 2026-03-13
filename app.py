import streamlit as st
import google.generativeai as genai

# --- CONFIGURATION ---
# On récupère la clé de façon sécurisée via les "Secrets" de Streamlit
API_KEY = st.secrets["GOOGLE_API_KEY"]
genai.configure(api_key=API_KEY)

st.set_page_config(page_title="La Guerre des Clans", page_icon="🐾")
st.title("🐾 La Guerre des Clans : L'Aventure")

SYSTEM_PROMPT = """Tu es un auteur de génie et le Maître de Jeu expert de l'univers "La Guerre des Clans" (Warriors). 
Ton objectif est de faire vivre une épopée inoubliable à une enfant de 10 ans.

CONNAISSANCES DE L'UNIVERS :
- Tu connais parfaitement les 4 Clans (Tonnerre, Ombre, Vent, Rivière) et le Clan des Étoiles.
- Tu respectes le Code du Guerrier.
- Le temps passe en "Lunes" (mois) et les saisons sont : la Saison des Feuilles Vertes (été), des Feuilles Mortes (automne), du Cycle des Neiges (hiver), et des Nouvelles Feuilles (printemps).

STYLE DE NARRATION (TRÈS IMPORTANT) :
1. SENSORIEL : Ne dis pas "Tu es dans la forêt". Dis "L'odeur de l'humus humide chatouille tes narines et tu entends le bruissement d'un campagnol sous les ronces".
2. RÈGLE D'OR : Tu ne décris JAMAIS ce que le chat de la joueuse dit, fait ou pense. Tu t'arrêtes juste au moment où son cœur bat vite, juste avant qu'elle ne décide de sauter.
3. TERMINOLOGIE : Utilise TOUJOURS : Bipèdes (humains), Monstres (voitures), Chemin de Tonnerre (route), Monstres d'Argent (avions), Pelage, Museau, Papattes.

DÉROULEMENT :
- Si l'histoire commence, demande d'abord : Son nom (Nuage de...), son Clan et la couleur de son pelage.
- Une fois le personnage créé, lance une intrigue : une patrouille à la frontière, une assemblée tendue, ou une proie rare à chasser.
- Termine chaque réponse par une question ouverte pour l'inciter à agir."""

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
