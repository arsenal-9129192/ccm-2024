import networkx as nx

G = nx.read_gml('genus-exported-network/network.gml')

for node in G.nodes(data=True):
    label = node[1].get('label', '')
    
    phyla = ''
    family = ''
    
    taxonomic_levels = label.split(';')
    
    for level in taxonomic_levels:
        if level.startswith('p__'):
            phyla = level
        elif level.startswith('f__'):
            family = level
    
    G.nodes[node[0]]['phyla'] = phyla
    G.nodes[node[0]]['family'] = family

nx.write_gml(G, 'genus-exported-network/genus_modified_network.gml')
