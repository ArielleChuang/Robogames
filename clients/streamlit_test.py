import streamlit as st
import time, json
import numpy as np
import altair as alt
import pandas as pd
import Robogame as rg

# Main content
st.set_page_config(page_title="Robogame", layout="wide")
st.title('Robogame Dashboard')

# let's create two "spots" in the streamlit view for our charts
status = st.empty()
#predVis = st.empty()
#partVis = st.empty()

# Sidebar on the left
side = st.sidebar
with side:
	st.header('Streaming Data')
	# st.sidebar.write("test!")
	robotID = st.text_input('Robot ID')
	# st.button('Bid', type='primary')
	if robotID:
		st.write("You entered: ", robotID)

# create the game, and mark it as ready
game = rg.Robogame("bob")
game.setReady()

# grid layout
col1, col2, col3 = st.columns([2, 2, 1])
with col1:
	
	container1 = st.container()
	container2 = st.container()	

	with container1:
		st.subheader("Viz 1")
		viz1 = st.empty()

	with container2:
		st.subheader("Viz 2")
		viz2 = st.empty()

with col2:
	
	container3 = st.container()
	container4 = st.container()	

	with container3:
		st.subheader("Number Generator")
		viz3 = st.empty()

	with container4:
		st.subheader("Viz 4")
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
	# sleep 6 seconds
	for t in np.arange(0,6):
		status.write("Seconds to next hack: " + str(6-t))
		time.sleep(1)

	# update the hints
	game.getHints()

	# update robo info
	robots = game.getRobotInfo()
	team_counts = robots['winningTeam'].value_counts()
	team_counts = pd.DataFrame(team_counts)
	team_counts = team_counts.sort_values(by='count', ascending=False)
	team_table.write(team_counts)
	

	# create a dataframe for the time prediction hints
	df1 = pd.DataFrame(game.getAllPredictionHints())

	# if it's not empty, let's get going
	if (len(df1) > 0):
		# create a plot for the time predictions (ignore which robot it came from)
		c1 = alt.Chart(df1).mark_circle().encode(
			alt.X('time:Q',scale=alt.Scale(domain=(0, 100))),
			alt.Y('value:Q',scale=alt.Scale(domain=(0, 100)))
		)

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
		c3 = base3 + line

		# write it to the screen
		#predVis.write(c1)
		viz1.write(c1)
		viz3.write(c3)

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
		viz2.write(c2)
		viz4.write(c2)