import qiime2
from qiime2 import Artifact
from skbio.diversity import beta_diversity
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from scipy.cluster.hierarchy import linkage, leaves_list
import numpy as np

rarefied_table = Artifact.load('rarefied-table.qza')
rarefied_df = rarefied_table.view(pd.DataFrame)

jaccard_matrix = beta_diversity("jaccard", rarefied_df.values, ids=rarefied_df.index)

jaccard_df = pd.DataFrame(jaccard_matrix.data, index=rarefied_df.index, columns=rarefied_df.index)

metadata = pd.read_csv('metadata_backup.tsv', sep='\t', index_col='sample-id')
conditions = metadata.loc[rarefied_df.index, 'condition']  # Garantir a ordem correta das amostras

condition_order = conditions.sort_values().index
jaccard_df = jaccard_df.loc[condition_order, condition_order]

plt.figure(figsize=(10, 8))
heatmap = sns.heatmap(
    jaccard_df,
    cmap='Reds',
    annot=False,
    square=True,
    cbar_kws={'label': 'Jaccard Dissimilarity'},
    yticklabels=conditions.loc[condition_order],  # Rótulos das condições no eixo y
    xticklabels=False  # Remover rótulos do eixo x para evitar sobreposição
)

plt.title('Matriz de Dissimilaridade de Jaccard Agrupada por Condição', fontsize=16)

plt.ylabel('Condição', fontsize=12)

plt.savefig('jaccard_heatmap_grouped.pdf', bbox_inches='tight', format='pdf')

plt.show()
