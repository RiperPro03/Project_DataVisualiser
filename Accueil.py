import streamlit as st
import pandas as pd

from model import MongoConnection

# ---------- SETTING ----------
app_name = "DataVisualizer"
app_icon = ":bar_chart:"  # https://www.webfx.com/tools/emoji-cheat-sheet/
page_tile = "Accueil"
page_icon = ":house:"

st.set_page_config(page_title=page_tile + " | " + app_name, page_icon=app_icon, layout="wide",
                   initial_sidebar_state="expanded")
# -----------------------------

# ---------- SIDEBAR ----------
st.sidebar.header(app_name + " " + app_icon)


st.sidebar.markdown('''
---
Created with ❤️ by [Christopher ASIN](https://github.com/RiperPro03).
''')
# -----------------------------

# ---------- MAIN ----------
st.title(page_tile)
with st.spinner('Chargement des données en cours...'):
    db = MongoConnection.getInstance()
    collection_Essai = db['Essai']
    df = pd.DataFrame(list(collection_Essai.find({}, {'interventions': 0}).limit(10)))
    st.write(df)
