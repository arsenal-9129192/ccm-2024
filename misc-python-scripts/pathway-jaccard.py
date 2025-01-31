import pandas as pd
import numpy as np
from sklearn.metrics import pairwise_distances
import seaborn as sns
import matplotlib.pyplot as plt

pathway_data = pd.read_csv('pathway_abundance_no_header.tsv', sep='\t')
metadata = pd.read_csv('metadata_backup.tsv', sep='\t')

if '#OTU ID' not in pathway_data.columns:
    print("Colunas encontradas:", pathway_data.columns)
    raise ValueError("A coluna '#OTU ID' não foi encontrada. Verifique o cabeçalho do arquivo.")

pathway_data = pathway_data.set_index('#OTU ID').T.reset_index().rename(columns={'index': 'sample-id'})

combined_data = pd.merge(pathway_data, metadata[['sample-id', 'condition']], on='sample-id', how='inner')

def find_exclusive_pathways(data, condition_col, pathway_cols):
    exclusive_pathways = {}
    conditions = data[condition_col].unique()
    
    for condition in conditions:
        condition_data = data[data[condition_col] == condition]
        
        other_conditions = data[data[condition_col] != condition]
        exclusive = [
            pathway for pathway in pathway_cols
            if (condition_data[pathway] > 0).any() and (other_conditions[pathway] == 0).all()
        ]
        exclusive_pathways[condition] = exclusive
    
    return exclusive_pathways

pathway_cols = pathway_data.columns[1:]  # Todas as colunas de rotas metabólicas
exclusive_pathways = find_exclusive_pathways(combined_data, 'condition', pathway_cols)

print("Rotas metabólicas exclusivas por condition:")
for condition, pathways in exclusive_pathways.items():
    print(f"{condition}: {len(pathways)} rotas exclusivas")
    for pathway in pathways:
        print(f"  - {pathway}")

def calculate_jaccard_dissimilarity(data, condition_col, pathway_cols):
    presence_absence = data.groupby(condition_col)[pathway_cols].apply(lambda x: (x > 0).any().astype(int))
    
    presence_absence_matrix = presence_absence.to_numpy()
    
    jaccard_dist = pairwise_distances(presence_absence_matrix, metric='jaccard')
    jaccard_dist = pd.DataFrame(jaccard_dist, index=presence_absence.index, columns=presence_absence.index)
    
    return jaccard_dist

jaccard_dissimilarity = calculate_jaccard_dissimilarity(combined_data, 'condition', pathway_cols)

plt.figure(figsize=(10, 8))
sns.heatmap(jaccard_dissimilarity, annot=True, cmap='viridis', fmt=".2f", linewidths=0.5)
plt.title('Matriz de Dissimilaridade de Jaccard entre Conditions', fontsize=16)
plt.xlabel('Condition', fontsize=14)
plt.ylabel('Condition', fontsize=14)
plt.tight_layout()
plt.savefig('jaccard_dissimilarity_matrix.pdf', bbox_inches='tight')
plt.show()

jaccard_dissimilarity.to_csv('jaccard_dissimilarity_matrix.csv')
print("Matriz de dissimilaridade salva em 'jaccard_dissimilarity_matrix.csv'.")
