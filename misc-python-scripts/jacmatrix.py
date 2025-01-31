import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

dist_matrix = pd.read_csv('jaccard_matrix.tsv', sep='\t', index_col=0)

dist_matrix = dist_matrix.apply(pd.to_numeric, errors='coerce')

metadata = pd.read_csv('metadata_backup.tsv', sep='\t')

sample_to_condition = metadata.set_index('sample-id')['condition'].to_dict()

valid_samples = [idx for idx in dist_matrix.index if idx in sample_to_condition]
dist_matrix = dist_matrix.loc[valid_samples, valid_samples]

dist_matrix.index = [sample_to_condition[idx] for idx in dist_matrix.index]
dist_matrix.columns = [sample_to_condition[col] for col in dist_matrix.columns]

conditions = metadata['condition'].unique()
mean_dist_matrix = pd.DataFrame(np.zeros((len(conditions), len(conditions))), 
                              index=conditions, 
                              columns=conditions)

for cond1 in conditions:
    for cond2 in conditions:
        mask1 = dist_matrix.index == cond1
        mask2 = dist_matrix.columns == cond2
        if mask1.any() and mask2.any():
            mean_dist = dist_matrix.loc[mask1, mask2].mean().mean()
            mean_dist_matrix.loc[cond1, cond2] = mean_dist

mean_dist_matrix = mean_dist_matrix.astype(float)

mask = np.triu(np.ones_like(mean_dist_matrix), k=0)

plt.figure(figsize=(10, 8))
sns.heatmap(mean_dist_matrix,
            mask=mask,
            annot=True,
            cmap='Reds',
            fmt='.2f',
            linewidths=1,
            linecolor='black',
            cbar_kws={'label': 'Dissimilaridade de Jaccard Média'})

plt.title('Matriz de Dissimilaridade de Jaccard entre Condições', fontsize=16)
plt.xlabel('Condição', fontsize=14)
plt.ylabel('Condição', fontsize=14)

plt.tight_layout()
plt.savefig('jaccard_dissimilarity_matrix.pdf', bbox_inches='tight')
plt.show()

mean_dist_matrix.to_csv('mean_jaccard_dissimilarity_matrix.csv')
print("Matriz de dissimilaridade média salva em 'mean_jaccard_dissimilarity_matrix.csv'")
