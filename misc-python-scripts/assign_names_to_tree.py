import pandas as pd

taxonomy_df = pd.read_csv('exported-taxonomy/taxonomy.tsv', sep='\t', index_col=0)

with open('exported-tree/tree.nwk', 'r') as file:
    newick_tree = file.read()

for feature_id, row in taxonomy_df.iterrows():
    taxonomic_name = row['Taxon']
    newick_tree = newick_tree.replace(feature_id, taxonomic_name)

with open('exported-tree/tree_with_taxonomic_names.nwk', 'w') as file:
    file.write(newick_tree)
