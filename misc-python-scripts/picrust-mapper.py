import pandas as pd
import requests

BIOCYC_API_URL = "https://websvc.biocyc.org/getpathway"

def fetch_metacyc_info(pathway_id):
    try:
        params = {"pw": pathway_id, "fmt": "json"}
        response = requests.get(BIOCYC_API_URL, params=params)

        if response.status_code == 200:
            data = response.json()
            name = data.get("commonName", "Unknown")
            category = data.get("className", "Unknown")
            return name, category
        else:
            print(f"Falha ao buscar {pathway_id}: {response.status_code}")
            return "Unknown", "Unknown"
    except Exception as e:
        print(f"Erro ao buscar {pathway_id}: {e}")
        return "Unknown", "Unknown"

input_file = "pathway-gg-general_ranking_pathways.csv"
output_file = "updated_pathways.csv"

df = pd.read_csv(input_file)

names = []
categories = []

for pathway_id in df.iloc[:, 0]:  # Supondo que o ID está na primeira coluna
    name, category = fetch_metacyc_info(pathway_id)
    names.append(name)
    categories.append(category)

df["Pathway Name"] = names
df["Category"] = categories

df.to_csv(output_file, index=False)

print(f"Arquivo atualizado salvo como {output_file}")
