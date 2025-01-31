import qiime2
from qiime2 import Artifact
from skbio.diversity import beta_diversity
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import font_manager as fm

rarefied_table = Artifact.load('rarefied-table.qza')
rarefied_df = rarefied_table.view(pd.DataFrame)

jaccard_matrix = beta_diversity("jaccard", rarefied_df.values, ids=rarefied_df.index)

jaccard_df = pd.DataFrame(jaccard_matrix.data, index=rarefied_df.index, columns=rarefied_df.index)

metadata = pd.read_csv('metadata_backup.tsv', sep='\t', index_col='sample-id')
conditions = metadata.loc[rarefied_df.index, 'condition']  # Garantir a ordem correta das amostras

grouped_df = pd.DataFrame(index=conditions.unique(), columns=conditions.unique())

for group1 in grouped_df.index:
    for group2 in grouped_df.columns:
        samples_group1 = conditions[conditions == group1].index
        samples_group2 = conditions[conditions == group2].index
        
        submatrix = jaccard_df.loc[samples_group1, samples_group2]
        
        grouped_df.loc[group1, group2] = submatrix.mean().mean()

grouped_df = grouped_df.astype(float)

font_path = 'ArialNova.ttf'
custom_font = fm.FontProperties(fname=font_path)

plt.rcParams['font.family'] = custom_font.get_name()

plt.figure(figsize=(8, 6))
heatmap = sns.heatmap(
    grouped_df,
    cmap='Reds',
    annot=True,
    fmt=".2f",
    square=True,
    cbar_kws={'label': 'Média da Dissimilaridade de Jaccard'},
    linewidths=0.5,
    linecolor='black'
)

plt.title('Heatmap Agrupado por Condição', fontsize=16, fontproperties=custom_font)
plt.xlabel('Condição', fontsize=12, fontproperties=custom_font)
plt.ylabel('Condição', fontsize=12, fontproperties=custom_font)

for label in heatmap.get_xticklabels():
    label.set_fontproperties(custom_font)
for label in heatmap.get_yticklabels():
    label.set_fontproperties(custom_font)

plt.savefig('heatmap_grouped_condition.pdf', bbox_inches='tight', format='pdf')

plt.show()
