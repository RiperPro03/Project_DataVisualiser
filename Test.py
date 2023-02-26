import requests
import json

doi = '10.1093/gerona/glaa131'

url = f'https://api.crossref.org/works/{doi}'
response = requests.get(url)

if response.status_code == 200:
    data = json.loads(response.text)
    print(data)
else:
    print('Erreur : impossible de récupérer les métadonnées de la publication')