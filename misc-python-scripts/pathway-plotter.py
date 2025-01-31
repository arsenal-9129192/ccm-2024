import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import random
from matplotlib import font_manager
from sklearn.preprocessing import normalize

def group_others(row, threshold=0.5):
    others = row[row < threshold].sum()
    row = row[row >= threshold]
    if others > 0:
        row[f'Others < {threshold}%'] = others
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

phyla_data = pd.read_csv('pathway_abundance_no_header.tsv', sep='\t')
metadata = pd.read_csv('metadata_backup.tsv', sep='\t')

if '#OTU ID' not in phyla_data.columns:
    print("Colunas encontradas:", phyla_data.columns)
    raise ValueError("A coluna '#OTU ID' não foi encontrada. Verifique o cabeçalho do arquivo.")

phyla_data = phyla_data.set_index('#OTU ID').T.reset_index().rename(columns={'index': 'sample-id'})

combined_data = pd.merge(phyla_data, metadata[['sample-id', 'condition']], on='sample-id', how='inner')

grouped_data = combined_data.groupby('condition').sum(numeric_only=True)

grouped_percentage = grouped_data.div(grouped_data.sum(axis=1), axis=0) * 100

for condition in grouped_data.index:
    condition_data = pd.DataFrame({
        'Pathway ID': grouped_data.columns,
        'Raw Abundance': grouped_data.loc[condition],
        'Relative Abundance (%)': grouped_percentage.loc[condition]
    })
    condition_data.to_csv(f'pathway_abundance_{condition}.csv', index=False)

print("Arquivos CSV gerados com sucesso.")

grouped_normalized = grouped_percentage.apply(lambda x: group_others(x, threshold=0.5), axis=1)
sorted_pathways = grouped_normalized.sum(axis=0).sort_values(ascending=False).index
grouped_normalized = grouped_normalized[sorted_pathways]

grouped_normalized = grouped_normalized.loc[grouped_normalized.sum(axis=1).sort_values(ascending=False).index]

columns = [col for col in grouped_normalized.columns if not col.startswith('Others')] + [col for col in grouped_normalized.columns if col.startswith('Others')]
grouped_normalized = grouped_normalized[columns]

unique_pathways = grouped_normalized.columns.tolist()
color_mapping = get_random_colors(unique_pathways)

for col in grouped_normalized.columns:
    if col.startswith('Others'):
        color_mapping[col] = 'dimgray'

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

plt.title('Relative Abundance of Pathways by Condition (≥ 0.5%)', fontsize=16, fontproperties=prop)
plt.xlabel('Condition', fontsize=14, fontproperties=prop)
plt.ylabel('% Relative Abundance', fontsize=14, fontproperties=prop)
plt.xticks(rotation=45, ha='right', fontproperties=prop)
plt.legend(title='Pathways', bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=10, prop=prop)
plt.tight_layout(rect=[0, 0, 0.85, 1])
plt.savefig('pathway-gg-stacked_bar_chart_pathways.pdf', bbox_inches='tight')
plt.show()

for condition in grouped_normalized.index:
    condition_data = grouped_normalized.loc[condition].dropna()  # Remover valores NaN
    condition_data = group_others(condition_data, threshold=0.5)  # Garantir agrupamento de rotas menores
    sorted_condition_data = condition_data.sort_values(ascending=False)
    colors = [color_mapping[pathway] for pathway in sorted_condition_data.index]
    plt.figure(figsize=(8, 8))
    wedges, texts, autotexts = plt.pie(
        sorted_condition_data,
        labels=sorted_condition_data.index,
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
    plt.title(f'Relative Abundance of Pathways - {condition} (≥ 0.5%)', fontsize=14, fontproperties=prop)
    plt.tight_layout()
    plt.savefig(f'pathway-gg-pie_chart_{condition}_pathways.pdf', bbox_inches='tight')
    plt.show()
