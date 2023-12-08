import streamlit as st
import time, json
import numpy as np
import altair as alt
import pandas as pd
import Robogame as rg
import networkx as nx 
import time, json
import matplotlib.pyplot as plt
# from graphviz import Digraph
import io
from PIL import Image
from pyvis.network import Network
import streamlit.components.v1 as components
from stvis import pv_static

# Main content
st.set_page_config(page_title="Robogame", layout="wide")
st.title('Robogame Dashboard')

# let's create two "spots" in the streamlit view for our charts
status = st.empty()

# create the game, and mark it as ready
<<<<<<< Updated upstream
game = rg.Robogame("bgklt") # our team's secret
=======
# game = rg.Robogame("match12") # our team's secret
game = rg.Robogame("match12", server="roboviz.games", port=5000)
>>>>>>> Stashed changes
game.setReady()

## Set bet
# Save or read allBets to a text file to avoid losing our input
def save_to_file(allBets, file_path='allBets.txt'):
    with open(file_path, 'w') as file:
        for robot_id, value in allBets.items():
            file.write(f"{robot_id}: {value}\n")

def read_from_file(file_path='allBets.txt'):
	with open(file_path, 'r') as file:
		for line in file:
			parts = line.strip().split(':')
			robot_id = parts[0].strip()
			value = int(parts[1].strip())
			allBets[robot_id] = value

def reset_bids():
    allBets = {}
    for i in np.arange(0, 100):
        allBets[int(i)] = int(50)  # initially bet 50
    game.setBets(allBets)
    save_to_file(allBets)
    st.success('All bids have been reset.')

allBets = {}
try:
	read_from_file()
except:
	for i in np.arange(0,100):
		allBets[int(i)] = int(50) # initially bet 50

game.setBets(allBets)
save_to_file(allBets)

# Sidebar on the left
side = st.sidebar
with side:
	## Search
	with st.form("search-form"):
		st.subheader('Search Robot')
		searchID = st.number_input('Robot ID', value = None, step=1)
		searchButton = st.form_submit_button("Search")
		if searchID and searchButton:
			st.write("Search for: ", searchID)
	## Bid
	with st.form("bid-form"):
		st.subheader('Bid')
		bidID = st.number_input('Bid For Robot ID', value = None, step=1)
		bidVal = st.number_input('Value', value = None, step=1)
		bidButton = st.form_submit_button("Bid")
		if bidButton:
			st.write("You set bet for: ", bidID, " with ", bidVal)
			allBets[bidID] = bidVal
			game.setBets(allBets)
			save_to_file(allBets)
	
	st.subheader('Our bids')
	bidResetButton = st.button("Reset All Bids")
	if bidResetButton:
		st.warning('Are you sure you want to reset all bids to 50?', icon="⚠️")
			# Using columns for better layout
		buttonCol1, buttonCol2 = st.columns(2)

		with buttonCol1:
			yesResetButton = st.button("Reset", key="yes_reset", help="Click to reset", on_click=lambda: reset_bids(), type="primary")
		
		with buttonCol2:
			noResetButton = st.button("Cancel", key="cancel_reset", help="Click to cancel")

	read_from_file()
	df = pd.DataFrame({'Robot ID': list(allBets.keys()), 'Value': list(allBets.values())})
	df.set_index('Robot ID', inplace=True)
	bid = st.table(df)

# grid layout
col1, col2, col3 = st.columns([2, 2, 1])
with col1:
	
	container1 = st.container()
	container2 = st.container()
	container5 = st.container()

	with container1:
		st.subheader("Social Network")
		viz1 = st.empty()

	with container2:
		st.subheader("Family Tree")
		viz2 = st.empty()

		# #Family Tree
		# family = game.getTree()
		# fam_net = nx.tree_graph(family)
		# graph = Digraph(format='png')
		
		# for node in fam_net.nodes:
		# 	graph.node(str(node))
		# for edge in fam_net.edges:
		# 	graph.edge(str(edge[0]), str(edge[1]))
        # # Render the Graphviz Digraph to a PNG image
		# png_data = graph.pipe(format='png')
		# image = Image.open(io.BytesIO(png_data))
		# viz5 = st.image(image, use_column_width=True, width=800)

with col2:
	
	container3 = st.container()
	container4 = st.container()	

	with container3:
		st.subheader("Number Generator")
		viz3 = st.empty()

	with container4:
		st.subheader("Productivity Heatmap")
		viz4 = st.empty()

df = []
with col3:
	st.subheader('Team Status')
	team_table = st.table(df)

# wait for both players to be ready
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
	
	# Friendship Network
	robots = game.getRobotInfo()
	network = game.getNetwork()
	social_net = nx.node_link_graph(network)
	
	# Get the node winner values and colors
	node_winner_values = {node: robots.loc[robots['id'] == node, 'winner'].values[0] for node in social_net.nodes}
	node_colors = {1: 'green', 2: 'red', -2: 'blue'}
	colors = [node_colors.get(node_winner_values.get(node, 0), 'gray') for node in social_net.nodes]
	
	# Draw the network graph
	fig, ax = plt.subplots()
	nx.draw_kamada_kawai(social_net, with_labels=True, node_color=colors, ax=ax)
	
	# Update the visualization in container1
	viz1.pyplot(fig)

	# network = game.getNetwork()
	# robots = game.getRobotInfo()

	# links = network['links']
	# df = pd.DataFrame(links, columns=['source', 'target'])
	# G = nx.from_pandas_edgelist(df, source='source', target='target')
	# net = Network(notebook=False, height='300px', width='300px',heading='')

	# node_winner_values = {node: robots.loc[robots['id'] == node, 'winner'].values[0] for node in G.nodes}
	# # node_colors = {1: '#f38375', 2: '#8fb8ed', -2: '#686963'}
	# node_colors = {1: 'green', 2: 'red', -2: 'blue'}

	# nodes_list = list(G.nodes)

	# for node in G.nodes:
	# 	net.add_node(node, label=str(node), color=node_colors[node_winner_values[node]])

	# net.from_nx(G)
	# pv_static(net)

	# viz1.write(net)
	# st.pyplot(net.show(notebook=False))
	# viz1.write(net.show('network.html'))

	# sleep 6 seconds
	for t in np.arange(0,4):
		status.write("Seconds to next hack: " + str(6-t))
		time.sleep(1)

	# update the hints
	game.getHints()

	## Team Status
	team_counts = robots['winningTeam'].value_counts()
	team_counts = pd.DataFrame(team_counts, columns=['count'])
	team_counts = team_counts.sort_values(by='count', ascending=False)
	team_table.write(team_counts)

	# ## Productivity heatmap

	# part_hints=game.getAllPartHints()
        
    # # Put id, productivity, parts into {}
	# df = pd.DataFrame()
	# for hint in part_hints:
	# 	column_name = hint['column']
	# 	id_value = hint['id']
	# 	value = hint['value']
	# 	if id_value not in df.index:
	# 		new_row = pd.Series(name=id_value, dtype='object')
	# 		new_row[column_name] = value
	# 		df = pd.concat([df, new_row.to_frame().T])
	# df = df.reset_index().rename(columns={'index': 'id'})
	# D = pd.merge(robots[['id', 'Productivity']], df, on='id')
    
	# # Clean up df without id
	# melted_data = pd.melt(D, id_vars=['id'], var_name='Parts', value_name='value')
	# wide_data = melted_data.pivot(index=['id'], columns='Parts', values='value').reset_index()
	# df = pd.DataFrame(wide_data.to_dict(orient='list'))
	# new_df = df.drop('id', axis=1)

	# # Create correlation matrix
	# correlation_matrix = new_df.corr(numeric_only=True).stack().reset_index(name='correlation').rename(columns={'level_0': 'x', 'level_1': 'y'})

	# # Sort the values to position 'productivity' at the top of y-axis and x-axis
	# sort_order = ['Productivity']+ sorted(df.columns.drop('Productivity'))
	# correlation_matrix['x'] = pd.Categorical(correlation_matrix['x'], categories=sort_order, ordered=True)
	# correlation_matrix['y'] = pd.Categorical(correlation_matrix['y'], categories=sort_order, ordered=True)

	# chart = alt.Chart(correlation_matrix).mark_rect().encode(
    # 	x=alt.X('x:O', sort=sort_order, title='Parts'), y=alt.Y('y:O', sort=sort_order, title='Parts'), color='correlation:Q'
	# )

	# text = alt.Chart(correlation_matrix).mark_text(baseline='middle').encode(
    # 	x=alt.X('x:O', sort=sort_order), y=alt.Y('y:O', sort=sort_order), text=alt.Text('correlation:Q', format='.2f'), color=alt.condition(
    #     alt.datum.correlation > 0.5, alt.value('white'), alt.value('black'))
	# )

<<<<<<< Updated upstream
	heatmap = (chart + text).properties(
		width=700, height=700
	)
=======
	# heatmap = (chart + text).properties(
	# 	width=500, height=500
	# )
>>>>>>> Stashed changes

	## Robot Num Generator

	# create a dataframe for the time prediction hints
	df1 = pd.DataFrame(game.getAllPredictionHints())

	# if it's not empty, let's get going
	if (len(df1) > 0):

		selection = alt.selection_point(on='mouseover', nearest=True)
		color = alt.condition(
			selection,
			alt.Color('id:N').title("Robot ID").legend(orient="bottom"),
			alt.value('lightgray')
		)
		base3 = alt.Chart(df1).mark_circle().encode(
			alt.X('time:Q'),
			alt.Y('value:Q'),
			color=color
			#tooltip=['time', 'value', "id"]
		).add_selection(
			selection
		)
		line = base3.transform_regression('time', 'value', method="poly").mark_line()
		num = base3 + line

		# write it to the screen
		viz3.write(num)


	# get the parts
	df2 = pd.DataFrame(game.getAllPartHints())

	# we'll want only the quantitative parts for this
	# the nominal parts should go in another plot
	quantProps = ['Astrogation Buffer Length','InfoCore Size',
		'AutoTerrain Tread Count','Polarity Sinks',
		'Cranial Uplink Bandwidth','Repulsorlift Motor HP',
		'Sonoreceptors']

	# if it's not empty, let's get going
	if (len(df2) > 0):
		df2 = df2[df2['column'].isin(quantProps)]
		c2 = alt.Chart(df2).mark_circle().encode(
			alt.X('column:N'),
			alt.Y('value:Q',scale=alt.Scale(domain=(-100, 100)))
		)
		# partVis.write(c2)
		viz2.write("Family tree")
		viz4.write(c2)