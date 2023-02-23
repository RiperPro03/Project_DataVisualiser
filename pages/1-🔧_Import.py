import streamlit as st
import pandas as pd
from json import JSONDecodeError
import json
import time

from model import MongoConnection, Essai

# ---------- SETTING ----------
app_name = "DataVisualizer"
app_icon = ":bar_chart:" # https://www.webfx.com/tools/emoji-cheat-sheet/
page_tile = "Import"
page_icon = ":wrench:"

st.set_page_config(page_title=app_name + " | " + page_tile, page_icon=app_icon, layout="wide",
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
st.title(page_icon + " " + page_tile)
file = st.file_uploader("Upload un fichier Excel", type="xlsx")


def clean_dataframe(df):
    df = df.loc[df['id'].str.len() < 30]
    df = df.dropna(subset=['date'])
    df['phase'] = df['phase'].astype(str)
    return df


if file is not None:
    with st.spinner('Traitement des données en cours...'):
        db = MongoConnection.getInstance()
        liste_essai = []
        # Recuperer les données excel des Essai et Publications
        df_obs_essai = pd.read_excel(file, sheet_name='1 - ClinicalTrials_ObsStudies')
        df_rand_essai = pd.read_excel(file, sheet_name='2 - ClinicalTrials_RandTrials')
        df_obs_pub = pd.read_excel(file, sheet_name='3 - Publications_ObsStudies')
        df_rand_pub = pd.read_excel(file, sheet_name='4 - Publications_RandTrials')
        # Nettoyer les deux DataFrames
        df_obs_essai = clean_dataframe(df_obs_essai)
        df_rand_essai = clean_dataframe(df_rand_essai)
        # Concaténer les deux DataFrames et supprimer les lignes en double
        df_merged = pd.concat([df_obs_essai, df_rand_essai])
        df_merged = df_merged.drop_duplicates()
        # transformer la colonne conditions en liste
        df_merged['conditions'] = df_merged['conditions'].str.split(' • ')

        # Recuperer la collection Essai sur MongoDB
        collection_Essai = db['Essai']
        df_bd = pd.DataFrame(list(collection_Essai.find()))

        # Supprimer les lignes en double
        if not df_bd.empty:
            df_traiter = df_merged[~df_merged['id'].isin(df_bd['_id'])]
        else:
            df_traiter = df_merged

        # Créeation d'objet Essai puis ajouter dans la liste
        for index, row in df_traiter.iterrows():
            if not row['interventions'] is None:
                try:
                    interventions_list = json.loads(
                        str(row['interventions']).replace("'", '"').replace("None", '"None"'))
                except JSONDecodeError:
                    interventions_list = None

            liste_essai.append(Essai(row['id'], row['registry'], row['dateInserted'], row['date'], row['linkout'],
                                     row['gender'], row['conditions'], row['acronym'], row['title'], row['abstract'],
                                     row['phase'], 0, 0, interventions_list))

        # Envoi des essais à MongoDB
        if liste_essai:
            # Convertir la liste d'objets Essai en liste de dictionnaires
            list_essai_dicts = [essai.getDict() for essai in liste_essai]
            # Envoi des données à la BD
            collection_Essai.insert_many(list_essai_dicts)

    if df_traiter.empty:
        st.warning("Toutes les données ont déjà été importées")
    else:
        st.success("Les données ont été importées avec succès")
        st.write("Nombre d'essais importés: " + str(len(liste_essai)))
        st.write(df_traiter)
