import networkx as nx
import matplotlib.pyplot as plt
from matplotlib import font_manager

font_path = 'ArialNova.ttf'  # Ensure this file is in the same directory as the script
font_prop = font_manager.FontProperties(fname=font_path)

font_manager.fontManager.addfont(font_path)
plt.rcParams['font.family'] = font_prop.get_name()

data = {
    'SLUDGE': {
        'Pollutant Degradation': 4,
        'Lipid Biosynthesis': 3,
        'Carbohydrate Biosynthesis': 2,
        'Amino Acid Metabolism': 2,
        'Energy Metabolism': 4,
        'Specialized Compound Biosynthesis': 5
    },
    'FISH': {
        'Energy Metabolism': 1,
        'Specialized Compound Biosynthesis': 1
    },
    'SEDIMENTS': {
        'Specialized Compound Biosynthesis': 1
    },
    'SOIL': {
        'Amino Acid Metabolism': 1
    }
}

G = nx.Graph()

for condition, categories in data.items():
    G.add_node(condition, type='condition')
    for category, count in categories.items():
        G.add_node(category, type='category')
        G.add_edge(condition, category, weight=count)

pos = nx.spring_layout(G, seed=42)

plt.figure(figsize=(12, 8))

nx.draw_networkx_nodes(
    G, pos,
    nodelist=[n for n, attr in G.nodes(data=True) if attr['type'] == 'condition'],
    node_color='lightblue', node_size=3000, edgecolors='black', linewidths=1.5
)
nx.draw_networkx_nodes(
    G, pos,
    nodelist=[n for n, attr in G.nodes(data=True) if attr['type'] == 'category'],
    node_color='lightgreen', node_size=2000, edgecolors='black', linewidths=1.5
)

nx.draw_networkx_edges(
    G, pos,
    width=[d['weight'] for u, v, d in G.edges(data=True)],
    edge_color='gray'
)

nx.draw_networkx_labels(
    G, pos,
    font_size=10,
    font_family=font_prop.get_name()  # Use the custom font
)

plt.title(
    'Relationship Between Conditions and Categories of Exclusive Metabolic Pathways',
    fontsize=16, fontproperties=font_prop
)
plt.axis('off')
plt.tight_layout()
plt.savefig('network_exclusive_pathways.pdf', bbox_inches='tight')
plt.show()
