import streamlit as st
from st_supabase_connection import SupabaseConnection
import random
from datetime import datetime

# Configuration de la page (Mobile First)
st.set_page_config(page_title="Notre Carnet d'Aventures", page_icon="💖", layout="centered")

# ==========================================
# CONFIGURATION SUPABASE & SÉCURITÉ
# ==========================================
# Instructions :
# 1. Créez un projet sur Supabase (https://supabase.com)
# 2. Allez dans Project Settings -> API
# 3. Copiez l'URL et la clé 'anon' / 'public' ci-dessous :
SUPABASE_URL = "https://undrmzgxabrhleodjqzn.supabase.co"
SUPABASE_KEY = "sb_publishable_sQojFj2F-6V1a6Z675Pa3Q_MQrMrtT6"

APP_PASSWORD = "amour" # 🔒 Changez ce mot de passe !

# ==========================================
# STYLES CSS PERSONNALISÉS (Doux & Romantique)
# ==========================================
st.markdown("""
<style>
    /* Couleurs de fond et texte */
    .stApp {
        background-color: #FFFDF9;
        color: #5D4037;
    }
    /* Style des cartes */
    .idea-card {
        padding: 15px;
        border-radius: 15px;
        margin-bottom: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        border: 1px solid #F0E6D2;
    }
    .cat-Voyage { background-color: #E3F2FD; }
    .cat-Food { background-color: #FFF3E0; }
    .cat-Maison { background-color: #E8F5E9; }
    .cat-Sorties { background-color: #F3E5F5; }
    .cat-Folie { background-color: #FFEBEE; }
    
    .idea-title {
        font-size: 1.2rem;
        font-weight: bold;
        margin-bottom: 5px;
    }
    .idea-meta {
        font-size: 0.9rem;
        color: #8D6E63;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 1. PAGE D'ACCUEIL SÉCURISÉE
# ==========================================
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.markdown("<h1 style='text-align: center;'>🔒 Notre Carnet d'Aventures</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'>Entrez le mot de passe pour accéder à nos secrets...</p>", unsafe_allow_html=True)
    
    pwd = st.text_input("Mot de passe", type="password")
    if st.button("Déverrouiller 🗝️", use_container_width=True):
        if pwd == APP_PASSWORD:
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("Mot de passe incorrect 💔")
    st.stop()

# ==========================================
# CONNEXION SUPABASE
# ==========================================
@st.cache_resource
def init_connection():
    return st.connection("supabase", type=SupabaseConnection, url=SUPABASE_URL, key=SUPABASE_KEY)

# Sécurité pour éviter les erreurs si les clés ne sont pas encore configurées
if SUPABASE_URL == "VOTRE_SUPABASE_URL_ICI":
    st.warning("⚠️ Veuillez configurer SUPABASE_URL et SUPABASE_KEY dans le code (lignes 14-15).")
    st.stop()

conn = init_connection()

# Fonction pour récupérer les données
def get_data():
response = conn.table("carnet_aventures").select("*").execute()
    return response.data

data = get_data()
envies = [d for d in data if not d['statut_fait']]
souvenirs = [d for d in data if d['statut_fait']]

# ==========================================
# BARRE DE PROGRESSION
# ==========================================
st.markdown("<h2 style='text-align: center;'>💖 Notre Carnet d'Aventures</h2>", unsafe_allow_html=True)

total_ideas = len(data)
realized = len(souvenirs)
progress = realized / total_ideas if total_ideas > 0 else 0

st.progress(progress, text=f"Nos rêves réalisés : {realized}/{total_ideas} ({int(progress*100)}%) ✨")

# ==========================================
# 2. NAVIGATION (ONGLETS)
# ==========================================
tab_envies, tab_souvenirs = st.tabs(["💭 Nos Envies", "📸 Nos Souvenirs"])

with tab_envies:
    # ==========================================
    # 4. BOUTON SURPRISE
    # ==========================================
    if st.button("🎲 Surprise-nous !", use_container_width=True, type="primary"):
        if envies:
            surprise = random.choice(envies)
            st.balloons()
            st.success(f"🎉 **Idée piochée :** {surprise['titre']} ({surprise['catégorie']})")
        else:
            st.info("Ajoutez d'abord des envies ! 📝")

    # ==========================================
    # 3. AJOUT D'UNE IDÉE
    # ==========================================
    with st.expander("➕ Ajouter une nouvelle envie"):
        with st.form("form_add"):
            titre = st.text_input("Qu'est-ce qui te ferait plaisir ?")
            categorie = st.selectbox("Catégorie", ["Voyage ✈️", "Food 🍕", "Maison 🏡", "Sorties 🎭", "Folie 🤪"])
            auteur = st.selectbox("Proposé par", ["Joanna 🌸", "Clément 🦊"])
            
            if st.form_submit_button("Ajouter à notre liste ✨", use_container_width=True):
                if titre:
                    conn.table("carnet_aventures").insert({
                        "titre": titre,
                        "catégorie": categorie,
                        "auteur": auteur,
                        "statut_fait": False
                    }).execute()
                    st.success("Envie ajoutée ! 💖")
                    st.rerun()
                else:
                    st.error("N'oublie pas le titre !")

    st.divider()
    
    # AFFICHAGE DES ENVIES
    if not envies:
        st.info("Notre liste est vide. Ajoutons de nouveaux projets ! 🚀")
        
    for idea in envies:
        # Extraction du premier mot de la catégorie pour la classe CSS (ex: "Voyage ✈️" -> "Voyage")
        cat_class = idea['catégorie'].split(" ")[0]
        
        st.markdown(f"""
        <div class="idea-card cat-{cat_class}">
            <div class="idea-title">{idea['titre']}</div>
            <div class="idea-meta">{idea['catégorie']} • Proposé par {idea['auteur']}</div>
        </div>
        """, unsafe_allow_html=True)
        
        # ==========================================
        # 5. VALIDATION D'UN SOUVENIR
        # ==========================================
        col1, col2 = st.columns([1, 2])
        with col1:
            if st.button("✅ C'est fait !", key=f"btn_{idea['id']}"):
                st.session_state[f"valider_{idea['id']}"] = True
                
        if st.session_state.get(f"valider_{idea['id']}", False):
            note = st.text_area("Un petit mot sur ce souvenir ?", key=f"note_{idea['id']}")
            if st.button("Enregistrer le souvenir 💌", key=f"save_{idea['id']}"):
                conn.table("carnet_aventures").update({
                    "statut_fait": True,
                    "note_souvenir": note,
                    "date_réalisation": datetime.now().isoformat()
                }).eq("id", idea['id']).execute()
                st.session_state[f"valider_{idea['id']}"] = False
                st.rerun()

with tab_souvenirs:
    if not souvenirs:
        st.info("Pas encore de souvenirs... Il est temps de passer à l'action ! 🥰")
        
    # Trier les souvenirs par date de réalisation (du plus récent au plus ancien)
    souvenirs_tries = sorted(souvenirs, key=lambda x: x.get('date_réalisation') or '', reverse=True)
    
    for s in souvenirs_tries:
        date_str = s.get('date_réalisation')
        if date_str:
            try:
                # Formatage de la date
                date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                date_formatee = date_obj.strftime("%d/%m/%Y")
            except:
                date_formatee = date_str[:10]
        else:
            date_formatee = "Date inconnue"
            
        st.markdown(f"""
        <div class="idea-card" style="background-color: #FAFAFA;">
            <div class="idea-title">✨ {s['titre']}</div>
            <div class="idea-meta">Réalisé le {date_formatee} • {s['catégorie']}</div>
            <hr style="margin: 10px 0; border-top: 1px dashed #D7CCC8;">
            <div style="font-style: italic; color: #5D4037;">"{s['note_souvenir']}"</div>
        </div>
        """, unsafe_allow_html=True)
