import pandas as pd
import matplotlib.pyplot as plt
import random
from matplotlib import font_manager

# função para agrupar valores pequenos
def group_others(row):
    others = row[row < 2].sum()
    row = row[row >= 2]
    if others > 0:
        row['others < 2%'] = others
    return row

# lista de cores disponíveis
colors_list = [
    "lightcoral", "indianred", "firebrick", "red", "salmon", "coral", "orangered", "peru", 
    "yellow", "yellowgreen", "greenyellow", "chartreuse", "palegreen", "lightblue", "powderblue", 
    "aqua", "dodgerblue", "purple", "violet", "deeppink", "hotpink", "mediumvioletred", "blue", 
    "slateblue", "turquoise", "lightseagreen", "seagreen", "mediumpurple", "orange", "moccasin", 
    "gold", "khaki", "navajowhite"
]

# função para gerar cores aleatórias
def get_random_colors(categories):
    random.shuffle(colors_list)
    return {category: colors_list[i % len(colors_list)] for i, category in enumerate(categories)}

# carregar fonte
font_path = 'ArialNova.ttf'
font_prop = font_manager.FontProperties(fname=font_path)

# carregar dados
data = pd.read_csv('gg-phyla-feature-table-hellinger.tsv', sep='\t', skipinitialspace=True)
metadata = pd.read_csv('metadata_backup.tsv', sep='\t')

# verificar coluna otu id
if '#OTU ID' not in data.columns:
    print("otu id not find")
    raise ValueError("otu id not find")

# processar dados
data['#OTU ID'] = data['#OTU ID'].str.replace('d__Bacteria;p__', '').str.replace('d__Archaea;p__', '').str.replace('d__Bacteria;__', 'unclassified').str.replace('Unassigned;__', 'unassigned')
data = data.set_index('#OTU ID').T
data['condition'] = data.index.map(metadata.set_index('sample-id')['condition'])

# calcular abundâncias
grouped_data = data.groupby('condition').sum()
grouped_percentage = grouped_data.div(grouped_data.sum(axis=1), axis=0) * 100

# salvar rankings por condição
with pd.ExcelWriter('gg-condition_rankings_phyla.xlsx') as writer:
    for condition in grouped_data.index:
        condition_data = pd.DataFrame({
            'abundance': grouped_data.loc[condition],
            'percentage': grouped_percentage.loc[condition]
        }).sort_values(by='percentage', ascending=False)
        condition_data.to_excel(writer, sheet_name=condition)

# ranking geral
total_abundance = data.drop(columns='condition').sum()
total_percentage = total_abundance / total_abundance.sum() * 100
total_percentage = total_percentage.dropna()
general_ranking = pd.DataFrame({
    'abundance': total_abundance,
    'percentage': total_percentage
}).sort_values(by='percentage', ascending=False)
general_ranking.to_csv('gg-general_ranking_phyla.csv')

print("arquivos gerados")

# normalizar dados
grouped_mean = data.groupby('condition').mean()
grouped_normalized = grouped_mean.div(grouped_mean.sum(axis=1), axis=0) * 100
grouped_normalized = grouped_normalized.dropna(how='all')

# agrupar valores pequenos
grouped_normalized = grouped_normalized.apply(group_others, axis=1)
sorted_phyla = grouped_normalized.sum(axis=0).sort_values(ascending=False).index
grouped_normalized = grouped_normalized[sorted_phyla]

# ordenar condições
grouped_normalized = grouped_normalized.loc[grouped_normalized.sum(axis=1).sort_values(ascending=False).index]

# garantir ordem correta
columns = [col for col in grouped_normalized.columns if col != 'others < 2%'] + ['others < 2%']
grouped_normalized = grouped_normalized[columns]

# gerar cores
unique_phyla = grouped_normalized.columns.tolist()
if 'others < 2%' not in unique_phyla:
    unique_phyla.append('others < 2%')
color_mapping = get_random_colors(unique_phyla)
color_mapping['others < 2%'] = 'dimgray'

# gráfico de barras
plt.figure(figsize=(20, 10))
for i, phylum in enumerate(grouped_normalized.columns):
    plt.bar(
        grouped_normalized.index,
        grouped_normalized[phylum],
        bottom=grouped_normalized.iloc[:, :i].sum(axis=1),
        color=color_mapping[phylum],
        label=phylum
    )
    for j, value in enumerate(grouped_normalized[phylum]):
        if value > 0:
            plt.text(
                j, 
                grouped_normalized.iloc[j, :i].sum() + value / 2, 
                f'{value:.2f}%', 
                ha='center', 
                va='center', 
                fontsize=8, 
                color='black', 
                fontproperties=font_prop
            )

plt.title('abundância relativa por condição', fontsize=16, fontproperties=font_prop)
plt.xlabel('condição', fontsize=14, fontproperties=font_prop)
plt.ylabel('% abundância relativa', fontsize=14, fontproperties=font_prop)
plt.xticks(rotation=45, ha='right', fontproperties=font_prop)
plt.legend(title='filos', bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=10, prop=font_prop)
plt.tight_layout(rect=[0, 0, 0.85, 1])
plt.savefig('gg-stacked_bar_chart_phyla.pdf', bbox_inches='tight')
plt.show()

# gráficos de pizza por condição
for condition in grouped_normalized.index:
    condition_data = grouped_normalized.loc[condition].dropna()
    condition_data = group_others(condition_data)
    sorted_condition_data = condition_data.sort_values(ascending=False)
    colors = [color_mapping[phylum] for phylum in sorted_condition_data.index]
    plt.figure(figsize=(8, 8))
    wedges, texts, autotexts = plt.pie(
        sorted_condition_data,
        labels=sorted_condition_data.index,
        autopct='%1.2f%%',
        startangle=90,
        colors=colors,
        wedgeprops={'edgecolor': None}
    )
    for text in texts:
        text.set_fontsize(10)
        text.set_fontproperties(font_prop)
    for autotext in autotexts:
        autotext.set_fontsize(9)
        autotext.set_fontproperties(font_prop)
    plt.title(f'abundância relativa - {condition}', fontsize=14, fontproperties=font_prop)
    plt.tight_layout()
    plt.savefig(f'gg-pie_chart_{condition}_phyla.pdf', bbox_inches='tight')
    plt.show()

# gráfico de pizza geral
total_percentage = group_others(total_percentage)
sorted_total_percentage = total_percentage.sort_values(ascending=False)
colors = [color_mapping[phylum] for phylum in sorted_total_percentage.index]
plt.figure(figsize=(8, 8))
wedges, texts, autotexts = plt.pie(
    sorted_total_percentage,
    labels=sorted_total_percentage.index,
    autopct='%1.2f%%',
    startangle=90,
    colors=colors,
    wedgeprops={'edgecolor': None}
)
for text in texts:
    text.set_fontsize(10)
    text.set_fontproperties(font_prop)
for autotext in autotexts:
    autotext.set_fontsize(9)
    autotext.set_fontproperties(font_prop)
plt.title('abundância relativa - geral', fontsize=14, fontproperties=font_prop)
plt.tight_layout()
plt.savefig('gg-general_pie_chart_phyla.pdf', bbox_inches='tight')
plt.show()
