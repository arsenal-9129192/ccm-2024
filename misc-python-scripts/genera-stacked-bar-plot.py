import pandas as pd
import matplotlib.pyplot as plt

feature_table = pd.read_csv('feature-table-hellinger.tsv', sep='\t', index_col=0)

metadata = pd.read_csv('metadata_backup.tsv', sep='\t')

feature_table = feature_table[feature_table.index.str.startswith('g__')]

common_samples = feature_table.columns.intersection(metadata['sample-id'])

feature_table = feature_table[common_samples]
metadata = metadata[metadata['sample-id'].isin(common_samples)]

conditions = metadata.set_index('sample-id')['condition']

grouped_data = feature_table.T.groupby(conditions).sum()

ax = grouped_data.plot(kind='bar', stacked=True, figsize=(10, 7))

plt.title('Abundâncias Relativas de Gêneros')
plt.xlabel('Condition')
plt.ylabel('Abundância Relativa')
plt.xticks(rotation=45, ha='right')
plt.tight_layout()

plt.savefig('abundancia_relativa_gêneros.png', format='png')

plt.show()
