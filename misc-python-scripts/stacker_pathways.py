import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from openpyxl import Workbook
import matplotlib.font_manager as fm

available_colors = [
    "lightcoral", "indianred", "firebrick", "red", "salmon", "coral", 
    "orangered", "peru", "yellow", "yellowgreen", "greenyellow", "chartreuse",
    "palegreen", "lightblue", "powderblue", "aqua", "dodgerblue", "purple",
    "violet", "deeppink", "hotpink", "mediumvioletred", "blue", "slateblue",
    "turquoise", "lightseagreen", "seagreen", "mediumpurple", "orange",
    "moccasin", "gold", "khaki", "navajowhite"
]

font_path = 'ArialNova.ttf'
fm.fontManager.addfont(font_path)
plt.rcParams['font.family'] = 'Arial Nova'

def read_data():
    pathways = pd.read_csv('pathway_abundance_no_header.tsv', sep='\t')
    metadata = pd.read_csv('metadata_backup.tsv', sep='\t')
    
    pathways = pathways.rename(columns={'#OTU ID': 'pathway'})
    
    return pathways, metadata

def hellinger_transform(df):
    abundance_cols = df.drop('pathway', axis=1)
    
    transformed = np.sqrt(abundance_cols.div(abundance_cols.sum()))
    
    transformed.insert(0, 'pathway', df['pathway'])
    
    return transformed

def get_top_pathways(df, n=20):
    abundance_means = df.drop('pathway', axis=1).mean(axis=1)
    top_indices = abundance_means.nlargest(n).index
    
    return df.iloc[top_indices].reset_index(drop=True)

def get_pathway_colors(pathways):
    return {pathway: available_colors[i % len(available_colors)] 
            for i, pathway in enumerate(pathways)}

def create_bar_plot(df, pathway_colors, title, output_file):
    plt.figure(figsize=(10, 5))  # Ajustar para maior largura e menor altura
    
    means = df.drop('pathway', axis=1).mean(axis=1) * 100  # Converter para porcentagem
    pathways = df['pathway'].values
    
    bars = plt.barh(range(len(means)), means, 
                    color=[pathway_colors[pathway] for pathway in pathways])
    
    for i, bar in enumerate(bars):
        bar.set_edgecolor('black')
        bar.set_linewidth(1)
        width = bar.get_width()
        plt.text(width, bar.get_y() + bar.get_height()/2., 
                 f'{width:.2f}%', 
                 ha='left', va='center')
    
    plt.yticks(range(len(pathways)), pathways)
    plt.title(title)
    plt.xlabel('Abundância Relativa (%)')
    plt.tight_layout()
    
    plt.savefig(output_file, format='pdf')
    plt.close()

def create_stacked_bar_plot(df, metadata, pathway_colors, output_file):
    condition_groups = {}
    for sample in df.columns[1:]:
        if sample in metadata['sample-id'].values:
            condition = metadata[metadata['sample-id'] == sample]['condition'].iloc[0]
            if condition not in condition_groups:
                condition_groups[condition] = []
            condition_groups[condition].append(sample)
    
    condition_means = pd.DataFrame()
    for condition, samples in condition_groups.items():
        condition_means[condition] = df[samples].mean(axis=1) * 100  # Converter para porcentagem
    
    plt.figure(figsize=(15, 8))
    
    condition_means.index = df['pathway']
    
    bottom = np.zeros(len(condition_means.columns))
    for pathway in df['pathway']:
        values = condition_means.loc[pathway]
        plt.bar(range(len(condition_means.columns)), values, bottom=bottom, 
                label=pathway, color=pathway_colors[pathway],
                edgecolor='black', linewidth=1)
        
        for i, v in enumerate(values):
            plt.text(i, bottom[i] + v/2, f'{v:.2f}%',
                    ha='center', va='center')
        bottom += values
    
    plt.xticks(range(len(condition_means.columns)), condition_means.columns, rotation=45)
    plt.title('Abundância Relativa por Condição')
    plt.ylabel('Abundância Relativa (%)')
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    
    plt.savefig(output_file, format='pdf', bbox_inches='tight')
    plt.close()

def create_excel_rankings(df, metadata, output_file):
    writer = pd.ExcelWriter(output_file, engine='openpyxl')
    
    condition_groups = {}
    for sample in df.columns[1:]:
        if sample in metadata['sample-id'].values:
            condition = metadata[metadata['sample-id'] == sample]['condition'].iloc[0]
            if condition not in condition_groups:
                condition_groups[condition] = []
            condition_groups[condition].append(sample)
    
    for condition, samples in condition_groups.items():
        condition_data = df[['pathway'] + samples].copy()
        
        condition_data['mean'] = condition_data[samples].mean(axis=1)
        condition_data = condition_data.sort_values('mean', ascending=False)
        
        condition_data.to_excel(writer, sheet_name=condition, index=False)
    
    writer.close()

def create_csv_rankings(df, output_file):
    raw_abundances = df.drop('pathway', axis=1).sum(axis=1)
    
    relative_abundances = raw_abundances / raw_abundances.sum() * 100
    
    rankings = pd.DataFrame({
        'Pathway': df['pathway'],
        'Raw_Abundance': raw_abundances,
        'Relative_Abundance': relative_abundances
    })
    
    rankings = rankings.sort_values('Relative_Abundance', ascending=False)
    
    rankings['Relative_Abundance'] = rankings['Relative_Abundance'].apply(lambda x: f'{x:.2f}')
    
    rankings.to_csv(output_file, index=False)

def main():
    pathways, metadata = read_data()
    
    transformed_data = hellinger_transform(pathways)
    
    top_20_pathways = get_top_pathways(transformed_data, 20)
    
    pathway_colors = get_pathway_colors(top_20_pathways['pathway'])
    
    create_bar_plot(top_20_pathways, pathway_colors, 'Top 20 Rotas Metabólicas', 'top_20_pathways.pdf')
    
    create_stacked_bar_plot(top_20_pathways, metadata, pathway_colors, 'stacked_pathways.pdf')
    
    create_excel_rankings(transformed_data, metadata, 'pathway_rankings.xlsx')
    
    create_csv_rankings(transformed_data, 'pathway_rankings.csv')

if __name__ == "__main__":
    main()
