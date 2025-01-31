import pandas as pd
import numpy as np
from sklearn.preprocessing import normalize
import requests
import os

ko_metagenome_path = os.path.expanduser("~/ccmnovo/picrust2_output/exported_ko_metagenome/ko_metagenome.tsv")
metadata_path = os.path.expanduser("~/ccmnovo/metadata_backup.tsv")

with open(ko_metagenome_path, 'r') as f:
    for line in f:
        if line.startswith("#OTU ID"):
            header = line.strip().split("\t")
            break

ko_metagenome = pd.read_csv(ko_metagenome_path, sep="\t", comment="#", header=None, skiprows=2)
ko_metagenome.columns = header

ko_metagenome.set_index("#OTU ID", inplace=True)

metadata = pd.read_csv(metadata_path, sep="\t")

metadata = metadata[metadata['sample-id'].isin(ko_metagenome.columns)]

def hellinger_transform(df):
    return np.sqrt(df.div(df.sum(axis=1), axis=0))

ko_metagenome_hellinger = hellinger_transform(ko_metagenome)

def get_kegg_pathways(ko_id):
    url = f"http://rest.kegg.jp/link/pathway/{ko_id}"
    response = requests.get(url)
    if response.status_code == 200:
        pathways = response.text.strip().split('\n')
        pathways = [path.split('\t')[1] for path in pathways if path.startswith('ko')]
        return pathways
    return []

ko_pathways = {}
for ko in ko_metagenome.index:
    pathways = get_kegg_pathways(ko)
    if pathways:
        ko_pathways[ko] = pathways

pathway_df = pd.DataFrame.from_dict(ko_pathways, orient='index').stack().reset_index()
pathway_df.columns = ['KO', 'drop', 'Pathway']
pathway_df = pathway_df.drop(columns=['drop'])

grouped = ko_metagenome_hellinger.groupby(metadata.set_index('sample-id')['condition'], axis=1).mean()

output_dir = os.path.expanduser("~/ccmnovo/picrust2_output/exported_ko_metagenome")
os.makedirs(output_dir, exist_ok=True)

for condition in grouped.columns:
    ko_metagenome[metadata[metadata['condition'] == condition]['sample-id']].to_csv(
        os.path.join(output_dir, f"{condition}_abundancias_brutas.csv")
    )
    
    ko_metagenome_hellinger[metadata[metadata['condition'] == condition]['sample-id']].to_csv(
        os.path.join(output_dir, f"{condition}_abundancias_relativas.csv")
    )

ko_metagenome.to_csv(os.path.join(output_dir, "abundancias_gerais_brutas.csv"))
ko_metagenome_hellinger.to_csv(os.path.join(output_dir, "abundancias_gerais_relativas.csv"))

for condition in grouped.columns:
    condition_pathways = pathway_df.merge(
        grouped[condition].reset_index(), 
        left_on='KO', 
        right_on='index'
    ).drop(columns=['index'])
    condition_pathways.groupby('Pathway').mean().to_csv(
        os.path.join(output_dir, f"{condition}_rotas_metabolicas.csv")
    )

all_pathways = pathway_df.merge(
    ko_metagenome_hellinger.reset_index(), 
    left_on='KO', 
    right_on='index'
).drop(columns=['index'])
all_pathways.groupby('Pathway').mean().to_csv(
    os.path.join(output_dir, "rotas_metabolicas_gerais.csv")
)

print("Processamento concluído! Arquivos CSV gerados em:", output_dir)
