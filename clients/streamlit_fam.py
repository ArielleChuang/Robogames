import Robogame as rg
import networkx as nx
import altair as alt
import pandas as pd
import numpy as np
from pyvis.network import Network
import igraph
from igraph import Graph, EdgeSeq

game = rg.Robogame("bob")
game.setReady()

fam = game.getTree()
fam_net = nx.tree_graph(fam)