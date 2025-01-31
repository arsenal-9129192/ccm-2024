import pandas as pd
import matplotlib.pyplot as plt
import random
from matplotlib import font_manager

def group_others(row):
    others = row[row < 1].sum()
    row = row[row >= 1]
    if others > 0:
        if 'Others < 1%' in row.index:
            row['Others < 1%'] += others
        else:
            row['Others < 1%'] = others
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

family_data = pd.read_csv('family-feature-table-hellinger.tsv', sep='\t', skipinitialspace=True)
metadata = pd.read_csv('metadata_backup.tsv', sep='\t')

if '#OTU ID' not in family_data.columns:
    print("Colunas encontradas:", family_data.columns)
    raise ValueError("A coluna '#OTU ID' não foi encontrada. Verifique o cabeçalho do arquivo.")

family_data['#OTU ID'] = family_data['#OTU ID'].str.extract(r'f__([^;]+)')  # Extrair apenas o nome da família
family_data['#OTU ID'] = family_data['#OTU ID'].fillna('Unclassified')
family_data = family_data.set_index('#OTU ID').T
family_data['condition'] = family_data.index.map(metadata.set_index('sample-id')['condition'])

grouped_data = family_data.groupby('condition').sum()
grouped_percentage = grouped_data.div(grouped_data.sum(axis=1), axis=0) * 100

with pd.ExcelWriter('condition_rankings_family.xlsx') as writer:
    for condition in grouped_data.index:
        condition_data = pd.DataFrame({
            'Abundance': grouped_data.loc[condition],
            'Percentage': grouped_percentage.loc[condition]
        }).sort_values(by='Percentage', ascending=False)
        condition_data.to_excel(writer, sheet_name=condition)

total_abundance = family_data.drop(columns='condition').sum()
total_percentage = total_abundance / total_abundance.sum() * 100
total_percentage = total_percentage.dropna()  # Remover valores NaN
general_ranking = pd.DataFrame({
    'Abundance': total_abundance,
    'Percentage': total_percentage
}).sort_values(by='Percentage', ascending=False)
general_ranking.to_csv('general_ranking_family.csv')

print("Arquivos CSV gerados com sucesso.")

grouped_mean = family_data.groupby('condition').mean()
grouped_normalized = grouped_mean.div(grouped_mean.sum(axis=1), axis=0) * 100
grouped_normalized = grouped_normalized.dropna(how='all')  # Remover linhas completamente NaN

if grouped_normalized.columns.duplicated().any():
    print("Duplicate columns found before applying group_others:", grouped_normalized.columns[grouped_normalized.columns.duplicated()])

grouped_normalized = grouped_normalized.apply(group_others, axis=1)

grouped_normalized.columns = pd.Index([f"{col}_{i}" if col in grouped_normalized.columns[:i] else col for i, col in enumerate(grouped_normalized.columns)])

if grouped_normalized.columns.duplicated().any():
    print("Duplicate columns found after applying group_others:", grouped_normalized.columns[grouped_normalized.columns.duplicated()])

sorted_families = grouped_normalized.sum(axis=0).sort_values(ascending=False).index
grouped_normalized = grouped_normalized[sorted_families]

grouped_normalized = grouped_normalized.loc[grouped_normalized.sum(axis=1).sort_values(ascending=False).index]

columns = [col for col in grouped_normalized.columns if col != 'Others < 1%'] + ['Others < 1%']
grouped_normalized = grouped_normalized[columns]

unique_families = grouped_normalized.columns.tolist()
if 'Others < 1%' not in unique_families:
    unique_families.append('Others < 1%')

color_mapping = get_random_colors(unique_families)

color_mapping['Others < 1%'] = 'dimgray'  # Cor cinza escuro para 'Others < 1%'

plt.figure(figsize=(20, 10))
bars = []
for i, family in enumerate(grouped_normalized.columns):
    bar = plt.bar(
        grouped_normalized.index,
        grouped_normalized[family],
        bottom=grouped_normalized.iloc[:, :i].sum(axis=1),
        color=color_mapping[family],
        edgecolor='black',
        label=family
    )
    bars.append(bar)

    for j, value in enumerate(grouped_normalized[family]):
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

plt.title('Relative Abundance of Families by Condition', fontsize=16, fontproperties=prop)
plt.xlabel('Condition', fontsize=14, fontproperties=prop)
plt.ylabel('% Relative Abundance', fontsize=14, fontproperties=prop)
plt.xticks(rotation=45, ha='right', fontproperties=prop)
plt.legend(title='Families', bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=10, prop=prop)
plt.tight_layout(rect=[0, 0, 0.85, 1])
plt.savefig('stacked_bar_chart_family.pdf', bbox_inches='tight')
plt.show()

for condition in grouped_normalized.index:
    condition_data = grouped_normalized.loc[condition].dropna()  # Remover valores NaN
    condition_data = group_others(condition_data)  # Garantir agrupamento de famílias menores
    sorted_condition_data = condition_data.sort_values(ascending=False)
    colors = [color_mapping[family] for family in sorted_condition_data.index]
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
    plt.title(f'Relative Abundance of Families - {condition}', fontsize=14, fontproperties=prop)
    plt.tight_layout()
    plt.savefig(f'pie_chart_{condition}_family.pdf', bbox_inches='tight')
    plt.show()

total_percentage = group_others(total_percentage)  # Garantir agrupamento de famílias menores
sorted_total_percentage = total_percentage.sort_values(ascending=False)
colors = [color_mapping[family] for family in sorted_total_percentage.index]
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
plt.title('Relative Abundance of Families - General', fontsize=14, fontproperties=prop)
plt.tight_layout()
plt.savefig('general_pie_chart_family.pdf', bbox_inches='tight')
plt.show()
