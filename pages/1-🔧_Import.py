import streamlit as st
import pandas as pd
import json

from json import JSONDecodeError
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
        try:
            db = MongoConnection.getInstance()
        except Exception as e:
            st.error("Une erreur est survenue lors de la connexion à la base de données")

        try:
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
                # Récupérer les id des essais observatifs et randomisés
                obs_essai_ids = set(df_obs_essai['id'].values)
                rand_essai_ids = set(df_rand_essai['id'].values)
                # Vérifier si l'essai est dans les essais observatifs et/ou randomisés
                if row['id'] in obs_essai_ids and row['id'] in rand_essai_ids:
                    obs_value, rand_value = 1, 1
                elif row['id'] in obs_essai_ids:
                    obs_value, rand_value = 1, 0
                elif row['id'] in rand_essai_ids:
                    obs_value, rand_value = 0, 1
                else:
                    obs_value, rand_value = 0, 0
                # Ajouter l'objet Essai dans la liste
                liste_essai.append(Essai(row['id'], row['registry'], row['dateInserted'], row['date'], row['linkout'],
                                         row['gender'], row['conditions'], row['acronym'], row['title'],
                                         row['abstract'],
                                         row['phase'], obs_value, rand_value, interventions_list))

            # Envoi des essais à MongoDB
            if liste_essai:
                # Convertir la liste d'objets Essai en liste de dictionnaires
                list_essai_dicts = [essai.getDict() for essai in liste_essai]
                # Envoi des données à la BD
                collection_Essai.insert_many(list_essai_dicts)

            statut = True
        except Exception as e:
            st.error("Une erreur est survenue lors de l'importation des données")
            statut = False

    if statut:
        if df_traiter.empty:
            st.warning("Toutes les données ont déjà été importées")
        else:
            st.success("Les données ont été importées avec succès")
            st.write("Nombre d'essais importés: " + str(len(liste_essai)))
            st.write(df_traiter)
