import streamlit as st
import time
import numpy as np
import altair as alt
import pandas as pd
import Robogame as rg
import networkx as nx 
import time, json
import matplotlib.pyplot as plt
from pyvis.network import Network
from streamlit.components.v1 import html as components_html
from stvis import pv_static

# Main content
st.set_page_config(page_title="Robogame", layout="wide")
st.title('Robogame Dashboard')

# let's create two "spots" in the streamlit view for our charts
status = st.empty()

# create the game, and mark it as ready
game = rg.Robogame("bob") # our team's secret
# game = rg.Robogame("match12", server="roboviz.games", port=5000)
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

# # grid layout
col1, col2 = st.columns([3,1])
with col1:
	container1 = st.container()
	container2 = st.container()
	with container1:
		st.subheader("Number Generator")
		viz1 = st.empty()

	with container2:
		st.subheader("Social Network")
		st.write("⚫️ Grey: Unassigned 🔴 Red: Team1 🔵 Blue: Team2")
		viz2 = st.empty()

df = []
with col2:
	st.subheader("Team Status")
	team_table = st.table(df)
	st.subheader("Productivity Table")
	productivity_table = st.table(df)

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

df_store = pd.DataFrame(game.getAllPredictionHints())

# run 100 times
for i in np.arange(0,101):

	robots = game.getRobotInfo()
	network = game.getNetwork()
	
	## Friendship Network
	
	# initialize network
	links = network['links']
	df = pd.DataFrame(links, columns=['source', 'target'])
	G = nx.from_pandas_edgelist(df, source='source', target='target')
	nodes_list = list(G.nodes)
	net = Network(neighborhood_highlight=True, notebook = True)

	# identify winners - for color
	node_winner_values = {node: robots.loc[robots['id'] == node, 'winner'].values[0] for node in G.nodes}
	node_colors = {1: '#f38375', 2: '#8fb8ed', -2: '#686963'} # Team 1: #f38375 (red), Team 2: #8fb8ed (blue), Unassigned: #686963 (grey)

	# count number of friends - for size
	count_source = df.groupby('source')['target'].count().reset_index(name='count_source')
	count_target = df.groupby('target')['source'].count().reset_index(name='count_target')
	friends_counts = pd.merge(count_source, count_target, how='outer', left_on='source', right_on='target')
	friends_counts = friends_counts.fillna(0)
	friends_counts['counts'] = friends_counts['count_source'] + friends_counts['count_target']
	friends_counts = pd.DataFrame(friends_counts)
	normalized_counts = friends_counts['counts'] / friends_counts['counts'].max()
	rounded_counts = (normalized_counts * 100).round().astype(int)
	node_set = set()

	# Add color abd size onto each node
	#for node in G.nodes:
	for edge in G.edges:	
		source, target = edge
		#print(str(node))
		source_matches = friends_counts[friends_counts['source'] == source]
		#print(source_matches)
		if not source_matches.empty:
			row = source_matches.iloc[0]
			net.add_node(source, label=str(source), color=node_colors[node_winner_values[source]], size=int(rounded_counts[source]))
			net.add_node(target, label=str(target), color=node_colors[node_winner_values[target]], size=int(rounded_counts[target]))
			node_set.add(source)
			#net.add_edge(source_matches['source'], source_matches['target'])
	#for edge in G.edges:
		#source, target = edge
		#if source in node_set and target in node_set:
			net.add_edge(source, target)
	net.from_nx(G)

	# save and read the network
	html_path = "network.html"
	net.write_html(html_path)
	HtmlFile = open(html_path, 'r', encoding='utf-8')
	source_code = HtmlFile.read() 

	# update the network every 30 sec
	if i % 5 == 0:
		viz2.empty()
		viz2 = components_html(source_code, width=1000, height=500, scrolling=False)
	
	game.getHints()

	## Team Status
	team_counts = robots['winningTeam'].value_counts()
	team_counts = pd.DataFrame(team_counts, columns=['count'])
	team_counts = team_counts.sort_values(by='count', ascending=False)
	team_table.write(team_counts)

	## Robot Num Generator

	# create a dataframe for the time prediction hints
	df1 = pd.DataFrame(game.getAllPredictionHints())
	df_store = pd.concat([df_store, df1]).drop_duplicates(subset=['time', 'id', 'value'])
	timenow = game.getGameTime()['curtime']
	df_store['curtime'] = timenow

	# if it's not empty, let's get going
	if (len(df_store) > 0):
		
		nearest = alt.selection_point(on='mouseover', fields=['time', 'value'])
		#selection = alt.selection_point(on='mouseover', fields=['time', 'value'])
		
		color = alt.condition(
			nearest,
			alt.Color('id:N').title("Robot ID").legend(orient="bottom"),
			alt.value('lightgray')
		)
		base3 = alt.Chart(df_store).mark_circle().encode(
			alt.X('time:Q'),
			alt.Y('value:Q'),
			color=color
			#tooltip=['time', 'value', "id"]
		).add_params(
			nearest
		).properties(
			width=1000, height=500
		) 
		#selectors = alt.Chart().mark_point().encode(
		#	x='time:Q',
		#	y='value:Q',
		#	opacity=alt.value(0),
		#).add_params(
		#	nearest
		#)
		degree_list = [3, 5]
		if searchID:
			base3 = base3.transform_filter(
        		alt.datum.id == searchID
			)
		line = base3.transform_regression('time', 'value', method="poly").mark_line().encode(
			alt.Color(legend=None)
		).interactive()
		line2 = base3.transform_regression('time', 'value', method="poly", order=5).mark_line(color="black").encode(
			alt.Color(legend=None)
		).interactive()
		

		#polynomial_fit = [
		#	base3.transform_regression(
		#		"time", "value", method="poly", order=order, as_=["time", str(order)]
		#	)
		#	.mark_line()
		#	.transform_fold([str(order)], as_=["degree", "value"])
		#	.encode(alt.Color("degree:N", legend=None)).interactive()
		#	for order in degree_list
		#]
		vrules = alt.Chart(df_store).mark_rule(color='gray').encode(
			x="curtime:Q"
		)
		num = alt.layer(base3, line, line2, vrules)#*polynomial_fit)
		#points = line.mark_point().encode(
    	#	opacity=alt.condition(nearest, alt.value(1), alt.value(0))
		#)
		#vrules = alt.Chart().mark_rule(color='gray').encode(
		#	x='time:Q',
		#).transform_filter(
		#	nearest
		#)
		#hrules = alt.Chart().mark_rule(color='gray').encode(
		#	y='value:Q',
		#).transform_filter(
		#	nearest
		#)
		#lines = line + selectors + points + vrules + hrules
		#num = base3 + line

		# write it to the screen
		viz1.write(num)

	## Productivity dataframe
	part_hints=game.getAllPartHints()
				
	# # Put id, productivity, parts into {}s
	df = pd.DataFrame()
	for hint in part_hints:
		column_name = hint['column']
		id_value = hint['id']
		value = hint['value']
		initial_data = {'id': [], 'Productivity': []}
		for col in df:
			initial_data[col] = [0] * len(part_hints)
		if id_value not in df.index:
			new_row = pd.Series(name=id_value, dtype='object')
			new_row[column_name] = value
			df = pd.concat([df, new_row.to_frame().T])
	df = df.reset_index().rename(columns={'index': 'id'})
	D = pd.merge(robots[['id', 'Productivity']], df, on='id')
	D.fillna(0, inplace=True)
	new_df = pd.DataFrame()
	try:
			corr_S = D['Sonoreceptors'].corr(D['Productivity'])
			corr_ATC = D['AutoTerrain Tread Count'].corr(D['Productivity'])
			corr_IS = D['InfoCore Size'].corr(D['Productivity'])
			corr_ABL = D['Astrogation Buffer Length'].corr(D['Productivity'])
			corr_PS = D['Polarity Sinks'].corr(D['Productivity'])
			corr_NM = pd.to_numeric(D['Nanochip Model'], errors='coerce').corr(D['Productivity'])
			corr_APM = pd.to_numeric(D['Axial Piston Model'], errors='coerce').corr(D['Productivity'])
			corr_CUB = D['Cranial Uplink Bandwidth'].corr(D['Productivity'])
			corr_AVM = pd.to_numeric(D['Arakyd Vocabulator Model'], errors='coerce').corr(D['Productivity'])
			corr_RMHP = D['Repulsorlift Motor HP'].corr(D['Productivity'])

			correlation_dict = {
				'Sonoreceptors': corr_S,
				'AutoTerrain Tread Count': corr_ATC,
				'InfoCore Size': corr_IS,
				'Astrogation Buffer Length': corr_ABL,
				'Polarity Sinks': corr_PS,
				'Nanochip Model': corr_NM,
				'Axial Piston Model': corr_APM,
				'Cranial Uplink Bandwidth': corr_CUB,
				'Arakyd Vocabulator Model': corr_AVM,
				'Repulsorlift Motor HP': corr_RMHP
			}

			sorted_corr_columns = sorted(correlation_dict, key=correlation_dict.get, reverse=True)
			max_1_column, max_2_column = sorted_corr_columns[0], sorted_corr_columns[1] if len(sorted_corr_columns) >= 2 else ()
			new_df = D[['id', 'Productivity', max_1_column, max_2_column]]
			new_df = new_df.sort_values(by=['Productivity'], ascending=False) 
			productivity_table.write(new_df)   

	except:
		new_df = pd.DataFrame(data=["Not Enough Data"], columns=[""])
		productivity_table.write(new_df) 

	# sleep 6 seconds
	for t in np.arange(0,6):
		status.write("Time now: " + str(timenow) + ", Seconds to next hack: " + str(6-t))
		time.sleep(1)