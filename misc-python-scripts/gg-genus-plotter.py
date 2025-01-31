import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import random
from matplotlib import font_manager

def group_others(row):
    others = row[row < 2].sum()
    row = row[row >= 2]
    if others > 0:
        row['Others < 2%'] = others
    return row

available_colors = [
    "mediumseagreen", "deepskyblue", "royalblue", "cornflowerblue", "crimson", "deeppink", "thistle", "plum", "khaki", "lawngreen"
]

def get_random_colors(categories):
    random.shuffle(available_colors)  # Embaralhar a lista de cores
    color_mapping = {category: available_colors[i % len(available_colors)] for i, category in enumerate(categories)}
    return color_mapping

font_path = 'ArialNova.ttf'
prop = font_manager.FontProperties(fname=font_path)

genus_data = pd.read_csv('gg-genus-feature-table-hellinger.tsv', sep='\t', skipinitialspace=True)
metadata = pd.read_csv('metadata_backup.tsv', sep='\t')

if '#OTU ID' not in genus_data.columns:
    print("Colunas encontradas:", genus_data.columns)
    raise ValueError("A coluna '#OTU ID' não foi encontrada. Verifique o cabeçalho do arquivo.")

genus_data['#OTU ID'] = genus_data['#OTU ID']
genus_data['#OTU ID'] = genus_data['#OTU ID'].str.replace('d__Bacteria;.*;g__', '')
genus_data['#OTU ID'] = genus_data['#OTU ID'].str.replace('d__Archaea;.*;g__', '')
genus_data['#OTU ID'] = genus_data['#OTU ID'].str.replace('d__Bacteria;.*;__', 'Unclassified')
genus_data['#OTU ID'] = genus_data['#OTU ID'].str.replace('Unassigned;__', 'Unassigned')
genus_data = genus_data.set_index('#OTU ID').T
genus_data['condition'] = genus_data.index.map(metadata.set_index('sample-id')['condition'])

grouped_data = genus_data.groupby('condition').sum()
grouped_percentage = grouped_data.div(grouped_data.sum(axis=1), axis=0) * 100

with pd.ExcelWriter('gg-condition_rankings_genus.xlsx') as writer:
    for condition in grouped_data.index:
        condition_data = pd.DataFrame({
            'Abundance': grouped_data.loc[condition],
            'Percentage': grouped_percentage.loc[condition]
        }).sort_values(by='Percentage', ascending=False)
        condition_data.to_excel(writer, sheet_name=condition)

total_abundance = genus_data.drop(columns='condition').sum()
total_percentage = total_abundance / total_abundance.sum() * 100
total_percentage = total_percentage.dropna()  # Remover valores NaN
general_ranking = pd.DataFrame({
    'Abundance': total_abundance,
    'Percentage': total_percentage
}).sort_values(by='Percentage', ascending=False)
general_ranking.to_csv('gg-general_ranking_genus.csv')

print("Arquivos CSV gerados com sucesso.")

grouped_mean = genus_data.groupby('condition').mean()
grouped_normalized = grouped_mean.div(grouped_mean.sum(axis=1), axis=0) * 100
grouped_normalized = grouped_normalized.dropna(how='all')  # Remover linhas completamente NaN

grouped_normalized = grouped_normalized.apply(group_others, axis=1)
sorted_genus = grouped_normalized.sum(axis=0).sort_values(ascending=False).index
grouped_normalized = grouped_normalized[sorted_genus]

grouped_normalized = grouped_normalized.loc[grouped_normalized.sum(axis=1).sort_values(ascending=False).index]

columns = [col for col in grouped_normalized.columns if col != 'Others < 2%'] + ['Others < 2%']
grouped_normalized = grouped_normalized[columns]

unique_genus = grouped_normalized.columns.tolist()
if 'Others < 2%' not in unique_genus:
    unique_genus.append('Others < 2%')

color_mapping = get_random_colors(unique_genus)

color_mapping['Others < 2%'] = 'dimgray'  # Cor cinza escuro para 'Others < 2%'

plt.figure(figsize=(20, 10))
bars = []
for i, genus in enumerate(grouped_normalized.columns):
    bar = plt.bar(
        grouped_normalized.index,
        grouped_normalized[genus],
        bottom=grouped_normalized.iloc[:, :i].sum(axis=1),
        color=color_mapping[genus],
        edgecolor='black',
        label=genus
    )
    bars.append(bar)

    for j, value in enumerate(grouped_normalized[genus]):
        if value > 0:
            plt.text(
                j, 
                grouped_normalized.iloc[j, :i].sum() + value / 2, 
                f'{value:.2f}%',  # Exibir duas casas decimais
                ha='center', 
                va='center', 
                fontsize=8, 
                color='black', 
                fontproperties=prop
            )

plt.title('Relative Abundance of Genus by Condition', fontsize=16, fontproperties=prop)
plt.xlabel('Condition', fontsize=14, fontproperties=prop)
plt.ylabel('% Relative Abundance', fontsize=14, fontproperties=prop)
plt.xticks(rotation=45, ha='right', fontproperties=prop)
plt.legend(title='Genus', bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=10, prop=prop)
plt.tight_layout(rect=[0, 0, 0.85, 1])
plt.savefig('gg-stacked_bar_chart_genus.pdf', bbox_inches='tight')
plt.show()

for condition in grouped_normalized.index:
    condition_data = grouped_normalized.loc[condition].dropna()  # Remover valores NaN
    condition_data = group_others(condition_data)  # Garantir agrupamento de gêneros menores
    sorted_condition_data = condition_data.sort_values(ascending=False)
    colors = [color_mapping[genus] for genus in sorted_condition_data.index]
    plt.figure(figsize=(8, 8))
    wedges, texts, autotexts = plt.pie(
        sorted_condition_data,
        labels=sorted_condition_data.index,
        autopct='%1.2f%%',  # Exibir duas casas decimais
        startangle=90,
        colors=colors,
        wedgeprops={'edgecolor': 'black'}
    )
    for text in texts:
        text.set_fontsize(10)
        text.set_fontproperties(prop)
    for autotext in autotexts:
        autotext.set_fontsize(9)
        autotext.set_fontproperties(prop)
    plt.title(f'Relative Abundance of Genus - {condition}', fontsize=14, fontproperties=prop)
    plt.tight_layout()
    plt.savefig(f'gg-pie_chart_{condition}_genus.pdf', bbox_inches='tight')
    plt.show()

total_percentage = group_others(total_percentage)  # Garantir agrupamento de gêneros menores
sorted_total_percentage = total_percentage.sort_values(ascending=False)
colors = [color_mapping[genus] for genus in sorted_total_percentage.index]
plt.figure(figsize=(8, 8))
wedges, texts, autotexts = plt.pie(
    sorted_total_percentage,
    labels=sorted_total_percentage.index,
    autopct='%1.2f%%',  # Exibir duas casas decimais
    startangle=90,
    colors=colors,
    wedgeprops={'edgecolor': 'black'}
)
for text in texts:
    text.set_fontsize(10)
    text.set_fontproperties(prop)
for autotext in autotexts:
    autotext.set_fontsize(9)
    autotext.set_fontproperties(prop)
plt.title('Relative Abundance of Genus - General', fontsize=14, fontproperties=prop)
plt.tight_layout()
plt.savefig('gg-general_pie_chart_genus.pdf', bbox_inches='tight')
plt.show()
