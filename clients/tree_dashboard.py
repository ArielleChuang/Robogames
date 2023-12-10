from pyecharts import options as opts
from pyecharts.charts import Tree
import streamlit as st
import pandas as pd
import Robogame as rg
from streamlit_echarts import st_echarts
import numpy as np
import copy
import time, json


# Main content
st.set_page_config(page_title="Robogame", layout="wide")
st.title('Family Tree')

# let's create two "spots" in the streamlit view for our charts
status = st.empty()
st.write("⚫️ Grey: Unassigned 🟢 Green: Positive Productivity 🔴 Red: Negative Productivity")
viz = st.empty()

# create the game, and mark it as ready
game = rg.Robogame("bob")  # our team's secret
game.setReady()

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
     
# Function to check if a node or its children match the search text
def is_node_matching_search(node, search_text):
    node_name = str(node['id']).lower()
    search_text_lower = search_text.lower()

    if search_text_lower in node_name:
        return True

    if 'children' in node:
        for child in node['children']:
            if is_node_matching_search(child, search_text):
                return True

    return False

family = game.getTree()
robots = game.getRobotInfo()

if "iteration" not in st.session_state:
    st.session_state["iteration"] = 0

# Extracting robot productivity information
robot_productivity = {}
for index, row in robots.iterrows():
    robot_id = row['id']
    productivity = row['Productivity']
    if not pd.isnull(robot_id) and not pd.isnull(productivity):
        robot_productivity[robot_id] = productivity

def assign_item_style(node, robot_productivity):
    node_id = node['id']
    productivity = robot_productivity.get(node_id, np.nan)

    # Assign itemStyle based on productivity values
    if np.isnan(productivity):
        node['itemStyle'] = {"color": 'grey'}  # Grey for NA values
    elif productivity > 0:
        node['itemStyle'] = {"color": 'green'}  # Green for positive values
    else:
        node['itemStyle'] = {"color": 'red'}  # Red for negative values

    # Recursively assign itemStyle to children
    if 'children' in node:
        for child in node['children']:
            assign_item_style(child, robot_productivity)

# Create a copy of the family tree to avoid modifying the original structure
family_copy = copy.deepcopy(family)

# Assign itemStyle to each node in the copy
assign_item_style(family_copy, robot_productivity)

def convert_to_echarts_format(node):
    echarts_node = {"name": str(node['id']),
                    "itemStyle": node.get("itemStyle", {})}
    
    if 'children' in node:
        echarts_node["children"] = [convert_to_echarts_format(child) for child in node['children']]
    
    return echarts_node

# Convert the modified family tree copy to ECharts format
echarts_data = convert_to_echarts_format(family_copy)

opts = {
    "tooltip": {"trigger": "item", "triggerOn": "mousemove"},
    "series": [
        {
            "type": "tree",
            "data": [echarts_data],
            "top": "1%",
            "left": "7%",
            "bottom": "1%",
            "right": "20%",
            "symbolSize": 10,
            "label": {
                "position": "left",
                "verticalAlign": "middle",
                "align": "right",
                "fontSize": 16,
            },
            "leaves": {
                "label": {
                    "position": "right",
                    "verticalAlign": "middle",
                    "align": "left",
                }
            },
            "expandAndCollapse": False,
            "animationDuration": 550,
            "animationDurationUpdate": 750,
        }
    ],
}

while st.session_state["iteration"] < 101:
    # st.markdown(f"Iteration number {st.session_state['iteration']}")

    with viz:
        st_echarts(opts, height="1200px", key="chart")

    for t in np.arange(0,6):
        status.write("Seconds to next hack: " + str(6-t))
        time.sleep(1)

    st.session_state["iteration"] += 1

    if st.session_state["iteration"] < 101:
        st.experimental_rerun()