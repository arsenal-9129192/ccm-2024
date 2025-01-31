import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib import font_manager

alpha_diversity_data = pd.read_csv('alpha_significance_rawdata.tsv', sep='\t', comment='#')

font_path = 'ArialNova.ttf'
font_manager.fontManager.addfont(font_path)
plt.rcParams['font.family'] = 'Arial Nova'

plt.figure(figsize=(10, 6))
sns.violinplot(x='condition', y='shannon_entropy', data=alpha_diversity_data, palette='rainbow')
plt.title('Violin Plot of Shannon Entropy by Condition', fontsize=14)
plt.xlabel('Condition', fontsize=12)
plt.ylabel('Shannon Entropy', fontsize=12)
plt.xticks(rotation=45)
plt.tight_layout()

# Salvar gráfico
plt.savefig('alpha_diversity_violin_plot.pdf')
plt.show()
