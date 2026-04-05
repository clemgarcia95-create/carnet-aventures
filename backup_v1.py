import streamlit as st
from st_supabase_connection import SupabaseConnection
import random

# ==========================================
# 1. CONFIGURATION & CLÉS
# ==========================================
# REMPLACE PAR TES VRAIES CLÉS ICI :
SUPABASE_URL = "https://undrmzgxabrhleodjqzn.supabase.co"
SUPABASE_KEY = "sb_publishable_sQojFj2F-6V1a6Z675Pa3Q_MQrMrtT6"
MOT_DE_PASSE_SECRET = "Amour" 

st.set_page_config(page_title="Notre Carnet d'Aventures", page_icon="💖", layout="centered")

# Style CSS pour cacher les labels des boutons de suppression (plus esthétique)
st.markdown("""
    <style>
    .stButton button { border-radius: 20px; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. CONNEXION BDD
# ==========================================
@st.cache_resource
def init_connection():
    return st.connection("supabase", type=SupabaseConnection, url=SUPABASE_URL, key=SUPABASE_KEY)

conn = init_connection()

def get_data():
    response = conn.table("carnet_aventures").select("*").execute()
    return response.data

# ==========================================
# 3. SÉCURITÉ (LOGIN)
# ==========================================
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("🔐 Accès Privé")
    pwd = st.text_input("Mot de passe :", type="password")
    if st.button("Se connecter"):
        if pwd == MOT_DE_PASSE_SECRET:
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("Mot de passe incorrect ❌")
    st.stop()

# ==========================================
# 4. FONCTIONS DE GESTION (MODALES)
# ==========================================
@st.dialog("Enregistrer ce souvenir 📸")
def valider_souvenir(item_id, titre):
    st.write(f"Bravo pour avoir réalisé : **{titre}** !")
    note = st.text_area("Un petit mot sur ce moment ?")
    if st.button("Confirmer ✅"):
        conn.table("carnet_aventures").update({
            "statut_fait": True, 
            "note_souvenir": note
        }).eq("id", item_id).execute()
        st.success("Souvenir enregistré !")
        st.rerun()

@st.dialog("Supprimer l'élément ? 🗑️")
def confirmer_suppression(item_id, titre):
    st.warning(f"Veux-tu vraiment supprimer '**{titre}**' ?")
    st.write("Cette action est irréversible.")
    if st.button("Oui, supprimer définitivement", type="primary"):
        conn.table("carnet_aventures").delete().eq("id", item_id).execute()
        st.success("Supprimé !")
        st.rerun()

# ==========================================
# 5. RÉCUPÉRATION DES DONNÉES
# ==========================================
data = get_data()
# Tri par date de création (plus récent en haut)
data = sorted(data, key=lambda x: x['date_creation'], reverse=True)
envies = [d for d in data if not d['statut_fait']]
souvenirs = [d for d in data if d['statut_fait']]

# ==========================================
# 6. INTERFACE ET DESIGN
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
        with st.form("add_form", clear_on_submit=True):
            titre = st.text_input("Qu'est-ce qui te ferait plaisir ?")
            cat = st.selectbox("Catégorie", ["Voyage ✈️", "Food 🍕", "Maison 🏠", "Sorties 🎭", "Folie 🤪"])
            qui = st.selectbox("Proposé par", ["Joanna 🌸", "Clément 🦊"])
            
            if st.form_submit_button("Ajouter à notre liste ✨"):
                if titre:
                    conn.table("carnet_aventures").insert({
                        "titre": titre, "categorie": cat, "auteur": qui, "statut_fait": False
                    }).execute()
                    st.rerun()

    # Bouton Surprise
    if envies:
        if st.button("🎲 Surprise-nous !"):
            choix = random.choice(envies)
            st.balloons()
            st.info(f"L'aventure du jour : **{choix['titre']}**")

    st.divider()
    if not envies:
        st.info("La liste est vide ! 🚀")
    else:
        for item in envies:
            col1, col2, col3 = st.columns([3, 0.8, 0.5])
            col1.markdown(f"**{item['titre']}** \n*{item['categorie']} • {item['auteur']}*")
            if col2.button("Fait ! ✅", key=f"done_{item['id']}"):
                valider_souvenir(item['id'], item['titre'])
            if col3.button("🗑️", key=f"del_{item['id']}"):
                confirmer_suppression(item['id'], item['titre'])

with tab2:
    if not souvenirs:
        st.write("Pas encore de souvenirs... 🏃‍♂️")
    else:
        for s in souvenirs:
            with st.chat_message("user", avatar="✨"):
                col_a, col_b = st.columns([5, 1])
                with col_a:
                    st.write(f"**{s['titre']}**")
                    st.caption(f"Catégorie : {s['categorie']}")
                    if s['note_souvenir']:
                        st.info(s['note_souvenir'])
                with col_b:
                    if st.button("🗑️", key=f"del_souv_{s['id']}"):
                        confirmer_suppression(s['id'], s['titre'])
