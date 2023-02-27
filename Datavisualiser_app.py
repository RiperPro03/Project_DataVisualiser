import streamlit as st
import pandas as pd
from streamlit_option_menu import option_menu
import json
import plotly.express as px
import plotly.graph_objects as go
import requests

from json import JSONDecodeError
from model import MongoConnection, Essai, Intervention, Publication

# ---------- SETTING ----------
app_name = "DataVisualizer"
app_icon = ":bar_chart:"  # https://www.webfx.com/tools/emoji-cheat-sheet/
pages = {
    "page_1": {'name': 'Tableau de bord', 'icon': 'house'},  # https://icons.getbootstrap.com/
    "page_2": {'name': 'Statistique', 'icon': 'bi-graph-up-arrow'},
    "page_3": {'name': 'Corpus', 'icon': 'bi-card-text'},
    "page_4": {'name': 'Import', 'icon': 'cloud-upload'},
    "page_5": {'name': 'TEST', 'icon': 'bi-tools'},
}
liste_noms_pages = [pages[page]['name'] for page in pages]
liste_icons_pages = [pages[page]['icon'] for page in pages]

st.set_page_config(page_title=app_name, page_icon=app_icon, layout="wide",
                   initial_sidebar_state="expanded")

with st.spinner('Connexion à la base de données en cours...'):
    try:
        db = MongoConnection.getInstance()
        collection_Essai = db['Essai']
        collection_Publication = db['Publication']
    except Exception as e:
        st.error("Erreur lors de la connexion à la base de données.")
        st.exception(e)
        st.stop()


# ---------- FONCTION ----------
@st.cache_data(show_spinner=False)
def getDf_essai():
    return pd.DataFrame(list(collection_Essai.find({}, {'interventions': 0})))


@st.cache_data(show_spinner=False)
def getDf_publication():
    return pd.DataFrame(list(collection_Publication.find()))


@st.cache_data(show_spinner=False)
def getDf_intervention():
    interventions = collection_Essai.find({'interventions': {'$ne': None}}, {'_id': 0, 'interventions': 1})
    Liste_intervention = [Intervention(inter['name'],
                                       inter['description'],
                                       inter['other_names'],
                                       inter['arm_group_labels'],
                                       inter['type'])
                          for i in interventions for inter in i['interventions']]
    return pd.DataFrame(inter.getDict() for inter in Liste_intervention)


def insert_objects_to_mongoDB(liste_objets, collection):
    if liste_objets:
        # Convertir la liste d'objets en liste de dictionnaires
        list_obj_dicts = [objet.getDict() for objet in liste_objets]
        # Envoi des données à la BD
        collection.insert_many(list_obj_dicts)
        return True
    else:
        return False


def get_obs_rand_values(id, df_obs_ids, df_rand_ids):
    obs_value, rand_value = 0, 0

    if id in df_obs_ids:
        obs_value = 1
    if id in df_rand_ids:
        rand_value = 1

    return obs_value, rand_value


def clean_dataframe(dataframe):
    dataframe = dataframe.loc[dataframe['id'].str.len() < 30]
    dataframe = dataframe.dropna(subset=['date'])
    dataframe['phase'] = dataframe['phase'].astype(str)
    return dataframe


def remove_duplicate_rows(df_merged, df_bd, id_column):
    if not df_bd.empty:
        df_traiter = df_merged[~df_merged[id_column].isin(df_bd['_id'])]
    else:
        df_traiter = df_merged
    return df_traiter


# ---------- SIDEBAR ----------
with open('style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
st.sidebar.markdown("---")

with st.sidebar:
    selected = option_menu(None, liste_noms_pages,
                           icons=liste_icons_pages,
                           menu_icon="cast", default_index=0)
if selected == pages['page_1']['name']:
    st.sidebar.markdown('''---''')
    st.sidebar.title(selected)
    st.sidebar.markdown('''---''')
elif selected == pages['page_2']['name']:
    st.sidebar.markdown('''---''')
    st.sidebar.title(selected)
    st.sidebar.markdown('''---''')
elif selected == pages['page_3']['name']:
    st.sidebar.markdown('''---''')
    st.sidebar.title(selected)
    st.sidebar.markdown('''---''')
elif selected == pages['page_4']['name']:
    st.sidebar.markdown('''---''')
    st.sidebar.title(selected)
    st.sidebar.markdown('''---''')
elif selected == pages['page_5']['name']:
    st.sidebar.markdown('''---''')
    st.sidebar.title(selected)
    st.sidebar.markdown('''---''')

if st.sidebar.button('Recharger les données'):
    st.cache_data.clear()
st.sidebar.markdown('''
---
Created with ❤️ by [Christopher ASIN](https://github.com/RiperPro03).
''')

# ---------- ACCEUIL ----------
if selected == pages['page_1']['name']:
    st.title(selected)
    with st.spinner('Chargement des données en cours...'):
        # Récupération des essais
        df_essai = getDf_essai()
        nb_essai = len(df_essai)

        # Récupération des interventions
        df_intervention = getDf_intervention()
        nb_intervention = len(df_intervention)

        # Récupération des publications
        nb_publication = collection_Publication.count_documents({})

    col1, col2, col3 = st.columns(3)
    col1.metric("Nombre d'essai", nb_essai)
    col2.metric("Nombre d'intervention", nb_intervention)
    col3.metric("Nombre de publication", nb_publication)

    labels = df_essai['registry'].drop_duplicates()
    values = [len(df_essai[df_essai['registry'] == label]) for label in labels]
    fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=.3)])
    fig.update_traces(textposition='inside')
    cont = st.container()
    cont.header("Répartition des essais par registre")
    cont.plotly_chart(fig)


# ---------- STATISTIQUE ---------
elif selected == pages['page_2']['name']:
    st.title(selected)
    with st.spinner('Chargement des données en cours...'):
        # Récupération des essais
        df_essai = getDf_essai()
        nb_essai = len(df_essai)

        # Récupération des interventions
        df_intervention = getDf_intervention()
        nb_intervention = len(df_intervention)

    tab1, tab2 = st.tabs(["📈 Chart", "🗃 Data"])
    tab1.plotly_chart(px.histogram(df_essai, x="dateInserted", color="registry", title="Nombre d'essais par jour"))
    tab2.dataframe(df_essai['dateInserted'].value_counts())

    st.line_chart(df_essai['dateInserted'].value_counts())
    st.area_chart(df_intervention['type'].value_counts())

# ---------- TABLE ---------------
elif selected == pages['page_3']['name']:
    st.title(selected)

    with st.spinner('Chargement des données en cours...'):
        # Récupération des essais
        df_essai = getDf_essai()
        nb_essai = len(df_essai)

        # Récupération des interventions
        df_intervention = getDf_intervention()
        nb_intervention = len(df_intervention)

    st.header("Essai")
    st.dataframe(df_essai)

    st.header("Intervention")
    st.dataframe(df_intervention)

# ---------- IMPORT --------------
elif selected == pages['page_4']['name']:
    st.title(selected)

    file = st.file_uploader("Upload un fichier Excel", type="xlsx")

    if file is not None:
        with st.spinner('Traitement des données en cours...'):
            try:
                progression_bar = st.progress(0)

                # Recuperer les données excel des Essai et Publications
                df_obs_essai = pd.read_excel(file, sheet_name='1 - ClinicalTrials_ObsStudies')
                df_rand_essai = pd.read_excel(file, sheet_name='2 - ClinicalTrials_RandTrials')
                df_obs_pub = pd.read_excel(file, sheet_name='3 - Publications_ObsStudies')
                df_rand_pub = pd.read_excel(file, sheet_name='4 - Publications_RandTrials')

                progression_bar.progress(10)

                # Nettoyer les deux DataFrames
                df_obs_essai = clean_dataframe(df_obs_essai)
                df_rand_essai = clean_dataframe(df_rand_essai)
                df_obs_pub = df_obs_pub.loc[df_obs_pub['id'].str.len() < 30]
                df_rand_pub = df_rand_pub.loc[df_rand_pub['id'].str.len() < 30]

                progression_bar.progress(20)

                # Concaténer les deux DataFrames et supprimer les lignes en double
                df_essai_merged = pd.concat([df_obs_essai, df_rand_essai]).drop_duplicates()
                df_pub_merged = pd.concat([df_obs_pub, df_rand_pub]).drop_duplicates(subset=['id'], keep='first')

                progression_bar.progress(30)

                # transformer la colonne conditions en liste
                df_essai_merged['conditions'] = df_essai_merged['conditions'].str.split(' • ')
                df_pub_merged['openAccess'] = df_pub_merged['openAccess'].str.split(' • ')
                df_pub_merged['concepts'] = df_pub_merged['concepts'].str.split(' • ')
                df_pub_merged['meshTerms'] = df_pub_merged['meshTerms'].str.split(' • ')

                progression_bar.progress(40)

                # Recuperer la collection Essai sur MongoDB
                df_bd_essai = pd.DataFrame(list(collection_Essai.find()))
                # Recuperer la collection Publication sur MongoDB
                df_bd_pub = pd.DataFrame(list(db['Publication'].find()))

                progression_bar.progress(50)

                # Supprimer les lignes en double
                df_traiter_essai = remove_duplicate_rows(df_essai_merged, df_bd_essai, 'id')
                # DataFrame des essais à supprimer
                if not df_bd_essai.empty:
                    df_drop_essai = df_bd_essai[~df_bd_essai['_id'].isin(df_essai_merged['id'])]

                # Supprimer les lignes en double
                df_traiter_pub = remove_duplicate_rows(df_pub_merged, df_bd_pub, 'id')
                # DataFrame des publications à supprimer
                if not df_bd_pub.empty:
                    df_drop_pub = df_bd_pub[~df_bd_pub['_id'].isin(df_pub_merged['id'])]

                progression_bar.progress(55)

                liste_essai = []
                # Créeation d'objet Essai puis ajouter dans la liste
                for index, row in df_traiter_essai.iterrows():
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
                    obs_value, rand_value = get_obs_rand_values(row['id'], obs_essai_ids, rand_essai_ids)

                    # Ajouter l'objet Essai dans la liste
                    liste_essai.append(
                        Essai(row['id'], row['registry'], row['dateInserted'], row['date'], row['linkout'],
                              row['gender'], row['conditions'], row['acronym'], row['title'],
                              row['abstract'],
                              row['phase'], obs_value, rand_value, interventions_list))

                progression_bar.progress(65)

                liste_publication = []
                for i, row in df_traiter_pub.iterrows():
                    # Récupérer les id des publications observatifs et randomisés
                    obs_pub_ids = set(df_obs_pub['id'].values)
                    rand_pub_ids = set(df_rand_pub['id'].values)

                    # Vérifier si la publication est dans les publications observatifs et/ou randomisés
                    obs_value, rand_value = get_obs_rand_values(row['id'], obs_pub_ids, rand_pub_ids)

                    # Récupérer les métadonnées de la publication
                    doi = row['doi']
                    url = f'https://api.crossref.org/works/{doi}'
                    response = requests.get(url)

                    if response.status_code == 200:
                        data = json.loads(response.text)
                        print(data)
                    else:
                        print('Erreur : impossible de récupérer les métadonnées de la publication')

                    # Ajouter l'objet Publication dans la liste
                    liste_publication.append(
                        Publication(row['id'], row['dateInserted'], row['datePublished'], ['doctype'], row['doi'],
                                    row['pmid'], row['linkout'], row['timesCited'], row['altmetric'], row['venue'],
                                    row['publisher'], row['title'], row['openAccess'], row['concepts'],
                                    row['meshTerms'], obs_value, rand_value, 0))

                progression_bar.progress(75)

                # Envoi des essais à MongoDB
                statut_essai = insert_objects_to_mongoDB(liste_essai, collection_Essai)
                # Envoi des publications à MongoDB
                statut_pub = insert_objects_to_mongoDB(liste_publication, collection_Publication)

                # Supprimer les essais et publications de MongoDB
                if not df_drop_essai.empty:
                    collection_Essai.delete_many({'_id': {'$in': list(df_drop_essai['_id'].values)}})
                    st.write("Nombre d'essai qui a été supprimer de la base de données : ", len(df_drop_essai))
                    st.dataframe(df_drop_essai)
                    st.cache_data.clear()
                if not df_drop_pub.empty:
                    collection_Publication.delete_many({'_id': {'$in': list(df_drop_pub['_id'].values)}})
                    st.write("Nombre de publication qui a été supprimer de la base de données : ", len(df_drop_pub))
                    st.dataframe(df_drop_pub)
                    st.cache_data.clear()

                progression_bar.progress(100)

            except Exception as e:
                st.error("Une erreur est survenue lors de l'importation des données")
                st.exception(e)
                st.stop()

        if not statut_essai and not statut_pub:
            st.warning("Toutes les données ont déjà été importées")
        elif statut_essai and statut_pub:
            st.success("Les données ont été importées avec succès")
            st.write("Nombre d'essais importés: " + str(len(liste_essai)))
            st.write(df_traiter_essai)
            st.write("Nombre de publications importées: " + str(len(liste_publication)))
            st.write(df_traiter_pub)
            st.cache_data.clear()
        elif statut_essai:
            st.success("Les essais ont été importés avec succès")
            st.write("Nombre d'essais importés: " + str(len(liste_essai)))
            st.write(df_traiter_essai)
            st.cache_data.clear()
        elif statut_pub:
            st.success("Les publications ont été importées avec succès")
            st.write("Nombre de publications importées: " + str(len(liste_publication)))
            st.write(df_traiter_pub)
            st.cache_data.clear()

# ---------- TEST -----------
elif selected == pages['page_5']['name']:
    st.title(selected)

    doi = st.text_input('Entrer un DOI')
    if doi:
        url = f'https://api.crossref.org/works/{doi}'
        response = requests.get(url)

        if response.status_code == 200:
            data = json.loads(response.text)
            st.json(data)
        else:
            st.error('Erreur : impossible de récupérer les métadonnées de la publication')
