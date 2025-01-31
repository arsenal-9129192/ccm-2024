import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

phyla_data = pd.read_csv('phyla-feature-table-hellinger.tsv', sep='\t', skipinitialspace=True)
metadata = pd.read_csv('metadata_backup.tsv', sep='\t')

if '#OTU ID' not in phyla_data.columns:
    print("Colunas encontradas:", phyla_data.columns)
    raise ValueError("A coluna '#OTU ID' não foi encontrada. Verifique o cabeçalho do arquivo.")

phyla_data['#OTU ID'] = phyla_data['#OTU ID'].str.replace('d__Bacteria;p__', '')

phyla_data = phyla_data.set_index('#OTU ID').T

phyla_data['condition'] = phyla_data.index.map(metadata.set_index('sample-id')['condition'])

grouped_data = phyla_data.groupby('condition').mean()

grouped_data = grouped_data.div(grouped_data.sum(axis=1), axis=0) * 100

def top_10_phyla(row):
    top_10 = row.nlargest(10)
    others = row.drop(top_10.index).sum()
    top_10['Others'] = others
    return top_10

grouped_data = grouped_data.apply(top_10_phyla, axis=1)

plt.figure(figsize=(20, 10))

palette = sns.color_palette("hsv", 50)
palette[-1] = (0.8, 0.8, 0.8)

colors = [palette[i % len(palette)] for i in range(len(grouped_data.columns))]

ax = grouped_data.plot(kind='bar', stacked=True, color=colors, width=0.8)

plt.title('Abundância Relativa de Filos por Condição', fontsize=16)
plt.xlabel('Condição', fontsize=14)
plt.ylabel('Abundância Relativa (%)', fontsize=14)
plt.xticks(rotation=45, ha='right')  # Rotacionar os rótulos do eixo x para melhor legibilidade
plt.legend(title='Filos', bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=10)
plt.tight_layout(rect=[0, 0, 0.85, 1])  # Ajustar o layout para evitar cortes

plt.savefig('stacked_bar_chart.pdf', bbox_inches='tight')  # Salvar com bbox_inches para evitar cortes
plt.show()
