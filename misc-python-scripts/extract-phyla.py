import pandas as pd

file_path = "phyla-feature-table.tsv"
df = pd.read_csv(file_path, sep="\t")

phyla = df.iloc[:, 0].unique()

output_path = "phyla_list.txt"
with open(output_path, "w") as f:
    for phylum in phyla:
        f.write(phylum + "\n")

print(f"Filos extraídos e salvos em {output_path}")
