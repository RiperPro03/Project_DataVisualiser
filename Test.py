import requests


def get_authors_from_doi(doi):
    url = f"https://api.crossref.org/works/{doi}"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        authors = data["message"]["author"]
        author_list = []

        for author in authors:
            full_name = f"{author['given']} {author['family']}"
            author_list.append(full_name)

        return author_list
    else:
        print(f"Erreur : Impossible de récupérer les informations pour le DOI {doi}")
        return None


# Remplacez "your_doi" par le DOI réel pour lequel vous souhaitez récupérer les auteurs.
your_doi = "10.23750/abm.v91i3-s.9419"
authors = get_authors_from_doi(your_doi)

if authors:
    print("Auteurs :")
    for author in authors:
        print(author)


# import re
# import time
# import os
# import requests
# from selenium import webdriver
# from PyPDF2 import PdfFileReader
# from io import BytesIO
#
# num_essai = 'NCT04346147'  # Remplacez ceci par le numéro d'essai que vous recherchez
# url = 'https://doi.org/10.1016/j.ijantimicag.2020.106028'  # Remplacez ceci par l'URL de la publication
#
#
# def scrapper_web(url, num_essai):
#     driver = webdriver.Chrome()  # Remplacez ceci par le webdriver de votre choix
#     driver.get(url)
#     time.sleep(5)
#
#     text = driver.page_source
#
#     driver.quit()
#
#     return re.search(num_essai, text) is not None
#
#
# def scrapper_pdf(url, num_essai):
#     response = requests.get(url)
#     response.raise_for_status()
#
#     with BytesIO(response.content) as pdf_data:
#         pdf_reader = PdfFileReader(pdf_data)
#         num_pages = pdf_reader.getNumPages()
#
#         for page in range(num_pages):
#             text = pdf_reader.getPage(page).extractText()
#             if re.search(num_essai, text):
#                 return True
#
#     return False
#
#
# if url.endswith('.pdf'):
#     trouve = scrapper_pdf(url, num_essai)
# else:
#     trouve = scrapper_web(url, num_essai)
#
# if trouve:
#     print(f'Le numéro d\'essai {num_essai} a été trouvé dans la publication.')
# else:
#     print(f'Le numéro d\'essai {num_essai} n\'a pas été trouvé dans la publication.')