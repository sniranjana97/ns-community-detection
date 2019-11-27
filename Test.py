
import networkx as nx
from networkx.algorithms.community import greedy_modularity_communities
import csv
import numpy as np
csv_file = '/Users/niranjanas/Desktop/Data.csv'
G = nx.Graph()
file = open(csv_file, 'r')
for line in file:
    source = line.split(',')[0]
    destination = line.split(',')[1]
    G.add_edge(source,destination)
file.close()

c = list(greedy_modularity_communities(G))

with open('subgraph_comm.csv', 'w') as writeFile:
        writer = csv.writer(writeFile)
        writer.writerow(c)
        writeFile.close()

