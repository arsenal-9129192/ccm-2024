import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np

alpha_diversity_data = pd.read_csv('alpha_significance_rawdata.tsv', sep='\t', comment='#')

plt.figure(figsize=(10, 6))

conditions = alpha_diversity_data['condition'].unique()
colors = plt.cm.rainbow(np.linspace(0, 1, len(conditions)))
color_dict = dict(zip(conditions, colors))

sns.violinplot(x='condition', y='shannon_entropy', data=alpha_diversity_data, palette=color_dict)

plt.title('Violin Plot of Shannon Entropy by Condition')
plt.xlabel('Condition')
plt.ylabel('Shannon Entropy')
plt.xticks(rotation=45)
plt.tight_layout()

plt.savefig('alpha_diversity_violin_plot.pdf', dpi=300, bbox_inches='tight')
plt.show()
