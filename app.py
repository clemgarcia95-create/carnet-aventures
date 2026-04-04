import streamlit as st
from st_supabase_connection import SupabaseConnection
import random

# ==========================================
# 1. CONFIGURATION & CLÉS (À REMPLIR)
# ==========================================
# Colle tes infos entre les guillemets ci-dessous :
SUPABASE_URL = "https://undrmzgxabrhleodjqzn.supabase.co"
SUPABASE_KEY = "sb_publishable_sQojFj2F-6V1a6Z675Pa3Q_MQrMrtT6"
MOT_DE_PASSE_SECRET = "Amour" # Tu peux le changer si tu veux

st.set_page_config(page_title="Notre Carnet d'Aventures", page_icon="💖", layout="centered")

# ==========================================
# 2. CONNEXION BDD
# ==========================================
@st.cache_resource
def init_connection():
    return st.connection("supabase", type=SupabaseConnection, url=SUPABASE_URL, key=SUPABASE_KEY)

conn = init_connection()

def get_data():
    # Correction de la syntaxe de lecture
    response = conn.table("carnet_aventures").select("*").execute()
    return response.data

# ==========================================
# 3. SÉCURITÉ (LOGIN)
# ==========================================
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("🔐 Accès Privé")
    pwd = st.text_input("Entrez le mot de passe pour voir nos aventures :", type="password")
    if st.button("Se connecter"):
        if pwd == MOT_DE_PASSE_SECRET:
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("Mot de passe incorrect ❌")
    st.stop()

# ==========================================
# 4. RÉCUPÉRATION DES DONNÉES
# ==========================================
data = get_data()
envies = [d for d in data if not d['statut_fait']]
souvenirs = [d for d in data if d['statut_fait']]

# ==========================================
# 5. INTERFACE ET DESIGN
# ==========================================
st.markdown("<h1 style='text-align: center;'>💖 Notre Carnet d'Aventures</h1>", unsafe_allow_html=True)

# Barre de progression
total = len(data)
realise = len(souvenirs)
progres = realise / total if total > 0 else 0
st.progress(progres, text=f"Nos rêves réalisés : {realise}/{total} ({int(progres*100)}%) ✨")

tab1, tab2 = st.tabs(["🎯 Nos Envies", "📸 Nos Souvenirs"])

with tab1:
    # Formulaire d'ajout
    with st.expander("+ Ajouter une nouvelle envie"):
        with st.form("add_form"):
            titre = st.text_input("Qu'est-ce qui te ferait plaisir ?")
            cat = st.selectbox("Catégorie", ["Voyage ✈️", "Food 🍕", "Maison 🏠", "Sorties 🎭", "Folie 🤪"])
            qui = st.selectbox("Proposé par", ["Joanna 🌸", "Clément 🦊"])
            
            if st.form_submit_button("Ajouter à notre liste ✨"):
                if titre:
                    try:
                        conn.table("carnet_aventures").insert({
                            "titre": titre,
                            "categorie": cat,
                            "auteur": qui,
                            "statut_fait": False
                        }).execute()
                        st.success("C'est noté ! ❤️")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Erreur : {e}")
                else:
                    st.warning("Donne un petit nom à cette envie ! :)")

    # Bouton Surprise
    if envies:
        if st.button("🎲 Surprise-nous !"):
            choix = random.choice(envies)
            st.balloons()
            st.info(f"L'aventure du jour sera : **{choix['titre']}** ({choix['categorie']})")

    # Affichage des cartes
    st.divider()
    if not envies:
        st.write("La liste est vide, ajoutez vite des idées ! 🚀")
    else:
        for item in envies:
            with st.container():
                col1, col2 = st.columns([4, 1])
                col1.write(f"**{item['titre']}** \n*{item['categorie']} - Par {item['auteur']}*")
                if col2.button("Fait ! ✅", key=item['id']):
                    note = st.text_area("Un petit mot sur ce souvenir ?", key=f"note_{item['id']}")
                    if st.button("Valider le souvenir 📸", key=f"val_{item['id']}"):
                        conn.table("carnet_aventures").update({
                            "statut_fait": True,
                            "note_souvenir": note
                        }).eq("id", item['id']).execute()
                        st.rerun()

with tab2:
    if not souvenirs:
        st.write("Pas encore de souvenirs... Allons en créer ! 🏃‍♂️🏃‍♀️")
    else:
        for s in souvenirs:
            st.success(f"**{s['titre']}** \n{s['note_souvenir'] if s['note_souvenir'] else 'Pas de note.'}")
