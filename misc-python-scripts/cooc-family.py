import pandas as pd

feature_table = pd.read_csv("gg-family-feature-table-hellinger.tsv", sep="\t", index_col=0)
metadata = pd.read_csv("metadata_backup.tsv", sep="\t")

common_samples = set(feature_table.columns).intersection(metadata['sample-id'])
metadata = metadata[metadata['sample-id'].isin(common_samples)]

condition_groups = metadata['condition'].unique()

families_by_group = {group: set() for group in condition_groups}

for group in condition_groups:
    samples_in_group = metadata[metadata['condition'] == group]['sample-id']
    
    group_feature_table = feature_table[samples_in_group]
    
    families_in_group = group_feature_table[group_feature_table >= 0.001].dropna(how='all').index
    families_in_group = [family.split(';')[-2].replace('f__', '') for family in families_in_group]
    
    families_by_group[group].update(families_in_group)

common_families = set.intersection(*families_by_group.values())

with open("cooc-family.txt", "w") as f:
    for family in sorted(common_families):
        f.write(f"{family}\n")

print(f"Arquivo 'cooc-family.txt' criado com {len(common_families)} famílias comuns.")
