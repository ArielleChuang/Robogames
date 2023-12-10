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

# Main content
st.set_page_config(page_title="Robogame", layout="wide")
st.title('Robogame Dashboard')

# let's create two "spots" in the streamlit view for our charts
status = st.empty()

# create the game, and mark it as ready
game = rg.Robogame("bob") # our team's secret
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


with col2:
	
	container3 = st.container()
	container4 = st.container()	

	with container3:
		st.subheader("Number Generator")
		viz3 = st.empty()

	with container4:
		st.subheader("Productivity Dataframe")
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
	
	## Friendship Network
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

	except:
			new_df = pd.DataFrame(data=["Not Enough Data"], columns=[""])


	## Robot Num Generator
# create a dataframe for the time prediction hints
	df1 = pd.DataFrame(game.getAllPredictionHints())

	# if it's not empty, let's get going
	if (len(df1) > 0):
		
		nearest = alt.selection_point(on='mouseover', fields=['time', 'value'])
		#selection = alt.selection_point(on='mouseover', fields=['time', 'value'])
		
		color = alt.condition(
			nearest,
			alt.Color('id:N').title("Robot ID").legend(orient="bottom"),
			alt.value('lightgray')
		)
		base3 = alt.Chart(df1).mark_circle().encode(
			alt.X('time:Q'),
			alt.Y('value:Q'),
			color=color
			#tooltip=['time', 'value', "id"]
		).add_params(
			nearest
		).properties(
			width=500, height=500
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

		num = alt.layer(base3, line, line2)#*polynomial_fit)
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
		viz4.write(new_df)


