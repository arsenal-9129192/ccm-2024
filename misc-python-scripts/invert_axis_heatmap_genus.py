import pandas as pd

data = pd.read_csv("feature-table.tsv", sep='\t', skiprows=1, index_col=0)

transposed_data = data.T

transposed_data.to_csv("transposed-feature-table.tsv", sep='\t')
