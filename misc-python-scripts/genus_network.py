import pandas as pd
from SCNIC import make_network, calculate_correlations

data = pd.read_csv('exported-genus-table/feature-table.biom', sep='\t', index_col=0)

correlations = calculate_correlations(data, method='spearman')

network = make_network(correlations, min_r=0.5, min_p=0.05)

network.write_graphml('network.graphml')
