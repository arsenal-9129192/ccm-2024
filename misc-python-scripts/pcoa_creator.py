import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
from matplotlib.font_manager import FontProperties

pcoa_data = pd.read_csv('ordination.txt', sep='\t', skiprows=9, index_col=0)

pcoa_data = pcoa_data.iloc[:, :3]
pcoa_data.columns = ['PC1', 'PC2', 'PC3']

metadata = pd.read_csv('/home/ubuntu/ccmnovo/metadata_backup.tsv', sep='\t', index_col='sample-id')

merged_data = pcoa_data.join(metadata['condition'])

nan_samples = merged_data[merged_data['condition'].isna()]
print("Samples with 'NaN' condition:")
print(nan_samples)

merged_data = merged_data.dropna(subset=['condition'])

font_path = '/home/ubuntu/ccmnovo/ArialNova.ttf'
font_prop = FontProperties(fname=font_path)

with open('ordination.txt', 'r') as f:
    lines = f.readlines()
    proportion_explained = [float(x) for x in lines[1].strip().split('\t')[1:4]]

plt.figure(figsize=(10, 8))

conditions = merged_data['condition'].unique()
colors = plt.cm.rainbow(np.linspace(0, 1, len(conditions)))
color_dict = dict(zip(conditions, colors))

for condition in conditions:
    subset = merged_data[merged_data['condition'] == condition]
    plt.scatter(subset['PC1'], subset['PC2'], 
                label=condition, color=color_dict[condition], s=50, edgecolor='k')

plt.xlabel(f'PC1 ({proportion_explained[0]:.2f}% variance explained)', fontproperties=font_prop)
plt.ylabel(f'PC2 ({proportion_explained[1]:.2f}% variance explained)', fontproperties=font_prop)
plt.title('2D PCoA Plot (Bray-Curtis)', fontproperties=font_prop)
plt.legend(title='Condition', prop=font_prop)

plt.savefig('pcoa_2d_plot.pdf', dpi=300, bbox_inches='tight')

fig = plt.figure(figsize=(10, 8))
ax = fig.add_subplot(111, projection='3d')

for condition in conditions:
    subset = merged_data[merged_data['condition'] == condition]
    ax.scatter(subset['PC1'], subset['PC2'], subset['PC3'], 
               label=condition, color=color_dict[condition], s=50, edgecolor='k')

ax.set_xlabel(f'PC1 ({proportion_explained[0]:.2f}% variance explained)', fontproperties=font_prop)
ax.set_ylabel(f'PC2 ({proportion_explained[1]:.2f}% variance explained)', fontproperties=font_prop)
ax.set_zlabel(f'PC3 ({proportion_explained[2]:.2f}% variance explained)', fontproperties=font_prop)
ax.set_title('3D PCoA Plot (Bray-Curtis)', fontproperties=font_prop)
ax.legend(title='Condition', prop=font_prop)

plt.savefig('pcoa_3d_plot.pdf', dpi=300, bbox_inches='tight')

plt.show()
