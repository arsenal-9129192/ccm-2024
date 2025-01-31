import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from sklearn.preprocessing import normalize

plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Arial', 'DejaVu Sans', 'Helvetica']  # Fontes padrão

pathway_data = pd.read_csv('pathway_abundance_no_header.tsv', sep='\t')
metadata = pd.read_csv('metadata_backup.tsv', sep='\t')

if '#OTU ID' not in pathway_data.columns:
    print("Colunas encontradas:", pathway_data.columns)
    raise ValueError("A coluna '#OTU ID' não foi encontrada.")

raw_data = pathway_data.set_index('#OTU ID').copy()
pathway_data_t = pathway_data.set_index('#OTU ID').T

hellinger_data = pd.DataFrame(
    normalize(np.sqrt(pathway_data_t), norm='l2'),
    columns=pathway_data_t.columns,
    index=pathway_data_t.index
)

raw_means = raw_data.mean()
relative_abundance = (raw_means / raw_means.sum()) * 100

results_df = pd.DataFrame({
    'Pathway_ID': raw_means.index,
    'Raw_Abundance': raw_means.values,
    'Relative_Abundance': relative_abundance.values
})

results_df = results_df.sort_values('Relative_Abundance', ascending=False)
results_df.to_csv('pathway_analysis_general.csv', index=False)

def plot_horizontal_bar(data, names, title, filename):
    plt.figure(figsize=(15, max(8, len(data)*0.3)))
    
    y_pos = np.arange(len(data))
    
    bars = plt.barh(y_pos, data, color='skyblue', edgecolor='black', linewidth=0.8)
    
    for i, v in enumerate(data):
        plt.text(v, i, f' {v:.2f}%', va='center')
    
    plt.title(title, fontsize=16)
    plt.xlabel('Relative Abundance (%)', fontsize=14)
    plt.ylabel('Pathway', fontsize=14)
    
