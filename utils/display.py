import streamlit as st

def layout_title_and_input():
    st.title("🇫🇷 Générateur de transitions françaises")
    st.markdown("Remplace chaque `TRANSITION` par une phrase de 5 mots sans répétition de mots.")
    return st.text_area("📝 Collez le texte contenant des `TRANSITION`", height=300)

def show_output(text):
    st.text_area("📝 Texte avec transitions :", text, height=300)

def show_warning_or_error(missing=False, not_enough=False):
    if missing:
        st.warning("Aucune balise `TRANSITION` trouvée.")
    if not_enough:
        st.error("Pas assez de transitions uniques. Ajoutez-en dans transitions.json.")

def show_version(version_hash):
    st.caption(f"🔄 Version de l'application : `{version_hash}`")
