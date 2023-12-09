import Robogame as rg
import networkx as nx
import altair as alt
import pandas as pd
import numpy as np
from pyvis.network import Network
import time, json
import streamlit as st
from streamlit.components.v1 import html as components_html

# Main content
st.set_page_config(page_title="Robogame", layout="wide")
st.title('Robogame Dashboard')

# let's create two "spots" in the streamlit view for our charts
status = st.empty()
viz1 = st.empty()

game = rg.Robogame("bob")
game.setReady()

while(True):	
	gametime = game.getGameTime()
	timetogo = gametime['gamestarttime_secs'] - gametime['servertime_secs']
	
	if ('Error' in gametime):
		status.write("Error"+str(gametime))
		break
	if (timetogo <= 0):
		status.write("Let's go!")
		break
	status.write("waiting to launch... game will start in " + str(int(timetogo)))
	time.sleep(1) # sleep 1 second at a time, wait for the game to start

# run 100 times
for i in np.arange(0,101):
	
    network = game.getNetwork()
    robots = game.getRobotInfo()

    links = network['links']
    df = pd.DataFrame(links, columns=['source', 'target'])
    G = nx.from_pandas_edgelist(df, source='source', target='target')

    net = Network(notebook = True)

    node_winner_values = {node: robots.loc[robots['id'] == node, 'winner'].values[0] for node in G.nodes}
    node_colors = {1: '#f38375', 2: '#8fb8ed', -2: '#686963'} # Team 1: #f38375 (red), Team 2: #8fb8ed (blue), Unassigned: #686963 (grey)

    # Count occurrences for each source and target separately
    count_source = df.groupby('source')['target'].count().reset_index(name='count_source')
    count_target = df.groupby('target')['source'].count().reset_index(name='count_target')
    friends_counts = pd.merge(count_source, count_target, how='outer', left_on='source', right_on='target')
    friends_counts = friends_counts.fillna(0)
    friends_counts['counts'] = friends_counts['count_source'] + friends_counts['count_target']
    friends_counts = pd.DataFrame(friends_counts)

    normalized_counts = friends_counts['counts'] / friends_counts['counts'].max()
    rounded_counts = (normalized_counts * 100).round().astype(int)

    nodes_list = list(G.nodes)

    # for node, (index, row) in zip(G.nodes, friends_counts.iterrows()):
    #     net.add_node(node, label=str(node), color=node_colors[node_winner_values[node]], size=int(rounded_counts.loc[index]))
    for node in G.nodes:
        source_matches = friends_counts[friends_counts['source'] == node]
        if not source_matches.empty:
            row = source_matches.iloc[0]
            net.add_node(node, label=str(node), color=node_colors[node_winner_values[node]], size=int(rounded_counts[row.name]))


    net.from_nx(G)
    html_path = "network.html"
    net.write_html(html_path)

    HtmlFile = open(html_path, 'r', encoding='utf-8')
    source_code = HtmlFile.read() 
    
    # Update viz1 every 1 minute
    if i % 10 == 0:
        viz1.empty()
        viz1 = components_html(source_code, width=800, height=800, scrolling=True)

    # sleep 6 seconds
    for t in np.arange(0,6):
        status.write("Seconds to next hack: " + str(6-t))
        time.sleep(1)
	