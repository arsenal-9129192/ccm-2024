import pandas as pd
import numpy as np

data = pd.read_csv("gg-genera-feature-table.tsv", sep='\t', skiprows=1, index_col=0)

data_hellinger = data.apply(np.sqrt)

data_hellinger.to_csv("gg-genera-feature-table-hellinger.tsv", sep='\t')
