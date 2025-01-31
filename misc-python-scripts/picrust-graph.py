import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import random
from matplotlib import font_manager
from sklearn.preprocessing import normalize

def group_others(row):
    others = row[row < 0.5].sum()
    row = row[row >= 0.5]
    if others > 0:
        row['Others < 0.5%'] = others
    return row

available_colors = [
    "lightcoral", "indianred", "firebrick", "red", "salmon", "coral", "orangered", "peru", 
    "yellow", "yellowgreen", "greenyellow", "chartreuse", "palegreen", "lightblue", "powderblue", 
    "aqua", "dodgerblue", "purple", "violet", "deeppink", "hotpink", "mediumvioletred", "blue", 
    "slateblue", "turquoise", "lightseagreen", "seagreen", "mediumpurple", "orange", "moccasin", 
    "gold", "khaki", "navajowhite"
]

def get_random_colors(categories):
    random.shuffle(available_colors)  # Embaralhar a lista de cores
    color_mapping = {category: available_colors[i % len(available_colors)] for i, category in enumerate(categories)}
    return color_mapping

font_path = 'ArialNova.ttf'
prop = font_manager.FontProperties(fname=font_path)

pathway_data = pd.read_csv('pathway_abundance_no_header.tsv', sep='\t')
metadata = pd.read_csv('metadata_backup.tsv', sep='\t')

if '#OTU ID' not in pathway_data.columns:
    print("Colunas encontradas:", pathway_data.columns)
    raise ValueError("A coluna '#OTU ID' não foi encontrada. Verifique o cabeçalho do arquivo.")

pathway_data = pathway_data.set_index('#OTU ID').T.reset_index().rename(columns={'index': 'sample-id'})

pathway_data_hellinger = pd.DataFrame(
    normalize(np.sqrt(pathway_data.iloc[:, 1:]), norm='l2'),
    columns=pathway_data.columns[1:],
    index=pathway_data['sample-id']
).reset_index()

combined_data = pd.merge(pathway_data_hellinger, metadata[['sample-id', 'condition']], on='sample-id', how='inner')

grouped_data = combined_data.groupby('condition').sum(numeric_only=True)

grouped_percentage = grouped_data.div(grouped_data.sum(axis=1), axis=0) * 100

with pd.ExcelWriter('pathway-gg-condition_rankings_pathways.xlsx') as writer:
    for condition in grouped_data.index:
        condition_data = pd.DataFrame({
            'Abundance': grouped_data.loc[condition],
            'Percentage': grouped_percentage.loc[condition]
        }).sort_values(by='Percentage', ascending=False)
        condition_data.to_excel(writer, sheet_name=condition)

total_abundance = grouped_data.sum()
total_percentage = total_abundance / total_abundance.sum() * 100
total_percentage = total_percentage.dropna()  # Remover valores NaN
general_ranking = pd.DataFrame({
    'Abundance': total_abundance,
    'Percentage': total_percentage
}).sort_values(by='Percentage', ascending=False)
general_ranking.to_csv('pathway-gg-general_ranking_pathways.csv')

print("Arquivos CSV gerados com sucesso.")

grouped_normalized = grouped_percentage.apply(group_others, axis=1)

sorted_pathways = grouped_normalized.sum(axis=0).sort_values(ascending=False).index
grouped_normalized = grouped_normalized[sorted_pathways]

columns = [col for col in grouped_normalized.columns if col != 'Others < 0.5%'] + ['Others < 0.5%']
grouped_normalized = grouped_normalized[columns]

unique_pathways = grouped_normalized.columns.tolist()
color_mapping = get_random_colors(unique_pathways)

color_mapping['Others < 0.5%'] = 'dimgray'  # Cor cinza escuro para 'Others < 0.5%'

plt.figure(figsize=(20, 10))
bars = []
for i, pathway in enumerate(grouped_normalized.columns):
    bar = plt.bar(
        grouped_normalized.index,
        grouped_normalized[pathway],
        bottom=grouped_normalized.iloc[:, :i].sum(axis=1),
        color=color_mapping[pathway],
        edgecolor='black',
        label=pathway
    )
    bars.append(bar)

    for j, value in enumerate(grouped_normalized[pathway]):
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

plt.title('Relative Abundance of Pathways by Condition (Others < 0.5% grouped)', fontsize=16, fontproperties=prop)
plt.xlabel('Condition', fontsize=14, fontproperties=prop)
plt.ylabel('% Relative Abundance', fontsize=14, fontproperties=prop)
plt.xticks(rotation=45, ha='right', fontproperties=prop)
plt.legend(title='Pathways', bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=10, prop=prop)
plt.tight_layout(rect=[0, 0, 0.85, 1])
plt.savefig('pathway-gg-stacked_bar_chart_pathways.pdf', bbox_inches='tight')
plt.show()

total_percentage = group_others(total_percentage)  # Garantir agrupamento de rotas metabólicas menores
sorted_total_percentage = total_percentage.sort_values(ascending=False)
colors = [color_mapping[pathway] for pathway in sorted_total_percentage.index]
plt.figure(figsize=(8, 8))
wedges, texts, autotexts = plt.pie(
    sorted_total_percentage,
    labels=sorted_total_percentage.index,
    autopct='%1.2f%%',  # Exibir duas casas decimais
    startangle=90,
    colors=colors,
    wedgeprops={'edgecolor': 'black'}
)
for i, wedge in enumerate(wedges):
    wedge.set_hatch(None)  # Remover hachuras
for text in texts:
    text.set_fontsize(10)
    text.set_fontproperties(prop)
for autotext in autotexts:
    autotext.set_fontsize(9)
    autotext.set_fontproperties(prop)
plt.title('Relative Abundance of Pathways - General (Others < 0.5% grouped)', fontsize=14, fontproperties=prop)
plt.tight_layout()
plt.savefig('pathway-gg-general_pie_chart_pathways.pdf', bbox_inches='tight')
plt.show()
