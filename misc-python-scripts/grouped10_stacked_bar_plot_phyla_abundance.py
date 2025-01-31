import pandas as pd
import matplotlib.pyplot as plt

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

def group_others(row):
    others = row[row < 3].sum()
    row = row[row >= 3]
    row['Others < 3%'] = others
    return row

grouped_data = grouped_data.apply(group_others, axis=1)

total_abundance = grouped_data.sum(axis=0)
sorted_phyla = total_abundance.sort_values(ascending=False).index
grouped_data = grouped_data[sorted_phyla]

plt.figure(figsize=(20, 10))  # Aumentar a largura da figura
ax = grouped_data.plot(kind='bar', stacked=True, colormap='tab20', width=0.8)

plt.title('Abundância Relativa de Filos por Condição', fontsize=16)
plt.xlabel('Condição', fontsize=14)
plt.ylabel('Abundância Relativa (%)', fontsize=14)
plt.xticks(rotation=45, ha='right')  # Rotacionar os rótulos do eixo x para melhor legibilidade
plt.legend(title='Filos', bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=10)
plt.tight_layout(rect=[0, 0, 0.85, 1])  # Ajustar o layout para evitar cortes

plt.savefig('stacked_bar_chart.pdf', bbox_inches='tight')  # Salvar com bbox_inches para evitar cortes
plt.show()

for condition in grouped_data.index:
    plt.figure(figsize=(8, 8))
    grouped_data.loc[condition].plot(kind='pie', autopct='%1.1f%%', startangle=90, colormap='tab20')
    plt.title(f'Abundância Relativa de Filos - {condition}', fontsize=14)
    plt.ylabel('')  # Remover o rótulo do eixo y
    plt.tight_layout()
    plt.savefig(f'pie_chart_{condition}.pdf', bbox_inches='tight')  # Salvar cada gráfico de pizza
    plt.show()
