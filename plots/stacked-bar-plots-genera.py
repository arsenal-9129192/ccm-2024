import pandas as pd
import matplotlib.pyplot as plt
import random
from matplotlib import font_manager

# função para agrupar valores pequenos
def group_others(row):
    others = row[row < 1].sum()  # filtro de 1%
    row = row[row >= 1]
    if others > 0:
        row['others < 1%'] = others  # alterado para 1%
    return row

# lista de cores disponíveis
colors_list = [
    "aliceblue", "antiquewhite", "aqua", "aquamarine", "azure", "beige", "bisque", "blanchedalmond", "blue",
    "blueviolet", "brown", "burlywood", "cadetblue", "chartreuse", "chocolate", "coral", "cornflowerblue",
    "cornsilk", "crimson", "cyan", "darkblue", "darkcyan", "darkgoldenrod", "darkgreen", "deeppink", "deepskyblue",
    "khaki", "lawngreen", "mediumseagreen", "pink", "plum", "royalblue", "thistle"
]

# função para gerar cores aleatórias
def get_random_colors(categories):
    random.shuffle(colors_list)
    return {category: colors_list[i % len(colors_list)] for i, category in enumerate(categories)}

# carregar fonte
font_path = 'ArialNova.ttf'
font_prop = font_manager.FontProperties(fname=font_path)

# carregar dados
data = pd.read_csv('gg-genera-feature-table-hellinger.tsv', sep='\t', skipinitialspace=True)
metadata = pd.read_csv('metadata_backup.tsv', sep='\t')

# verificar coluna otu id
if '#OTU ID' not in data.columns:
    print("otu id not find")
    raise ValueError("otu id not find")

# processar dados
data['#OTU ID'] = data['#OTU ID'].apply(lambda x: x.split(";g__")[-1] if "g__" in x else "unassigned")
data = data.set_index('#OTU ID').T
data['condition'] = data.index.map(metadata.set_index('sample-id')['condition'])

# resolver duplicatas
data = data.groupby(data.index).sum()

# calcular abundâncias
grouped_data = data.groupby('condition').sum()
grouped_percentage = grouped_data.div(grouped_data.sum(axis=1), axis=0) * 100

# salvar rankings por condição
with pd.ExcelWriter('gg-condition_rankings_genera.xlsx') as writer:
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
general_ranking.to_csv('gg-general_ranking_genera.csv')

print("arquivos gerados")

# normalizar dados
grouped_mean = data.groupby('condition').mean()
grouped_normalized = grouped_mean.div(grouped_mean.sum(axis=1), axis=0) * 100
grouped_normalized = grouped_normalized.dropna(how='all')

# remover colunas duplicadas
grouped_normalized = grouped_normalized.loc[:, ~grouped_normalized.columns.duplicated()]

# agrupar valores pequenos
grouped_normalized = grouped_normalized.apply(group_others, axis=1)

# garantir que 'unclassified' e 'unassigned' sejam tratados corretamente
if 'unclassified' in grouped_normalized.columns:
    grouped_normalized['unclassified'] = grouped_normalized.filter(like='unclassified', axis=1).sum(axis=1)
if 'unassigned' in grouped_normalized.columns:
    grouped_normalized['unassigned'] = grouped_normalized.filter(like='unassigned', axis=1).sum(axis=1)

# recalcular porcentagens
grouped_normalized = grouped_normalized.div(grouped_normalized.sum(axis=1), axis=0) * 100

# ordenar gêneros
grouped_normalized = grouped_normalized.loc[:, grouped_normalized.sum().sort_values(ascending=False).index]

# garantir ordem correta
columns = [col for col in grouped_normalized.columns if col != 'others < 1%'] + ['others < 1%']
grouped_normalized = grouped_normalized[columns]

# gerar cores
unique_genera = grouped_normalized.columns.tolist()
if 'others < 1%' not in unique_genera:
    unique_genera.append('others < 1%')
color_mapping = get_random_colors(unique_genera)
color_mapping['others < 1%'] = 'dimgray'

# gráfico de barras
plt.figure(figsize=(20, 10))
for i, genus in enumerate(grouped_normalized.columns):
    plt.bar(
        grouped_normalized.index,
        grouped_normalized[genus],
        bottom=grouped_normalized.iloc[:, :i].sum(axis=1),
        color=color_mapping[genus],
        label=genus
    )
    for j, value in enumerate(grouped_normalized[genus]):
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
plt.legend(title='gêneros', bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=10, prop=font_prop)
plt.tight_layout()
plt.savefig('gg-stacked_bar_chart_genera.pdf', bbox_inches='tight')
plt.show()

# gráficos de pizza por condição
for condition in grouped_normalized.index:
    condition_data = grouped_normalized.loc[condition].dropna()
    condition_data = group_others(condition_data)
    sorted_condition_data = condition_data.sort_values(ascending=False)
    colors = [color_mapping[genus] for genus in sorted_condition_data.index]
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
    plt.savefig(f'gg-pie_chart_{condition}_genera.pdf', bbox_inches='tight')
    plt.show()

# gráfico de pizza geral
total_percentage = group_others(total_percentage)
sorted_total_percentage = total_percentage.sort_values(ascending=False)
colors = [color_mapping[genus] for genus in sorted_total_percentage.index]
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
plt.savefig('gg-general_pie_chart_genera.pdf', bbox_inches='tight')
plt.show()
