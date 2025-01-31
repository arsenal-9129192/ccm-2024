import pandas as pd
import matplotlib.pyplot as plt

phyla_data = pd.read_csv('phyla-feature-table-hellinger.tsv', sep='\t', skipinitialspace=True)
metadata = pd.read_csv('metadata_backup.tsv', sep='\t')

phyla_data['#OTU ID'] = phyla_data['#OTU ID'].str.replace('d__Bacteria;p__', '')

phyla_data = phyla_data.set_index('#OTU ID').T

phyla_data['condition'] = phyla_data.index.map(metadata.set_index('sample-id')['condition'])

grouped_data = phyla_data.groupby('condition').mean()

grouped_data = grouped_data.div(grouped_data.sum(axis=1), axis=0) * 100

plt.figure(figsize=(4800, 3200))
grouped_data.plot(kind='bar', stacked=True, colormap='tab20', width=0.8)

plt.title('Abundância Relativa de Filos por Condição')
plt.xlabel('Condição')
plt.ylabel('Abundância Relativa (%)')
plt.legend(title='Filos', bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()

plt.savefig('stacked_bar_chart.pdf')
plt.show()
