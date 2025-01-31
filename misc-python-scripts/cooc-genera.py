import pandas as pd

feature_table = pd.read_csv("gg-genera-feature-table-hellinger.tsv", sep="\t", index_col=0)
metadata = pd.read_csv("metadata_backup.tsv", sep="\t")

common_samples = set(feature_table.columns).intersection(metadata['sample-id'])
metadata = metadata[metadata['sample-id'].isin(common_samples)]

condition_groups = metadata['condition'].unique()

genera_by_group = {group: set() for group in condition_groups}

for group in condition_groups:
    samples_in_group = metadata[metadata['condition'] == group]['sample-id']
    
    group_feature_table = feature_table[samples_in_group]
    
    genera_in_group = group_feature_table[group_feature_table >= 0.001].dropna(how='all').index
    genera_in_group = [genus.split(';')[-1].replace('g__', '') for genus in genera_in_group]
    
    genera_by_group[group].update(genera_in_group)

common_genera = set.intersection(*genera_by_group.values())

with open("cooc-genera.txt", "w") as f:
    for genus in sorted(common_genera):
        f.write(f"{genus}\n")

print(f"Arquivo 'cooc-genera.txt' criado com {len(common_genera)} gêneros comuns.")
