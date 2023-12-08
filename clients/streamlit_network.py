import Robogame as rg
import networkx as nx
import altair as alt
import pandas as pd
import numpy as np
from pyvis.network import Network

game = rg.Robogame("bob")
game.setReady()

network = game.getNetwork()
robots = game.getRobotInfo()

links = network['links']
df = pd.DataFrame(links, columns=['source', 'target'])
G = nx.from_pandas_edgelist(df, source='source', target='target')

net = Network(notebook = True)

node_winner_values = {node: robots.loc[robots['id'] == node, 'winner'].values[0] for node in G.nodes}
node_colors = {1: '#686963', 2: '#8fb8ed', -2: '#f38375'}

nodes_list = list(G.nodes)

for node in G.nodes:
    net.add_node(node, label=str(node), color=node_colors[node_winner_values[node]])

net.from_nx(G)
net.show("network.html")